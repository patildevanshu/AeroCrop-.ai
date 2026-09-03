"""
AeroCrop.ai -- Model Training Pipeline (Model Layer)

Trains MultiModalAeroCropNet using:
  - Disease images:  New Plant Diseases Dataset (Augmented) -- 87,900 images, 38 classes
  - Yield tabular:   yield_df.csv -- FAO yield + weather data

Joint Loss:
    L_total = alpha  CrossEntropyLoss(disease) + beta  MSELoss(yield)
    Default: alpha = 1.0, beta = 0.5

Usage:
    python model/train.py \
        --image_dir   "data/New Plant Diseases Dataset(Augmented)/train" \
        --val_dir     "data/New Plant Diseases Dataset(Augmented)/valid" \
        --yield_csv   "data/yield_df.csv" \
        --epochs      30 \
        --batch_size  32 \
        --lr          1e-4

Output:
    model/aerocrop_weights.pth       -- best checkpoint (by val disease accuracy)
    model/training_log.csv           -- per-epoch metrics log
"""

import argparse
import csv
import os
import sys
import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from model.architecture import MultiModalAeroCropNet
from model.dataset import (
    MultiModalDataset,
    PlantDiseaseDataset,
    TRAIN_TRANSFORM,
    VAL_TRANSFORM,
)


# -- Argument Parser --------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Train AeroCrop.ai MultiModalAeroCropNet"
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
    parser.add_argument("--epochs",     type=int,   default=30)
    parser.add_argument("--batch_size", type=int,   default=32)
    parser.add_argument("--lr",         type=float, default=1e-4)
    parser.add_argument("--alpha",      type=float, default=1.0,
                        help="Weight for disease classification loss")
    parser.add_argument("--beta",       type=float, default=0.05,
                        help="Balanced weight for yield regression loss (MSE scale)")
    parser.add_argument("--workers",    type=int,   default=4,
                        help="DataLoader num_workers (set 0 on Windows if errors)")
    parser.add_argument("--pretrained", action="store_true",
                        help="Use ImageNet pretrained ResNet-18 backbone")
    parser.add_argument("--max_per_class", type=int, default=None,
                        help="Limit images per class (for quick experiments)")
    parser.add_argument("--resume", type=str, default=None,
                        help="Path to checkpoint .pth to resume training from (e.g. model/aerocrop_weights.pth)")
    return parser.parse_args()


# -- Metrics Tracking -------------------------------------------------------
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
            return None  # No yield data available (disease-only training)
        mse = self.yield_mse_sum / self.n_batches
        return mse ** 0.5


# -- Training Loop ---------------------------------------------------------
def train_one_epoch(model, loader, optimizer, criterion_cls, criterion_reg,
                    device, alpha, beta):
    model.train()
    tracker = MetricsTracker()

    for batch in loader:
        if len(batch) == 4:
            images, tabular, labels, yield_true = batch
            images     = images.to(device)
            tabular    = tabular.to(device)
            labels     = labels.to(device)
            yield_true = yield_true.to(device)
        else:
            images, labels = batch
            tabular    = torch.zeros(images.size(0), config.TABULAR_INPUT_DIM).to(device)
            labels     = labels.to(device)
            yield_true = None

        optimizer.zero_grad()
        disease_logits, yield_pred = model(images, tabular)

        loss_cls = criterion_cls(disease_logits, labels)
        if yield_true is not None:
            loss_reg = criterion_reg(yield_pred, yield_true)
            loss = alpha * loss_cls + beta * loss_reg
        else:
            loss = loss_cls

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
        optimizer.step()

        tracker.update(disease_logits, labels, yield_pred, yield_true, loss)

    return tracker


@torch.no_grad()
def validate(model, loader, criterion_cls, criterion_reg, device, alpha, beta):
    model.eval()
    tracker = MetricsTracker()

    for batch in loader:
        if len(batch) == 4:
            images, tabular, labels, yield_true = batch
            images     = images.to(device)
            tabular    = tabular.to(device)
            labels     = labels.to(device)
            yield_true = yield_true.to(device)
        else:
            images, labels = batch
            tabular    = torch.zeros(images.size(0), config.TABULAR_INPUT_DIM).to(device)
            labels     = labels.to(device)
            yield_true = None

        disease_logits, yield_pred = model(images, tabular)
        loss_cls = criterion_cls(disease_logits, labels)
        if yield_true is not None:
            loss_reg = criterion_reg(yield_pred, yield_true)
            loss = alpha * loss_cls + beta * loss_reg
        else:
            loss = loss_cls

        tracker.update(disease_logits, labels, yield_pred, yield_true, loss)

    return tracker


# -- Main -------------------------------------------------------------------
def main():
    args   = parse_args()
    device = torch.device(config.DEVICE)

    print("\n" + "=" * 65)
    print("  AeroCrop.ai -- Model Training")
    print("=" * 65)
    print(f"  Device      : {device}")
    print(f"  Epochs      : {args.epochs}")
    print(f"  Batch size  : {args.batch_size}")
    print(f"  LR          : {args.lr}")
    print(f"  alpha (cls) : {args.alpha}   beta (reg) : {args.beta}")
    print(f"  Pretrained  : {args.pretrained}")
    print("=" * 65 + "\n")

    # -- Dataset Setup ----------------------------------------------------
    yield_csv_abs = os.path.join(config.BASE_DIR, args.yield_csv)
    img_train_abs = os.path.join(config.BASE_DIR, args.image_dir)
    img_val_abs   = os.path.join(config.BASE_DIR, args.val_dir)

    use_multimodal = (
        os.path.exists(yield_csv_abs) and os.path.exists(img_train_abs)
    )

    if use_multimodal:
        print("[Dataset] Using MultiModalDataset (image + tabular joint training)")
        train_dataset = MultiModalDataset(
            image_root=img_train_abs,
            yield_csv=yield_csv_abs,
            split="train",
            transform=TRAIN_TRANSFORM,
        )
        val_dataset = MultiModalDataset(
            image_root=img_val_abs,
            yield_csv=yield_csv_abs,
            split="val",
            transform=VAL_TRANSFORM,
        )
    elif os.path.exists(img_train_abs):
        print("[Dataset] Using PlantDiseaseDataset only (no yield CSV found)")
        train_dataset = PlantDiseaseDataset(
            img_train_abs, transform=TRAIN_TRANSFORM,
            max_per_class=args.max_per_class
        )
        val_dataset = PlantDiseaseDataset(
            img_val_abs, transform=VAL_TRANSFORM,
            max_per_class=args.max_per_class
        )
    else:
        print(f"[ERROR] Image directory not found: {img_train_abs}")
        print("  Please extract the dataset zip to the 'data/' folder first.")
        print("  Run: python model/extract_data.py")
        sys.exit(1)

    # Windows-safe num_workers
    num_workers = args.workers if sys.platform != "win32" else min(args.workers, 0)

    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size,
        shuffle=True, num_workers=num_workers,
        pin_memory=(device.type == "cuda"),
    )
    val_loader = DataLoader(
        val_dataset, batch_size=args.batch_size,
        shuffle=False, num_workers=num_workers,
        pin_memory=(device.type == "cuda"),
    )

    print(f"\n  Train samples : {len(train_dataset):,}")
    print(f"  Val   samples : {len(val_dataset):,}")
    print(f"  Train batches : {len(train_loader):,}")

    # -- Model ------------------------------------------------------------
    model = MultiModalAeroCropNet(
        num_classes=config.NUM_DISEASE_CLASSES,
        tabular_input_dim=config.TABULAR_INPUT_DIM,
        pretrained=args.pretrained,
    ).to(device)

    # ── Resume from checkpoint ────────────────────────────────────────────
    resume_path = args.resume or (config.WEIGHTS_PATH if args.pretrained else None)
    if args.resume and os.path.exists(args.resume):
        state = torch.load(args.resume, map_location=device, weights_only=True)
        model.load_state_dict(state)
        print(f"\n  [Resume] Loaded checkpoint from: {args.resume}")
    elif args.resume:
        print(f"\n  [Resume] WARNING: checkpoint not found at {args.resume} — starting from scratch.")

    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n  Model params  : {total_params:,}")

    # -- Optimizer & Scheduler --------------------------------------------
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.lr, weight_decay=1e-4
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=1e-6
    )

    criterion_cls = nn.CrossEntropyLoss(label_smoothing=0.1)
    criterion_reg = nn.MSELoss()

    # -- CSV Log ----------------------------------------------------------
    log_path = os.path.join(config.MODEL_DIR, "training_log.csv")
    log_file = open(log_path, "w", newline="")
    log_writer = csv.writer(log_file)
    log_writer.writerow([
        "epoch", "train_loss", "train_acc", "train_yield_rmse",
        "val_loss", "val_acc", "val_yield_rmse", "lr", "elapsed_s"
    ])

    best_val_acc = 0.0
    t0 = time.time()

    print("\n" + "-" * 65)
    print(f"  {'Ep':>3} | {'TrLoss':>8} | {'TrAcc%':>7} | "
          f"{'VaLoss':>8} | {'VaAcc%':>7} | {'YldRMSE':>8} | {'LR':>9}")
    print("-" * 65)

    for epoch in range(1, args.epochs + 1):
        ep_start = time.time()

        tr = train_one_epoch(
            model, train_loader, optimizer,
            criterion_cls, criterion_reg, device, args.alpha, args.beta
        )
        va = validate(
            model, val_loader,
            criterion_cls, criterion_reg, device, args.alpha, args.beta
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
            torch.save(model.state_dict(), config.WEIGHTS_PATH)
            print(f"         [BEST] New best val acc: {best_val_acc:.2f}% -- saved to {config.WEIGHTS_PATH}")

    total_time = time.time() - t0
    log_file.close()

    print("\n" + "=" * 65)
    print(f"  Training complete in {total_time/60:.1f} min")
    print(f"  Best val accuracy : {best_val_acc:.2f}%")
    print(f"  Weights saved to  : {config.WEIGHTS_PATH}")
    print(f"  Log saved to      : {log_path}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
