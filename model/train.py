"""
AeroCrop.ai — Model Training Pipeline (Model Layer)

Trains MultiModalAeroCropNet using:
  - Disease images:  New Plant Diseases Dataset (Augmented) — 87,900 images, 38 classes
  - Yield tabular:   yield_df.csv — FAO yield + meteorological telemetry

Features & Optimizations:
  - Automatic Mixed Precision (AMP) for 2.5x speedup and reduced VRAM on NVIDIA GPUs
  - Robust dataset auto-discovery (handles single and double nested directories)
  - Huber / SmoothL1 loss for stable yield regression
  - Transfer learning enabled by default (ImageNet ResNet-18 backbone)
  - Safe interruption handling (preserves best model on Ctrl+C)
  - Saves best weights to model/aerocrop_weights.pth and latest checkpoint

Usage:
    python model/train.py --epochs 15 --batch_size 32
"""

from __future__ import annotations
import argparse
import csv
import os
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from model.architecture import MultiModalAeroCropNet
from model.dataset import (
    MultiModalDataset,
    PlantDiseaseDataset,
    TRAIN_TRANSFORM,
    VAL_TRANSFORM,
)


# ── Argument Parser ────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="Train AeroCrop.ai MultiModalAeroCropNet on GPU/CPU"
    )
    parser.add_argument(
        "--image_dir",
        type=str,
        default=r"data\New Plant Diseases Dataset(Augmented)\New Plant Diseases Dataset(Augmented)\train",
        help="Path to PlantVillage training image directory",
    )
    parser.add_argument(
        "--val_dir",
        type=str,
        default=r"data\New Plant Diseases Dataset(Augmented)\New Plant Diseases Dataset(Augmented)\valid",
        help="Path to PlantVillage validation image directory",
    )
    parser.add_argument(
        "--yield_csv",
        type=str,
        default=r"data\yield_df.csv",
        help="Path to yield_df.csv",
    )
    parser.add_argument("--epochs",       type=int,   default=15,
                        help="Number of training epochs")
    parser.add_argument("--batch_size",   type=int,   default=64,
                        help="Batch size (64 recommended for RTX 3050 6GB GPU)")
    parser.add_argument("--lr",           type=float, default=1e-4,
                        help="Peak learning rate for AdamW")
    parser.add_argument("--alpha",        type=float, default=1.0,
                        help="Weight for disease classification loss")
    parser.add_argument("--beta",         type=float, default=0.05,
                        help="Weight for yield regression loss")
    parser.add_argument("--workers",      type=int,   default=min(os.cpu_count() or 4, 4),
                        help="DataLoader num_workers (4 recommended for multi-worker async prefetch)")
    parser.add_argument("--no_pretrained", action="store_true",
                        help="Disable ImageNet pretraining (train from scratch)")
    parser.add_argument("--no_amp",       action="store_true",
                        help="Disable Automatic Mixed Precision (AMP)")
    parser.add_argument("--max_per_class", type=int,  default=None,
                        help="Limit images per class (for rapid validation runs)")
    parser.add_argument("--resume",       type=str,   default=None,
                        help="Path to checkpoint .pth to resume training from")
    parser.add_argument("--output_weights", type=str, default=None,
                        help="Path to save best weights (defaults to config.WEIGHTS_PATH)")
    return parser.parse_args()


# ── Path Resolution Helper ─────────────────────────────────────────────────
def resolve_dir(provided_path: str, fallback_subfolder: str) -> str:
    """Resolve directory checking absolute, relative, and standard candidate paths."""
    p = Path(provided_path)
    if p.is_absolute() and p.exists():
        return str(p)

    rel_base = Path(config.BASE_DIR) / provided_path
    if rel_base.exists():
        return str(rel_base)

    candidates = [
        Path(config.DATA_DIR) / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / fallback_subfolder,
        Path(config.DATA_DIR) / "New Plant Diseases Dataset(Augmented)" / fallback_subfolder,
        Path(config.DATA_DIR) / fallback_subfolder,
    ]
    for c in candidates:
        if c.exists() and any(c.iterdir()):
            return str(c)

    return str(rel_base)


def resolve_file(provided_path: str, fallback_filename: str) -> str:
    p = Path(provided_path)
    if p.is_absolute() and p.exists():
        return str(p)

    rel_base = Path(config.BASE_DIR) / provided_path
    if rel_base.exists():
        return str(rel_base)

    alt = Path(config.DATA_DIR) / fallback_filename
    if alt.exists():
        return str(alt)

    return str(rel_base)


def safe_torch_save(obj, target_path: str):
    """Safely saves PyTorch artifacts on Windows using an atomic temporary file replacement with retry."""
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.with_name(f"{target.stem}_tmp_{int(time.time() * 1000)}{target.suffix}")
    try:
        torch.save(obj, str(tmp_path))
    except Exception:
        torch.save(obj, str(target))
        return

    for _ in range(5):
        try:
            os.replace(str(tmp_path), str(target))
            return
        except (PermissionError, OSError):
            time.sleep(0.3)

    try:
        import shutil
        shutil.copy2(str(tmp_path), str(target))
        if tmp_path.exists():
            tmp_path.unlink()
    except Exception as e:
        print(f"  [Warning] Failed to replace {target}: {e}")


# ── Metrics Tracking ───────────────────────────────────────────────────────
class MetricsTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.total, self.correct, self.loss_sum = 0, 0, 0.0
        self.yield_mse_sum, self.n_batches = 0.0, 0

    def update(self, logits, labels, yield_pred, yield_true, loss):
        preds = logits.argmax(dim=1)
        self.correct     += (preds == labels).sum().item()
        self.total       += labels.size(0)
        self.loss_sum    += loss.item()
        self.n_batches   += 1
        if yield_pred is not None and yield_true is not None:
            mse = ((yield_pred - yield_true) ** 2).mean().item()
            self.yield_mse_sum += mse

    @property
    def accuracy(self):
        return 100.0 * self.correct / self.total if self.total else 0

    @property
    def avg_loss(self):
        return self.loss_sum / self.n_batches if self.n_batches else 0

    @property
    def avg_yield_rmse(self):
        if self.n_batches == 0 or self.yield_mse_sum == 0.0:
            return None
        mse = self.yield_mse_sum / self.n_batches
        return mse ** 0.5


# ── Training & Validation Loops ───────────────────────────────────────────
def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion_cls: nn.Module,
    criterion_reg: nn.Module,
    scaler: torch.amp.GradScaler | None,
    device: torch.device,
    alpha: float,
    beta: float,
    use_amp: bool,
    epoch: int = 1,
    total_epochs: int = 15,
) -> MetricsTracker:
    model.train()
    tracker = MetricsTracker()
    total_batches = len(loader)
    report_interval = max(1, min(50, total_batches // 5)) if total_batches > 10 else max(1, total_batches // 2)
    t_start = time.time()

    for step, batch in enumerate(loader, start=1):
        if len(batch) == 4:
            images, tabular, labels, yield_true = batch
            images     = images.to(device, non_blocking=True)
            tabular    = tabular.to(device, non_blocking=True)
            labels     = labels.to(device, non_blocking=True)
            yield_true = yield_true.to(device, non_blocking=True)
        else:
            images, labels = batch
            images     = images.to(device, non_blocking=True)
            tabular    = torch.zeros(images.size(0), config.TABULAR_INPUT_DIM, device=device)
            labels     = labels.to(device, non_blocking=True)
            yield_true = None

        optimizer.zero_grad(set_to_none=True)

        with torch.amp.autocast(device_type=device.type, enabled=(device.type == "cuda" and use_amp)):
            disease_logits, yield_pred = model(images, tabular)
            loss_cls = criterion_cls(disease_logits, labels)
            if yield_true is not None:
                loss_reg = criterion_reg(yield_pred, yield_true)
                loss = alpha * loss_cls + beta * loss_reg
            else:
                loss = loss_cls

        if scaler is not None and scaler.is_enabled():
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()

        tracker.update(disease_logits, labels, yield_pred, yield_true, loss)

        if step % report_interval == 0 or step == total_batches:
            elapsed = time.time() - t_start
            imgs_done = step * loader.batch_size
            speed = imgs_done / max(elapsed, 0.001)
            sys.stdout.write(
                f"\r    [Ep {epoch}/{total_epochs}] Batch {step:>4}/{total_batches} "
                f"| Loss: {tracker.avg_loss:.4f} | Acc: {tracker.accuracy:.1f}% "
                f"| Speed: {speed:.1f} img/s"
            )
            sys.stdout.flush()

    sys.stdout.write("\n")
    return tracker


@torch.no_grad()
def validate(
    model: nn.Module,
    loader: DataLoader,
    criterion_cls: nn.Module,
    criterion_reg: nn.Module,
    device: torch.device,
    alpha: float,
    beta: float,
    use_amp: bool,
) -> MetricsTracker:
    model.eval()
    tracker = MetricsTracker()

    for batch in loader:
        if len(batch) == 4:
            images, tabular, labels, yield_true = batch
            images     = images.to(device, non_blocking=True)
            tabular    = tabular.to(device, non_blocking=True)
            labels     = labels.to(device, non_blocking=True)
            yield_true = yield_true.to(device, non_blocking=True)
        else:
            images, labels = batch
            images     = images.to(device, non_blocking=True)
            tabular    = torch.zeros(images.size(0), config.TABULAR_INPUT_DIM, device=device)
            labels     = labels.to(device, non_blocking=True)
            yield_true = None

        with torch.amp.autocast(device_type=device.type, enabled=(device.type == "cuda" and use_amp)):
            disease_logits, yield_pred = model(images, tabular)
            loss_cls = criterion_cls(disease_logits, labels)
            if yield_true is not None:
                loss_reg = criterion_reg(yield_pred, yield_true)
                loss = alpha * loss_cls + beta * loss_reg
            else:
                loss = loss_cls

        tracker.update(disease_logits, labels, yield_pred, yield_true, loss)

    return tracker


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    args   = parse_args()
    device = torch.device(config.DEVICE)
    use_amp = (device.type == "cuda" and not args.no_amp)
    pretrained = not args.no_pretrained

    save_weights_path = resolve_file(args.output_weights, "aerocrop_weights.pth") if args.output_weights else config.WEIGHTS_PATH

    print("\n" + "=" * 68)
    print("  [AeroCrop.ai] High-Performance Neural Training Pipeline")
    print("=" * 68)
    print(f"  Device              : {device} ({torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'})")
    print(f"  Mixed Precision AMP : {'Enabled (FP16/FP32)' if use_amp else 'Disabled'}")
    print(f"  Epochs              : {args.epochs}")
    print(f"  Batch size          : {args.batch_size}")
    print(f"  Learning rate       : {args.lr}")
    print(f"  Target Weights File : {save_weights_path}")
    print(f"  Pretrained backbone : {pretrained}")
    print(f"  Loss balance        : alpha={args.alpha} (cls) + beta={args.beta} (SmoothL1 yield)")
    print("=" * 68 + "\n")

    # ── Hardware Acceleration Optimizations ──────────────────────────────
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass

    # ── Dataset Auto-Resolution ───────────────────────────────────────────
    img_train_abs = resolve_dir(args.image_dir, "train")
    img_val_abs   = resolve_dir(args.val_dir, "valid")
    yield_csv_abs = resolve_file(args.yield_csv, "yield_df.csv")

    if not os.path.exists(img_train_abs):
        print(f"[ERROR] Image training directory not found: {img_train_abs}")
        print("  Please ensure data directory is set up or run: python model/extract_data.py")
        sys.exit(1)

    use_multimodal = os.path.exists(yield_csv_abs)

    if use_multimodal:
        print("[Dataset] Mode: MultiModal (RGB Leaf + Tabular Agro-Meteorological Fusion)")
        print(f"  Train images: {img_train_abs}")
        print(f"  Val images  : {img_val_abs}")
        print(f"  Yield table : {yield_csv_abs}")
        train_dataset = MultiModalDataset(
            image_root=img_train_abs,
            yield_csv=yield_csv_abs,
            split="train",
            transform=TRAIN_TRANSFORM,
            max_per_class=args.max_per_class,
        )
        val_dataset = MultiModalDataset(
            image_root=img_val_abs,
            yield_csv=yield_csv_abs,
            split="val",
            transform=VAL_TRANSFORM,
            max_per_class=args.max_per_class,
        )
    else:
        print("[Dataset] Mode: Vision-Only (PlantDiseaseDataset)")
        print(f"  Train images: {img_train_abs}")
        train_dataset = PlantDiseaseDataset(
            img_train_abs, transform=TRAIN_TRANSFORM, max_per_class=args.max_per_class
        )
        val_dataset = PlantDiseaseDataset(
            img_val_abs, transform=VAL_TRANSFORM, max_per_class=args.max_per_class
        )

    # Multi-worker async prefetching to saturate GPU
    num_workers = max(0, args.workers)
    loader_kwargs = {
        "num_workers": num_workers,
        "pin_memory": (device.type == "cuda"),
    }
    if num_workers > 0:
        loader_kwargs["persistent_workers"] = True
        loader_kwargs["prefetch_factor"] = 2

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=True,  # Prevent BatchNorm1d error on odd leftover batch
        **loader_kwargs,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        drop_last=False,
        **loader_kwargs,
    )

    print(f"\n  Dataset Size  : {len(train_dataset):,} train samples, {len(val_dataset):,} val samples")
    print(f"  Batch Batches : {len(train_loader):,} steps per epoch (workers={num_workers})")

    # ── Model Initialization ───────────────────────────────────────────────
    model = MultiModalAeroCropNet(
        num_classes=config.NUM_DISEASE_CLASSES,
        tabular_input_dim=config.TABULAR_INPUT_DIM,
        pretrained=pretrained,
    ).to(device)

    # Resume from checkpoint if requested, or warm-start from baseline weights
    if args.resume and os.path.exists(args.resume):
        checkpoint = torch.load(args.resume, map_location=device, weights_only=True)
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        else:
            model.load_state_dict(checkpoint)
        print(f"\n  [Resume] Loaded model weights from {args.resume}")
    else:
        baseline_path = os.path.join(config.MODEL_DIR, "aerocrop_weights_baseline38.pth")
        if os.path.exists(baseline_path):
            try:
                old_state = torch.load(baseline_path, map_location=device, weights_only=True)
                if isinstance(old_state, dict) and "model_state_dict" in old_state:
                    old_state = old_state["model_state_dict"]
                new_state = model.state_dict()
                transferred = 0
                for k, v in old_state.items():
                    if k in new_state and new_state[k].shape == v.shape:
                        new_state[k] = v
                        transferred += 1
                    elif k == "disease_head.weight" and v.shape[0] <= new_state[k].shape[0]:
                        new_state[k][:v.shape[0]] = v
                        transferred += 1
                    elif k == "disease_head.bias" and v.shape[0] <= new_state[k].shape[0]:
                        new_state[k][:v.shape[0]] = v
                        transferred += 1
                model.load_state_dict(new_state)
                print(f"  [Warm-Start] Successfully transferred {transferred} layers from 38-class baseline model!")
            except Exception as e:
                print(f"  [Warm-Start] Could not warm-start ({e}); starting from ImageNet weights.")

    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Model Params  : {total_params:,} parameters")

    # ── Optimizer, Scheduler & Scaler ──────────────────────────────────────
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    criterion_cls = nn.CrossEntropyLoss(label_smoothing=0.1)
    criterion_reg = nn.SmoothL1Loss(beta=1.0)  # Robust Huber loss for yield

    # ── Metrics CSV Log ────────────────────────────────────────────────────
    output_stem = Path(save_weights_path).stem
    log_filename = f"training_log_{output_stem}.csv" if output_stem != "aerocrop_weights" else "training_log.csv"
    log_path = os.path.join(config.MODEL_DIR, log_filename)
    log_file = open(log_path, "w", newline="")
    log_writer = csv.writer(log_file)
    log_writer.writerow([
        "epoch", "train_loss", "train_acc", "train_yield_rmse",
        "val_loss", "val_acc", "val_yield_rmse", "lr", "elapsed_s"
    ])

    best_val_acc = 0.0
    t0 = time.time()

    print("\n" + "-" * 72)
    print(f"  {'Ep':>3} | {'TrLoss':>8} | {'TrAcc%':>7} | "
          f"{'VaLoss':>8} | {'VaAcc%':>7} | {'YldRMSE':>8} | {'LR':>9}")
    print("-" * 72)

    try:
        for epoch in range(1, args.epochs + 1):
            ep_start = time.time()

            tr = train_one_epoch(
                model=model,
                loader=train_loader,
                optimizer=optimizer,
                criterion_cls=criterion_cls,
                criterion_reg=criterion_reg,
                scaler=scaler,
                device=device,
                alpha=args.alpha,
                beta=args.beta,
                use_amp=use_amp,
                epoch=epoch,
                total_epochs=args.epochs,
            )
            va = validate(
                model=model,
                loader=val_loader,
                criterion_cls=criterion_cls,
                criterion_reg=criterion_reg,
                device=device,
                alpha=args.alpha,
                beta=args.beta,
                use_amp=use_amp,
            )
            scheduler.step()

            elapsed = time.time() - ep_start
            lr_now  = scheduler.get_last_lr()[0]

            rmse_str = f"{va.avg_yield_rmse:>7.4f}" if va.avg_yield_rmse is not None else "    N/A"
            print(f"  {epoch:>3} | {tr.avg_loss:>8.4f} | {tr.accuracy:>6.2f}% | "
                  f"{va.avg_loss:>8.4f} | {va.accuracy:>6.2f}% | "
                  f"{rmse_str} | {lr_now:>9.2e}")

            log_writer.writerow([
                epoch, round(tr.avg_loss, 5), round(tr.accuracy, 3),
                round(tr.avg_yield_rmse, 4) if tr.avg_yield_rmse is not None else "",
                round(va.avg_loss, 5), round(va.accuracy, 3),
                round(va.avg_yield_rmse, 4) if va.avg_yield_rmse is not None else "",
                f"{lr_now:.2e}", round(elapsed, 1),
            ])
            log_file.flush()

            # Save best checkpoint
            if va.accuracy > best_val_acc:
                best_val_acc = va.accuracy
                safe_torch_save(model.state_dict(), save_weights_path)
                print(f"         [BEST] New best val acc: {best_val_acc:.2f}% -> saved to {save_weights_path}")

            # Save latest checkpoint for resumption
            latest_path = os.path.join(config.MODEL_DIR, "checkpoint_latest.pth")
            safe_torch_save({
                "epoch": epoch,
                "best_val_acc": best_val_acc,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
            }, latest_path)

    except KeyboardInterrupt:
        print("\n\n  [Interrupted] Training interrupted by user. Preserving best weights...")
        if best_val_acc > 0 and not os.path.exists(save_weights_path):
            safe_torch_save(model.state_dict(), save_weights_path)
            print(f"  Saved best weights to {save_weights_path}")

    finally:
        total_time = time.time() - t0
        log_file.close()

    print("\n" + "=" * 68)
    print(f"  Training finished in {total_time/60:.1f} minutes")
    print(f"  Best Validation Accuracy : {best_val_acc:.2f}%")
    if os.path.exists(save_weights_path):
        print(f"  Model Weights saved to   : {save_weights_path}")
    print(f"  Metrics Log saved to     : {log_path}")
    print("=" * 68 + "\n")


if __name__ == "__main__":
    main()

