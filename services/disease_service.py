"""
AeroCrop.ai — Disease Service

Provides:
  - Complete 38-class PlantVillage disease taxonomy
  - Targeted chemical + organic treatment prescriptions
  - Crop-specific severity flags

Reference dataset: Kaggle — New Plant Diseases Dataset
GitHub: mayur7garg/PlantLeafDiseaseDetection
"""

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class DiseaseInfo:
    class_idx:   int
    name:        str
    crop:        str
    is_healthy:  bool
    chemical_treatment: list[str] = field(default_factory=list)
    organic_treatment:  list[str] = field(default_factory=list)
    severity:    str = "None"  # None | Low | Moderate | High | Critical
    description: str = ""


class DiseaseService:
    """
    Singleton service exposing the 38-class disease knowledge base.
    """

    # ── 38-class disease registry (aligned with PlantVillage) ────────────────
    DISEASES: ClassVar[list[DiseaseInfo]] = [
        DiseaseInfo(0, "Apple — Apple Scab",         "Apple",   False,
            ["Myclobutanil (Rally 40WSP)", "Captan 50WP", "Mancozeb 75WP"],
            ["Neem Oil spray (3 ml/L)", "Garlic extract"],
            "High",
            "Fungal disease causing olive-brown scab lesions on leaves and fruit."),
        DiseaseInfo(1, "Apple — Black Rot",           "Apple",   False,
            ["Thiophanate-methyl 70WP", "Ziram 76DF"],
            ["Bordeaux mixture (1%)", "Copper soap spray"],
            "High",
            "Fungal infection causing black rotting fruit and 'frog-eye' leaf spots."),
        DiseaseInfo(2, "Apple — Cedar Apple Rust",    "Apple",   False,
            ["Myclobutanil", "Propiconazole", "Trifloxystrobin"],
            ["Remove nearby juniper hosts", "Sulfur-based spray"],
            "Moderate",
            "Rust-coloured lesions requiring alternate host (juniper) for cycle completion."),
        DiseaseInfo(3, "Apple — Healthy",             "Apple",   True,  [], [],
            "None", "No disease detected. Leaf appears healthy."),
        DiseaseInfo(4, "Blueberry — Healthy",         "Blueberry", True, [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(5, "Cherry — Powdery Mildew",    "Cherry",  False,
            ["Myclobutanil", "Potassium bicarbonate", "Azoxystrobin"],
            ["Neem Oil (2%)", "Baking soda solution (5g/L)"],
            "Moderate",
            "White powdery fungal growth on leaf surfaces."),
        DiseaseInfo(6, "Cherry — Healthy",            "Cherry",  True,  [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(7, "Corn (Maize) — Cercospora Leaf Spot / Gray Leaf Spot", "Maize", False,
            ["Azoxystrobin + Propiconazole (Quilt Xcel)", "Pyraclostrobin"],
            ["Crop rotation", "Trichoderma-based biocontrol"],
            "High",
            "Gray-tan lesions running parallel to leaf veins; major yield reducer."),
        DiseaseInfo(8, "Corn (Maize) — Common Rust",  "Maize",  False,
            ["Trifloxystrobin 25SC", "Propiconazole 25EC"],
            ["Resistant varieties", "Sulfur dust application"],
            "Moderate",
            "Rust-brown pustules on both leaf surfaces spreading rapidly."),
        DiseaseInfo(9, "Corn (Maize) — Northern Leaf Blight", "Maize", False,
            ["Azoxystrobin", "Propiconazole", "Chlorothalonil 75WP"],
            ["Pseudomonas fluorescens spray", "Neem cake soil application"],
            "High",
            "Cigar-shaped, tan lesions starting from lower leaves."),
        DiseaseInfo(10, "Corn (Maize) — Healthy",     "Maize",   True,  [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(11, "Grape — Black Rot",           "Grape",  False,
            ["Myclobutanil", "Mancozeb 75WP", "Captan"],
            ["Bordeaux mixture", "Remove mummified berries"],
            "Critical",
            "Black shrivelling of berries; brown lesions with black pycnidia on leaves."),
        DiseaseInfo(12, "Grape — Esca (Black Measles)", "Grape", False,
            ["Thiophanate-methyl", "Tebuconazole"],
            ["Wound protectants", "Remove infected wood"],
            "High",
            "Tiger-striped leaves; internal wood discoloration."),
        DiseaseInfo(13, "Grape — Leaf Blight (Isariopsis Leaf Spot)", "Grape", False,
            ["Copper Oxychloride 50WP (3g/L)", "Mancozeb"],
            ["Neem Oil", "Bordeaux mixture"],
            "Moderate",
            "Dark brown leaf spots with yellow halos."),
        DiseaseInfo(14, "Grape — Healthy",             "Grape",  True,  [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(15, "Orange — Haunglongbing (Citrus Greening)", "Orange", False,
            ["Dimethoate EC (for psyllid vector)", "Imidacloprid 17.8SL"],
            ["Remove infected trees", "Beneficial insect release"],
            "Critical",
            "Bacterial disease spread by Asian citrus psyllid; causes blotchy mottling."),
        DiseaseInfo(16, "Peach — Bacterial Spot",      "Peach",  False,
            ["Copper Hydroxide 77WP", "Streptocycline + Copper Oxychloride"],
            ["Bordeaux mixture (1%)", "Copper soap"],
            "High",
            "Water-soaked spots becoming angular, dark brown lesions with yellow halos."),
        DiseaseInfo(17, "Peach — Healthy",             "Peach",  True,  [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(18, "Pepper (Bell) — Bacterial Spot", "Pepper", False,
            ["Copper Oxychloride 50WP (3g/L)", "Streptomycin sulphate"],
            ["Copper hydroxide spray", "Trichoderma harzianum"],
            "High",
            "Water-soaked lesions turning dark with yellow chlorotic halo."),
        DiseaseInfo(19, "Pepper (Bell) — Healthy",     "Pepper", True,  [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(20, "Potato — Early Blight",        "Potato", False,
            ["Chlorothalonil 75WP", "Mancozeb 75WP", "Azoxystrobin 23SC"],
            ["Neem Oil (2%)", "Garlic + Chili extract spray"],
            "Moderate",
            "Dark brown concentric ring lesions (target board pattern) on older leaves."),
        DiseaseInfo(21, "Potato — Late Blight",         "Potato", False,
            ["Metalaxyl + Mancozeb (Ridomil Gold)", "Cymoxanil 8% + Mancozeb 64%",
             "Copper Oxychloride 50WP"],
            ["Bordeaux mixture (1%)", "Trichoderma viride"],
            "Critical",
            "Water-soaked lesions turning dark brown; white sporulation under leaves."),
        DiseaseInfo(22, "Potato — Healthy",             "Potato", True,  [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(23, "Raspberry — Healthy",          "Raspberry", True, [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(24, "Soybean — Healthy",            "Soybean", True, [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(25, "Squash — Powdery Mildew",      "Squash",  False,
            ["Myclobutanil", "Potassium bicarbonate", "Trifloxystrobin"],
            ["Milk spray (10%)", "Neem Oil (2%)"],
            "Moderate",
            "White powdery coating on upper leaf surface."),
        DiseaseInfo(26, "Strawberry — Leaf Scorch",     "Strawberry", False,
            ["Iprodione 50WP", "Thiophanate-methyl 70WP"],
            ["Remove infected leaves", "Neem Oil spray"],
            "Moderate",
            "Small purple or red spots coalescing into irregular scorched patches."),
        DiseaseInfo(27, "Strawberry — Healthy",         "Strawberry", True, [], [],
            "None", "Leaf appears healthy."),
        DiseaseInfo(28, "Tomato — Bacterial Spot",      "Tomato",  False,
            ["Copper Oxychloride 50WP (3g/L)", "Streptocycline 500 ppm"],
            ["Bordeaux mixture", "Neem cake application"],
            "High",
            "Small, water-soaked spots with yellow halos on leaves and fruit."),
        DiseaseInfo(29, "Tomato — Early Blight",        "Tomato",  False,
            ["Chlorothalonil 75WP", "Azoxystrobin 23SC", "Iprodione 50WP"],
            ["Neem Oil (2%)", "Trichoderma viride spray"],
            "Moderate",
            "Concentric ring (bullseye) brown spots on older, lower leaves."),
        DiseaseInfo(30, "Tomato — Late Blight",         "Tomato",  False,
            ["Metalaxyl + Mancozeb (Ridomil)", "Copper Oxychloride 50WP",
             "Fenamidone 10% + Mancozeb 50%"],
            ["Bordeaux mixture (1%)", "Trichoderma harzianum"],
            "Critical",
            "Oily, dark green to brown lesions; white sporulation on leaf undersides in humid weather."),
        DiseaseInfo(31, "Tomato — Leaf Mold",           "Tomato",  False,
            ["Chlorothalonil", "Mancozeb", "Azoxystrobin"],
            ["Increase ventilation", "Neem Oil spray"],
            "Moderate",
            "Pale green/yellow spots on upper leaf with olive-green mold on underside."),
        DiseaseInfo(32, "Tomato — Septoria Leaf Spot",  "Tomato",  False,
            ["Chlorothalonil 75WP", "Copper-based fungicide", "Thiophanate-methyl"],
            ["Remove infected leaves", "Neem Oil"],
            "Moderate",
            "Circular spots with tan/white centers and dark borders; tiny black pycnidia inside."),
        DiseaseInfo(33, "Tomato — Spider Mites / Two-spotted Spider Mite", "Tomato", False,
            ["Abamectin 1.8EC", "Spiromesifen 22.9SC", "Etoxazole"],
            ["Neem Oil", "Water spray to dislodge mites", "Predatory mite release"],
            "Moderate",
            "Fine stippling on leaves; fine webbing on undersides; yellowing."),
        DiseaseInfo(34, "Tomato — Target Spot",         "Tomato",  False,
            ["Chlorothalonil", "Azoxystrobin + Difenoconazole (Amistar Top)"],
            ["Neem Oil spray", "Trichoderma biocontrol"],
            "High",
            "Concentric brown rings on leaves, stems, and fruit."),
        DiseaseInfo(35, "Tomato — Tomato Yellow Leaf Curl Virus", "Tomato", False,
            ["Imidacloprid 17.8SL (for whitefly vector)", "Thiamethoxam 25WG"],
            ["Reflective mulches", "Insect-proof nets", "Neem Oil"],
            "Critical",
            "Severe upward leaf curl, yellowing, stunting; spread by whitefly."),
        DiseaseInfo(36, "Tomato — Tomato Mosaic Virus",  "Tomato",  False,
            ["No curative chemical; control aphid vector with Imidacloprid"],
            ["Remove infected plants", "Sterilise tools", "Neem Oil for aphids"],
            "High",
            "Mosaic mottling and distortion of leaves; systemic viral infection."),
        DiseaseInfo(37, "Tomato — Healthy",              "Tomato",  True,  [], [],
            "None", "Leaf appears healthy."),
    ]

    # Build fast lookup dict once
    _by_idx: ClassVar[dict[int, DiseaseInfo]] = {}

    @classmethod
    def _ensure_index(cls):
        if not cls._by_idx:
            cls._by_idx = {d.class_idx: d for d in cls.DISEASES}

    @classmethod
    def get_by_index(cls, idx: int) -> DiseaseInfo | None:
        cls._ensure_index()
        return cls._by_idx.get(idx)

    @classmethod
    def get_all_names(cls) -> list[str]:
        return [d.name for d in cls.DISEASES]

    @classmethod
    def get_class_count(cls) -> int:
        return len(cls.DISEASES)
