# AeroCrop.ai — Project Architecture, Resume Profile & Synopsis References

> **Project Title**: *Multimodal Deep Learning Architecture for Cash Crop Disease Diagnostics and Yield Forecasting*  
> **Authors**: Devanshu Patil, Yash Bhutada, Smit Patil  
> **Guide**: Mrs. Padmavati Sarode  
> **Institution**: Department of Computer Engineering, G H Raisoni College of Engineering and Management, Wagholi, Pune, India  
> **Verification Base**: Source code, training logs (`training_log.csv`), weights (`aerocrop_weights.pth`), dataset specifications, and official project synopsis (`Synopsis__1_ (3) (1).pdf`).

---

## 1. Resume Project Section (ATS-Optimized & Defensible)

### **AeroCrop.ai — Multimodal Crop Disease Diagnostics & Yield Forecasting Platform**
**Technologies:** PyTorch 2.5 · ResNet-18 · CUDA AMP (FP16) · FastAPI · React 18 · TypeScript · Vite · MongoDB · Open-Meteo REST API · Docker

- **System Purpose & Problem Solved**: Engineered a unified multimodal multi-task deep learning platform for smallholder cash-crop farmers in Maharashtra, simultaneously diagnosing **134 disease and disorder classes across 11 field crops** (166,630 images) and forecasting harvest yield in tons/hectare and quintals/acre from a single leaf photograph and microclimatic weather telemetry with zero soil-testing barriers.
- **Novel Neural Architecture**: Designed and implemented **MultiModalAeroCropNet** (11.29M parameters), coupling a pretrained ResNet-18 visual encoder (512-dim) with a 3-layer MLP tabular encoder (64-dim) via intermediate feature concatenation (576-dim) and projection into a shared 128-dim latent manifold driving dual task heads (134-class Softmax classification and Softplus non-negative yield regression).
- **Optimization & Verified Results**: Optimized end-to-end on an NVIDIA RTX 3050 6GB GPU across **80 epochs** using a composite multi-task objective (label-smoothed Cross-Entropy $\epsilon = 0.1$ and Smooth L1 regression $\beta = 1.0$), achieving **95.27\% validation accuracy**, **92.77\% macro precision**, **91.73\% macro F1-score**, and **8.30 t/ha yield RMSE** (MAE 3.39 t/ha) with a compact 45.1 MB memory footprint.
- **Production Services & Agronomic Logic**: Built an asynchronous FastAPI ASGI backend with a GPU singleton inference engine (<15ms forward pass), Open-Meteo real-time weather caching across 36 districts, an automated foliar spray safety decision engine (wash-off $>1$ mm and drift $>15$ km/h hazards), APMC mandi price forecasting, vernacular voice narration (`mr-IN`, `hi-IN`, `en-IN`), and PMFBY insurance claim PDF generation.

---

## 2. Verified Research Paper References (Exactly 15 from Synopsis)

The project synopsis (`Synopsis__1_ (3) (1).pdf`, Section 2 & References) strictly lists the following 15 peer-reviewed publications across two core domains:

### Part A: Multimodal Methods for Crop Disease Diagnosis (References [1]–[8])

| Ref # | Full Formal Citation | Core Contribution & Focus | How AeroCrop.ai Builds Upon It |
|:---:|:---|:---|:---|
| **[1]** | **S. P. Mohanty, D. P. Hughes, and M. Salathé**, "Using deep learning for image-based plant disease detection," *Frontiers in Plant Science*, vol. 7, p. 1419, 2016. | Foundational PlantVillage benchmark; 54,306 laboratory images, 38 classes across 14 crops using AlexNet/GoogLeNet. | Serves as the visual classification baseline. AeroCrop.ai scales from 38 lab classes to 134 field classes across 11 crops and incorporates weather telemetry. |
| **[2]** | **A. Dolatabadian, P. E. Bayer, L. Schultz-Leisner, and J. Batley**, "Image-based crop disease detection using machine learning," *Plant Pathology*, 2025. | Comprehensive review of machine learning pipelines for in-field crop imagery under natural lighting, occlusion, and background noise. | Motivates the integration of environmental telemetry to disambiguate field visual noise and variable canopy lighting. |
| **[3]** | **W. Zhang, H. Liu, W. Wu, L. Zhan, and J. Wei**, "A deep learning-based crop disease diagnosis method using multimodal mixup augmentation," *Applied Sciences*, vol. 14, no. 10, p. 4322, 2024. | Multimodal mixup augmentation strategy synthetically blending leaf images with meteorological records during optimization. | Informed our stochastic tabular weather pairing within `MultiModalDataset` during training epochs. |
| **[4]** | **A. Almadhor, H. T. Rauf, M. I. U. Lali, R. Damasevicius, A. Alahmer, and A. Mahmood**, "A hybrid deep learning model for tomato leaf disease detection and classification," *Sensors*, vol. 22, no. 10, p. 3721, 2023. | Sequential hybrid deep learning architecture extracting multi-stage feature hierarchies for tomato foliar diseases. | Confirmed that multi-stage intermediate representations outperform shallow single-branch classifiers. |
| **[5]** | **H. Zhu, B. Zhang, X. Zhao, Z. Li, and Y. Peng**, "Interpretable deep multimodal-based tomato disease diagnosis and severity estimation," *Frontiers in Plant Science*, vol. 16, p. 1534810, 2025. | Climate-aware disease severity estimation coupled with explainability modules for transparent agronomic guidance. | Influenced AeroCrop.ai's dynamic disease severity triage (`None`, `Low`, `Moderate`, `High`, `Critical`). |
| **[6]** | **B. Khan, M. S. Farooq, S. Abbas, M. A. Khan, and S. S. U. Rizvi**, "Bayesian optimized multimodal deep hybrid learning approach for tomato leaf disease classification," *Scientific Reports*, vol. 14, no. 1, p. 21525, 2024. | Bayesian hyperparameter optimization applied to hybrid image-and-metadata deep models for parameter efficiency. | Informed our compact bottleneck dimensioning (128-dim shared latent embedding) to prevent parameter bloat. |
| **[7]** | **K. P. Ferentinos**, "Deep learning models for plant disease detection and diagnosis," *Computers and Electronics in Agriculture*, vol. 145, pp. 311–318, 2018. | Extensive evaluation of CNN architectures (VGG, ResNet, AlexNet) across 58 disease categories, setting performance ceilings. | Justified selecting ResNet with residual skip connections over deeper VGG backbones for stable backpropagation. |
| **[8]** | **S. Mukherjee, D. K. Bhatt, P. Misra, and A. Mishra**, "Hybrid multimodal learning framework for crop disease detection, adaptive treatment, and price forecasting," *Frontiers in Computer Science*, vol. 8, p. 1560547, 2026. | Edge AIoT hardware pipeline deploying multimodal disease detection with adaptive treatments and price forecasting. | Directly supports AeroCrop.ai's end-to-end operational vision: combining neural diagnosis with chemical/organic treatments and APMC mandi rates. |

---

### Part B: Multimodal Methods for Crop Classification and Yield Prediction (References [9]–[15])

| Ref # | Full Formal Citation | Core Contribution & Focus | How AeroCrop.ai Builds Upon It |
|:---:|:---|:---|:---|
| **[9]** | **K. Sivasubramanian et al.**, "Attention-based multi-modal deep learning model of spatio-temporal crop yield prediction with satellite, soil and climate data," 2026. | Attention-based meta-transformer integrating multi-temporal satellite imagery, soil data, and climate time-series. | Validates the dependence of crop yield on ambient temperature, humidity, and rainfall vectors. |
| **[10]** | **G. Tseng, H. Kerner, and D. Rolnick**, "Annual and permanent crop mapping from multispectral and multitemporal satellite data using deep learning," *Frontiers in Plant Science*, vol. 14, p. 1011780, 2023. | Convolutional architectures for annual and permanent crop classification from multispectral satellite observations. | Establishes the regional agronomic taxonomy for distinguishing diverse cash crops across heterogeneous landscapes. |
| **[11]** | **K. K. Gadiraju and R. R. Vatsavai**, "Multimodal deep learning based crop classification using multi-spectral and multitemporal satellite imagery," in *Proc. 26th ACM SIGKDD*, 2020, pp. 3234–3242. | Benchmark framework for multimodal satellite data fusion applied to agricultural crop classification at scale. | Highlights multimodal data integration principles in agricultural deep learning. |
| **[12]** | **P. Nevavuori, N. Narra, and T. Lipping**, "Crop yield prediction with deep convolutional neural networks," *Computers and Electronics in Agriculture*, vol. 163, p. 104859, 2019. | First major study applying deep 2D CNNs directly to RGB and NDVI UAV imagery for within-season crop yield regression. | Proves that visual spatial features possess direct predictive power for crop yield modeling. |
| **[13]** | **A. Feng, J. Zhou, E. D. Vories, and K. A. Sudduth**, "Prediction of cotton yield based on soil texture, weather conditions and UAV imagery using deep learning," *Precision Agriculture*, vol. 25, no. 1, pp. 303–326, 2024. | Multimodal fusion of soil electrical conductivity, historical weather, and UAV imagery for spatial cotton yield forecasting. | Directly corroborates fusing weather features with visual imagery for cash crop yield estimation. |
| **[14]** | **Z. Li, J. Yan, Z. Chen, J. Wang, R. Zhou, and Y. Hu**, "Multimodal deep learning models in precision agriculture: Cotton yield prediction based on unmanned aerial vehicle imagery and meteorological data," *Agriculture*, vol. 15, no. 5, p. 1217, 2025. | Multi-sensor integration combining drone multispectral sensors with local ground weather stations for pre-harvest cotton yield. | Eliminates expensive drone hardware requirements by substituting low-cost smartphone leaf photos + automated Open-Meteo GPS weather. |
| **[15]** | **J. Cao, Z. Zhang, Y. Luo, L. Zhang, J. Zhang, Z. Li, and F. Tao**, "Wheat yield predictions at a county and field scale with deep learning, machine learning, and google earth engine," *European Journal of Agronomy*, vol. 123, p. 126204, 2021. | Deep learning and machine learning fusion with Google Earth Engine climate variables for field and county wheat yield forecasting. | Guides feature normalization and regression loss parameterization for wide-range crop yields. |

---

## 3. Realistic and Innovative System Architecture

The following diagram illustrates the multi-tier system topology implemented in AeroCrop.ai:

```
====================================================================================================
                                      AEROCROP.AI SYSTEM ARCHITECTURE
====================================================================================================

  [ 1. CLIENT / PRESENTATION TIER ] (React 18 + TypeScript + Vite + Tailwind CSS)
  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
  │  • Leaf Photo Camera Upload & Gallery Selector (Client-side Canvas Image Compression)        │
  │  • Maharashtra 36 Districts Dropdown (Automatic Centroid Coordinate Mapping)                 │
  │  • Multi-Plot Cadastral Management (Land Area in Acres, Sowing Date, Crop Species)           │
  │  • Multilingual Vernacular Voice Narration (Web Speech API: mr-IN Marathi, hi-IN, en-IN)     │
  │  • Farmer Analysis Card: Pathology Badge, Confidence Bar, Severity Meter, Yield (q/acre)   │
  │  • PMFBY Crop Loss Proof PDF Export (Surveyor Sign Blocks) & 1-Click WhatsApp Sharing        │
  └──────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                 │ HTTP/REST (Multipart Form-Data & JSON)
                                                 ▼
  [ 2. ASYNCHRONOUS API GATEWAY TIER ] (FastAPI + ASGI Uvicorn + Pydantic V2)
  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
  │  • POST /api/predict          : Multipart image upload + crop + district orchestrator        │
  │  • GET  /api/weather/{dist}   : Real-time meteorological telemetry & spray window hazard     │
  │  • GET  /api/mandi/{dist}/{c} : District APMC commodity modal prices & MSP calculations      │
  │  • POST /api/auth/register    : Farmer secure registration (bcrypt password hashing)         │
  │  • POST /api/auth/login       : Authentication issuing HTTP-only secure JWT token            │
  │  • GET  /api/plots            : Multi-plot farm registry and historical diagnosis timeline  │
  └──────────────────┬───────────────────────────┬───────────────────────────────┬───────────────┘
                     │ Dependency Injection      │ Internal Call                 │ Database Call
                     ▼                           ▼                               ▼
  [ 3. AGRONOMIC DOMAIN SERVICES ]    [ 4. WEATHER & MARKET ]          [ 5. PERSISTENCE LAYER ]
  ┌──────────────────────────────┐    ┌───────────────────────────┐    ┌─────────────────────────┐
  │ DiseaseService (134 Classes) │    │ WeatherService            │    │ MongoDB (Async Motor)   │
  │ • Chemical active ingredients│    │ • Open-Meteo REST Client  │    │ • users collection     │
  │ • Dilution dosages (g or mL) │    │ • 36 Maharashtra centroids│    │ • farm_plots collection │
  │ • Organic bio-remedies       │    │ • In-memory 30-min cache  │    │ • analyses collection   │
  │ • Treatment cost/acre (₹)   │    ├───────────────────────────┤    ├─────────────────────────┤
  ├──────────────────────────────┤    │ SpraySafetyEngine         │    │ File System Storage     │
  │ MandiService                 │    │ • Rain > 1.0mm: Wash-off  │    │ • uploads/ (user photos)│
  │ • APMC mandi modal rates     │    │ • Wind > 15km/h: Drift    │    │ • aerocrop_weights.pth  │
  │ • GoI MSP support benchmark  │    │ • Temp > 36°C: Scorch     │    │ • classes.json (134 cls)│
  │ • Gross Revenue projection   │    │ • Badges: Safe/Warn/Danger│    │ • training_log.csv      │
  └──────────────┬───────────────┘    └─────────────┬─────────────┘    └─────────────────────────┘
                 │                                  │
                 └────────────────┬─────────────────┘
                                  │ Preprocessed Tensors: Image [1,3,224,224] & Telemetry [1,3]
                                  ▼
  [ 6. CORE NEURAL INFERENCE ENGINE: MultiModalAeroCropNet ] (PyTorch 2.5 + CUDA AMP FP16)
  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
  │                                                                                              │
  │   [ Visual Encoding Pathway ]                         [ Tabular Encoding Pathway ]           │
  │   Input Image: X_v ∈ R^(3 x 224 x 224)                Input Telemetry: x_t = [T, H, P] ∈ R^3 │
  │          │                                                   │                               │
  │          ▼                                                   ▼                               │
  │   ResNet-18 Feature Backbone                          Z-Score Normalization                  │
  │   (ImageNet Pretrained, 11.18M params)                (μ = [28, 65, 5], σ = [8, 20, 10])     │
  │   Conv1 -> ResBlock1-4 -> AdaptiveAvgPool                    │                               │
  │          │                                                   ▼                               │
  │          ▼                                            3-Layer MLP Tabular Encoder            │
  │   Visual Vector v ∈ R^512                             [Linear(3,64) -> BN -> ReLU -> D(0.2)] │
  │          │                                            [Linear(64,64)-> BN -> ReLU -> D(0.2)] │
  │          │                                            [Linear(64,64)-> ReLU]                 │
  │          │                                                   │                               │
  │          │                                                   ▼                               │
  │          │                                            Tabular Vector t ∈ R^64                │
  │          └──────────────────────────┬────────────────────────┘                               │
  │                                     │ Intermediate Feature Concatenation                     │
  │                                     ▼                                                        │
  │                         Joint Representation f = [v; t] ∈ R^576                              │
  │                                     │                                                        │
  │                                     ▼                                                        │
  │                             Fusion Projection Layer                                          │
  │                 Linear(576, 128) -> BatchNorm1d -> ReLU -> Dropout(0.3)                      │
  │                                     │                                                        │
  │                                     ▼                                                        │
  │                      Shared Latent Embedding z ∈ R^128                                       │
  │                                     │                                                        │
  │                    ┌────────────────┴────────────────┐                                       │
  │                    ▼                                 ▼                                       │
  │         [ Disease Classification Head ]     [ Yield Regression Head ]                        │
  │         Linear(128, 134) -> Softmax         Linear(128, 32) -> ReLU                          │
  │                    │                        Linear(32, 1) -> Softplus(β=1.0)                 │
  │                    ▼                                         │                               │
  │         Pathology Logits (134 Classes)                       ▼                               │
  │         Top-1 Diagnosis + Calibrated Conf          Predicted Yield y_r ∈ R^+ (t/ha)          │
  │                                                    Converted to Quintal / Acre               │
  └──────────────────────────────────────────────────────────────────────────────────────────────┘
====================================================================================================
```

---

## 4. Key Architectural Innovations & Technical Highlights

1. **Intermediate Latent Fusion vs. Early/Late Fusion**:
   - *Why not early fusion?* Concatenating raw pixel matrices ($3 \times 224 \times 224 = 150,528$ values) with 3 scalar telemetry numbers creates extreme dimensional asymmetry, causing backpropagation to completely drown out the meteorological gradient.
   - *Why not late fusion?* Separate models making isolated predictions prevent cross-modal synergy (e.g., ambient relative humidity directly influences whether a foliar lesion is fungal or physiological).
   - *The AeroCrop.ai Solution*: Unimodal encoders independently project imagery into a high-level 512-dim visual vector and weather into a 64-dim tabular vector, fusing them into a unified 128-dim shared manifold.

2. **Multi-Task Objective Balancing**:
   $$\mathcal{L}_{\text{total}} = 1.0 \cdot \mathcal{L}_{\text{CrossEntropy}}(\epsilon = 0.1) + 0.20 \cdot \mathcal{L}_{\text{SmoothL1}}(\beta = 1.0)$$
   Label smoothing regularizes the vision head against memorizing laboratory backgrounds, while Smooth L1 prevents extreme harvest outliers from destabilizing joint representation weights.

3. **Singleton Inference Service with Zero-Latency Cold Start**:
   `InferenceService` loads the PyTorch state dict once upon FastAPI application startup (`@asynccontextmanager`). Model forward passes execute in $<15$ ms on an RTX 3050 GPU, scaling to high concurrent requests without GPU memory thrashing.

4. **Zero Soil-Testing Operational Barrier**:
   Eliminates the major adoption failure of computational agriculture in developing nations (requiring laboratory Soil Health Cards for N-P-K). AeroCrop.ai automatically derives weather vectors from GPS district coordinates, allowing rural farmers to receive instantaneous diagnoses simply by taking a smartphone photo.

---

## 5. Verification Checklist & Confirmed Project Metrics

| Parameter | Verified Source Code Value | Verification Location |
|:---|:---:|:---|
| Total Curated Images | **166,630 images** | `docs/dataset_specifications.md` |
| Training / Validation Split | **133,388 (80%) / 33,242 (20%)** | `docs/dataset_specifications.md` |
| Total Diagnostic Classes | **134 classes** (all 11 crops have $\ge 10$) | `model/classes.json` |
| Total Neural Parameters | **11,285,191 parameters** | Python runtime verification |
| Model Weight File Size | **45.1 MB** | `model/aerocrop_weights.pth` |
| Final Epochs Trained | **80 Epochs** | `model/training_log.csv` |
| Best Validation Accuracy | **95.27%** (Final) / **95.39%** (Peak Ep. 41) | `model/training_log.csv` |
| Macro Precision / Macro F1 | **92.77% Precision / 91.73% F1** | `model/training_log.csv` |
| Validation Yield RMSE / MAE | **8.30 t/ha RMSE / 3.39 t/ha MAE** | `model/training_log.csv` |
| Supported Maharashtra Districts | **All 36 Districts** | `backend/services/weather_service.py` |
| Automated Test Suite | **166 Tests Passing (100% Pass Rate)** | `tests/` directory execution |
