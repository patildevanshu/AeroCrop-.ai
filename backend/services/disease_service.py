"""
AeroCrop.ai — Disease Service

Provides:
  - Canonical 50-class agricultural pathology taxonomy across 11 core crops
  - Targeted chemical + organic treatment prescriptions
  - Crop-specific severity flags

IMPORTANT: Class indices in DISEASES list MUST match model/classes.json exactly.
Ordering mirrors canonical folder names from the unified dataset:
  Banana (0-3), Corn/Maize (4-7), Cotton (8-9), Orange (10), Potato (11-13),
  Rice (14-18), Soybean (19), Sugarcane (20-24), Tomato (25-34),
  Turmeric (35-38), Wheat (39-49).
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
    Singleton service exposing the 50-class pathology knowledge base.
    Class indices MUST match model/classes.json exactly.
    """

    DISEASES: ClassVar[list[DiseaseInfo]] = [
        # ── Banana (0–3) ─────────────────────────────────────────────────────
        DiseaseInfo(
            0, "Banana — Cordana Leaf Spot (Cordana musae)", "Banana", False,
            ["Mancozeb 75WP (2 g/L)", "Propiconazole 25EC (1 ml/L)", "Carbendazim 50WP (1 g/L)"],
            ["Neem oil foliar spray (2%)", "Remove infected foliage", "Ensure plantation drainage"],
            "Moderate",
            "Oval to spindle-shaped lesions with bright yellow halos coalescing into pale brown necrotic areas."
        ),
        DiseaseInfo(
            1, "Banana — Panama Disease / Fusarium Wilt (Fusarium oxysporum)", "Banana", False,
            ["Carbendazim 50WP (2 g/L soil drench)", "Copper Oxychloride (2.5 g/L)"],
            ["Trichoderma viride / harzianum bio-agent", "Resistant suckers (e.g. Grand Naine)", "Soil solarization"],
            "Critical",
            "Lethal vascular wilt characterized by yellowing of lower leaves, longitudinal pseudostem splitting, and vascular discoloration."
        ),
        DiseaseInfo(
            2, "Banana — Sigatoka Leaf Spot (Pseudocercospora fijiensis / musae)", "Banana", False,
            ["Propiconazole 25EC (1 ml/L)", "Trifloxystrobin + Tebuconazole (1 g/L)", "Mancozeb 75WP (2 g/L)"],
            ["Mineral oil spray (1%)", "Prune spotted leaves during dry weather", "Balanced potassium nutrition"],
            "High",
            "Narrow reddish-brown streaks enlarging into elliptical dark brown lesions with grey sunken centers, reducing photosynthetic leaf area."
        ),
        DiseaseInfo(
            3, "Banana — Healthy", "Banana", True,
            [], [], "None",
            "Lush, broad green banana fronds free from chlorotic streaks, necrotic blotches, or pseudostem wilting."
        ),

        # ── Corn / Maize (4–7) ───────────────────────────────────────────────
        DiseaseInfo(
            4, "Corn (Maize) — Cercospora Leaf Spot / Gray Leaf Spot", "Maize", False,
            ["Azoxystrobin + Propiconazole (Quilt Xcel 1 ml/L)", "Pyraclostrobin 20WG (1 g/L)"],
            ["Crop rotation with non-host legumes", "Resistant hybrids", "Trichoderma foliar spray"],
            "High",
            "Narrow rectangular grey-to-tan necrotic lesions running strictly parallel to leaf veins."
        ),
        DiseaseInfo(
            5, "Corn (Maize) — Common Rust (Puccinia sorghi)", "Maize", False,
            ["Mancozeb 75WP (2 g/L)", "Tebuconazole 25.9EC (1 ml/L)", "Azoxystrobin (1 ml/L)"],
            ["Resistant hybrid varieties", "Sulfur dust foliar application", "Neem extract foliar spray"],
            "Moderate",
            "Small, powdery cinnamon-brown pustules erupting on both upper and lower leaf surfaces."
        ),
        DiseaseInfo(
            6, "Corn (Maize) — Northern Leaf Blight (Exserohilum turcicum)", "Maize", False,
            ["Mancozeb 75WP (2.5 g/L)", "Azoxystrobin (1 ml/L)", "Propiconazole 25EC (1 ml/L)"],
            ["Plow down crop residues", "Resistant crop rotation", "Trichoderma viride seed treatment"],
            "High",
            "Long, elliptical, cigar-shaped grayish-green lesions turning tan and necrotic."
        ),
        DiseaseInfo(
            7, "Corn (Maize) — Healthy", "Maize", True,
            [], [], "None",
            "Vigorous erect maize foliage with deep green coloring and no fungal pustules or necrotic streaks."
        ),

        # ── Cotton (8–9) ─────────────────────────────────────────────────────
        DiseaseInfo(
            8, "Cotton — Bacterial Blight / Black Arm (Xanthomonas citri)", "Cotton", False,
            ["Copper Oxychloride 50WP (2.5 g/L) + Streptocycline (100 ppm / 1 g in 10L)", "Kasugamycin 3% SL"],
            ["Pseudomonas fluorescens foliar spray (5 g/L)", "Neem seed kernel extract (NSKE 5%)", "Acid delinting of seeds"],
            "Critical",
            "Angular water-soaked dark brown leaf lesions bounded by veins, progressing into black arm lesion stem dieback."
        ),
        DiseaseInfo(
            9, "Cotton — Healthy", "Cotton", True,
            [], [], "None",
            "Vibrant, dark green palmate cotton leaves without angular water-soaked spots, vein-blight, or boll rot."
        ),

        # ── Orange / Citrus (10) ─────────────────────────────────────────────
        DiseaseInfo(
            10, "Orange — Huanglongbing / Citrus Greening (Candidatus Liberibacter)", "Orange", False,
            ["Imidacloprid 17.8SL (0.5 ml/L to suppress psyllid vector)", "Thiamethoxam 25WG (0.3 g/L)", "Tetracycline trunk injection"],
            ["Sticky yellow traps for Asian Citrus Psyllid", "Release of Tamarixia radiata parasitoid", "Strict quarantine & certified budwood"],
            "Critical",
            "Asymmetric blotchy leaf mottle crossing secondary veins, yellow vein chlorosis, and stunted bitter lopsided fruit."
        ),

        # ── Potato (11–13) ───────────────────────────────────────────────────
        DiseaseInfo(
            11, "Potato — Early Blight (Alternaria solani)", "Potato", False,
            ["Mancozeb 75WP (2 g/L)", "Chlorothalonil 75WP (2 g/L)", "Difenoconazole 25EC (0.5 ml/L)"],
            ["Copper hydroxide spray", "Neem oil (2%)", "Crop rotation avoiding Solanaceae"],
            "Moderate",
            "Dark brown concentric rings forming distinctive 'target board' lesions on older foliage."
        ),
        DiseaseInfo(
            12, "Potato — Late Blight (Phytophthora infestans)", "Potato", False,
            ["Metalaxyl 8% + Mancozeb 64% WP (Ridomil Gold 2 g/L)", "Cymoxanil + Mancozeb (2 g/L)", "Dimethomorph 50WP (1 g/L)"],
            ["Bordeaux mixture (1%) preventive spray", "Certified disease-free seed tubers", "Immediate destruction of infected haulms"],
            "Critical",
            "Water-soaked dark lesions with pale green borders and white fuzzy fungal growth on the underside during humid conditions."
        ),
        DiseaseInfo(
            13, "Potato — Healthy", "Potato", True,
            [], [], "None",
            "Vibrant composite potato foliage free from water-soaked blights or concentric fungal spots."
        ),

        # ── Rice (14–18) ─────────────────────────────────────────────────────
        DiseaseInfo(
            14, "Rice — Bacterial Leaf Blight (Xanthomonas oryzae)", "Rice", False,
            ["Copper Hydroxide 77WP (2 g/L) + Streptocycline (100 ppm)", "Bismerthiazol (1 g/L)"],
            ["Neem oil spray (2%)", "Avoid excess split nitrogen application", "Plow stubble after harvest"],
            "Critical",
            "Water-soaked stripes starting at leaf tips/margins, rapidly expanding into wavy yellowish-white bleached lesions."
        ),
        DiseaseInfo(
            15, "Rice — Brown Spot (Bipolaris oryzae)", "Rice", False,
            ["Mancozeb 75WP (2 g/L)", "Tricyclazole 75WP (0.6 g/L)", "Edifenphos 50EC (1 ml/L)"],
            ["Pseudomonas fluorescens seed treatment (10 g/kg)", "Balanced NPK + Zinc sulfate soil replenishment", "Neem cake application"],
            "High",
            "Oval or circular dark brown spots with distinct grey or whitish centers scattered uniformly across leaf blades."
        ),
        DiseaseInfo(
            16, "Rice — Leaf Blast (Magnaporthe oryzae / Pyricularia oryzae)", "Rice", False,
            ["Tricyclazole 75WP (0.6 g/L)", "Isoprothiolane 40EC (1.5 ml/L)", "Kasugamycin 3% SL (2 ml/L)"],
            ["Seed treatment with Trichoderma viride", "Silica soil supplementation", "Avoid excessive nitrogen top-dressing"],
            "Critical",
            "Spindle-shaped diamond lesions with pointed ends, grey/whitish centers, and reddish-brown margins causing lodging."
        ),
        DiseaseInfo(
            17, "Rice — Leaf Smut (Entyloma oryzae)", "Rice", False,
            ["Mancozeb 75WP (2 g/L)", "Copper Oxychloride 50WP (2.5 g/L)", "Propiconazole 25EC (1 ml/L)"],
            ["Balanced soil nutrition", "Neem extract foliar application (5%)", "Ensure clean field sanitation"],
            "Moderate",
            "Small, slightly elevated angular black spots scattered across both surfaces of mature leaf blades."
        ),
        DiseaseInfo(
            18, "Rice — Tungro Disease (Rice Tungro Spherical/Bacilliform Virus)", "Rice", False,
            ["Thiamethoxam 25WG (0.3 g/L to suppress Green Leafhopper vector)", "Imidacloprid 17.8SL (0.5 ml/L)"],
            ["Yellow sticky traps for Nephotettix virescens vector", "Rogue out infected plants immediately", "Synchronous planting"],
            "Critical",
            "Severe leaf yellowing to orange discoloration starting from tip, marked plant stunting, and poor tillering."
        ),

        # ── Soybean (19) ─────────────────────────────────────────────────────
        DiseaseInfo(
            19, "Soybean — Healthy", "Soybean", True,
            [], [], "None",
            "Vigorous trifoliate soybean canopy showing uniform bright green pigmentation without rust, mosaic, or blight."
        ),

        # ── Sugarcane (20–24) ────────────────────────────────────────────────
        DiseaseInfo(
            20, "Sugarcane — Mosaic (Sugarcane Mosaic Virus - SCMV)", "Sugarcane", False,
            ["Imidacloprid (0.5 ml/L to control aphid vector Melanaphis sacchari)", "Dimethoate 30EC (1.7 ml/L)"],
            ["Certified virus-free tissue cultured seed cane", "Hot water sett treatment (52°C for 30 min)", "Rogue out affected clumps"],
            "Moderate",
            "Mottled pattern of contrasting dark and light green islands, chlorotic streaks running parallel to midrib."
        ),
        DiseaseInfo(
            21, "Sugarcane — Red Rot (Colletotrichum falcatum)", "Sugarcane", False,
            ["Carbendazim 50WP sett dip (1 g/L)", "Thiophanate-methyl 70WP"],
            ["Trichoderma viride sett treatment (10 g/L)", "Resistant varieties (e.g. Co 86032)", "Avoid ratoon cropping in infected fields"],
            "Critical",
            "Internal reddening of stalk tissue interrupted by white transverse patches with characteristic alcohol/sour odor."
        ),
        DiseaseInfo(
            22, "Sugarcane — Rust (Puccinia melanocephala)", "Sugarcane", False,
            ["Mancozeb 75WP (2 g/L)", "Propiconazole 25EC (1 ml/L)", "Triadimefon 25WP (1 g/L)"],
            ["Sulfur dusting (25 kg/ha)", "Resistant cultivars", "Avoid dense planting to improve air circulation"],
            "Moderate",
            "Elongated chlorotic flecks developing into reddish-brown raised pustules that rupture into powdery spores."
        ),
        DiseaseInfo(
            23, "Sugarcane — Yellow Leaf (Sugarcane Yellow Leaf Virus - SCYLV)", "Sugarcane", False,
            ["Thiamethoxam (0.3 g/L for aphid vector management)", "Pymetrozine 50WG"],
            ["Tissue-cultured disease-free setts", "Proper balanced potassium fertilization", "Field sanitation"],
            "High",
            "Intense yellowing of midrib on the lower surface of leaves 3 to 6, gradually spreading across leaf blade."
        ),
        DiseaseInfo(
            24, "Sugarcane — Healthy", "Sugarcane", True,
            [], [], "None",
            "Robust deep green linear sugarcane leaves with clear central midrib and complete absence of red rot or mosaic."
        ),

        # ── Tomato (25–34) ───────────────────────────────────────────────────
        DiseaseInfo(
            25, "Tomato — Bacterial Spot (Xanthomonas perforans)", "Tomato", False,
            ["Copper Hydroxide (2 g/L) + Streptocycline (100 ppm)", "Kasugamycin (2 ml/L)"],
            ["Bordeaux mixture (1%)", "Resistant seed varieties", "Avoid overhead drip splash"],
            "High",
            "Small, dark, water-soaked circular lesions on foliage and raised scab-like spots on tomato fruit."
        ),
        DiseaseInfo(
            26, "Tomato — Early Blight (Alternaria solani)", "Tomato", False,
            ["Mancozeb 75WP (2 g/L)", "Azoxystrobin 23SC (1 ml/L)", "Difenoconazole 25EC (0.5 ml/L)"],
            ["Copper soap spray", "Prune lower leaves to enhance airflow", "Mulch base to stop soil splash"],
            "High",
            "Dark brown concentric rings producing characteristic 'target board' lesions bordered by yellow halos."
        ),
        DiseaseInfo(
            27, "Tomato — Late Blight (Phytophthora infestans)", "Tomato", False,
            ["Metalaxyl 8% + Mancozeb 64% WP (2 g/L)", "Cymoxanil + Mancozeb (2 g/L)", "Dimethomorph (1 g/L)"],
            ["Bordeaux mixture (1%) preventive application", "Destroy infected vine debris", "Avoid excess moisture"],
            "Critical",
            "Rapidly expanding pale green to dark water-soaked lesions with white sporulation on undersides during damp mornings."
        ),
        DiseaseInfo(
            28, "Tomato — Leaf Mold (Passalora fulva)", "Tomato", False,
            ["Chlorothalonil 75WP (2 g/L)", "Mancozeb 75WP (2 g/L)", "Copper Oxychloride (2.5 g/L)"],
            ["Ensure greenhouse ventilation", "Neem oil (2%) foliar spray", "Drip irrigation to keep foliage dry"],
            "Moderate",
            "Pale greenish-yellow chlorotic spots on upper leaf surfaces matching olive-green velvety fungal patches beneath."
        ),
        DiseaseInfo(
            29, "Tomato — Septoria Leaf Spot (Septoria lycopersici)", "Tomato", False,
            ["Mancozeb 75WP (2 g/L)", "Chlorothalonil 75WP (2 g/L)", "Propiconazole 25EC (1 ml/L)"],
            ["Clean crop debris", "Mulch heavily around base of tomato plants", "Crop rotation"],
            "Moderate",
            "Numerous small circular spots with dark brown margins and sunken tan centers bearing tiny black pycnidia."
        ),
        DiseaseInfo(
            30, "Tomato — Spider Mites / Two-Spotted Spider Mite (Tetranychus urticae)", "Tomato", False,
            ["Abamectin 1.9EC (0.5 ml/L)", "Spiromesifen 22.9SC (1 ml/L)", "Fenazaquin 10EC (1.5 ml/L)"],
            ["Neem oil foliar spray (3%)", "Release Phytoseiulus persimilis predatory mites", "High-pressure water spray"],
            "Moderate",
            "Fine yellow stippling across leaf surfaces, dense silken webbing on undersides, and leaf bronzing under dry hot weather."
        ),
        DiseaseInfo(
            31, "Tomato — Target Spot (Corynespora cassiicola)", "Tomato", False,
            ["Azoxystrobin 23SC (1 ml/L)", "Chlorothalonil (2 g/L)", "Boscalid + Pyraclostrobin"],
            ["Copper fungicide spray", "Improve plant spacing for air penetration", "Sanitize stakes and trellises"],
            "Moderate",
            "Small brown circular lesions with distinct light brown concentric centers and dark borders causing defoliation."
        ),
        DiseaseInfo(
            32, "Tomato — Tomato Yellow Leaf Curl Virus (TYLCV)", "Tomato", False,
            ["Thiamethoxam 25WG (0.3 g/L for whitefly control)", "Imidacloprid 17.8SL (0.5 ml/L)", "Diafenthiuron 50WP (1 g/L)"],
            ["Yellow sticky insect traps", "Fine insect-proof net covering (40-50 mesh)", "Immediate eradication of infected plants"],
            "Critical",
            "Severe upward curling and cupping of leaflets, reduced leaflet size, chlorotic leaf margins, and bushy stunting."
        ),
        DiseaseInfo(
            33, "Tomato — Tomato Mosaic Virus (ToMV)", "Tomato", False,
            ["No direct chemical viricide; disinfect tools with 10% Trisodium phosphate (TSP)", "Spray skim milk solution (20%)"],
            ["Strict tool and hand sanitization before pruning", "Resistant tomato hybrids (Tm-2a gene)", "Seed treatment in hot water (56°C)"],
            "High",
            "Alternating light and dark green mosaic patterns, leaf puckering, distortion, and 'fern-leaf' strapping."
        ),
        DiseaseInfo(
            34, "Tomato — Healthy", "Tomato", True,
            [], [], "None",
            "Vigorous tomato vine with balanced green foliage, sturdy petioles, and no signs of bacterial spot or viral curling."
        ),

        # ── Turmeric (35–38) ─────────────────────────────────────────────────
        DiseaseInfo(
            35, "Turmeric — Dry Leaf / Leaf Blight (Rhizoctonia / Alternaria)", "Turmeric", False,
            ["Mancozeb 75WP (2 g/L)", "Copper Oxychloride 50WP (2.5 g/L)", "Carbendazim 50WP (1 g/L)"],
            ["Neem cake soil application (250 kg/ha)", "Panchagavya spray (3%)", "Ensure ridge drainage"],
            "Moderate",
            "Extensive leaf margin drying and tip burn advancing inwards, causing premature drying of the turmeric canopy."
        ),
        DiseaseInfo(
            36, "Turmeric — Leaf Blotch (Taphrina maculans)", "Turmeric", False,
            ["Mancozeb 75WP (2 g/L)", "Copper Oxychloride (2.5 g/L)", "Propiconazole 25EC (1 ml/L)"],
            ["Panchagavya foliar spray (3%)", "Pseudomonas fluorescens foliar spray (5 g/L)", "Balanced potassium nutrition"],
            "Moderate",
            "Small rectangular reddish-brown to dark brown spots on both leaf surfaces coalescing into extensive blotches."
        ),
        DiseaseInfo(
            37, "Turmeric — Rhizome Rot (Pythium aphanidermatum)", "Turmeric", False,
            ["Metalaxyl 8% + Mancozeb 64% WP soil drench (Ridomil Gold 2 g/L)", "Copper Oxychloride drench (3 g/L)"],
            ["Seed rhizome treatment with Trichoderma viride (10 g/kg)", "Raised broad-bed planting for drainage", "Soil solarization"],
            "Critical",
            "Basal pseudostem rotting, yellowing of lower leaves, collar necrosis, and soft water-soaked decaying rhizomes with foul odor."
        ),
        DiseaseInfo(
            38, "Turmeric — Healthy", "Turmeric", True,
            [], [], "None",
            "Erect, broad glossy green turmeric leaves free from necrotic margins, blotches, or basal collar rot."
        ),

        # ── Wheat (39–49) ────────────────────────────────────────────────────
        DiseaseInfo(
            39, "Wheat — Aphid Infestation (Rhopalosiphum padi / Sitobion avenae)", "Wheat", False,
            ["Thiamethoxam 25WG (0.3 g/L)", "Dimethoate 30EC (1.5 ml/L)", "Imidacloprid 17.8SL (0.4 ml/L)"],
            ["Neem oil foliar spray (3%)", "Encourage Coccinellid ladybird beetles", "Yellow sticky traps"],
            "Moderate",
            "Colonies of tiny green-black aphids clustering on flag leaves and earheads, sucking sap and secreting sticky honeydew."
        ),
        DiseaseInfo(
            40, "Wheat — Black Rust / Stem Rust (Puccinia graminis f. sp. tritici)", "Wheat", False,
            ["Propiconazole 25EC (Tilt 1 ml/L)", "Tebuconazole 25.9EC (1 ml/L)", "Mancozeb 75WP (2 g/L)"],
            ["Cultivate resistant varieties (e.g. DBW series)", "Early sowing to escape warm late-season infection", "Barberry host eradication"],
            "Critical",
            "Large, reddish-brown to dark black elongated pustules erupting through stem, leaf sheath, and glumes with frayed epidermal edges."
        ),
        DiseaseInfo(
            41, "Wheat — Brown Rust / Leaf Rust (Puccinia triticina)", "Wheat", False,
            ["Propiconazole 25EC (1 ml/L)", "Mancozeb 75WP (2 g/L)", "Azoxystrobin (1 ml/L)"],
            ["Resistant wheat cultivars", "Sulfur dust application (25 kg/ha)", "Trichoderma viride foliar spray"],
            "High",
            "Small circular orange-brown pustules scattered randomly across upper leaf surfaces, rarely forming elongated stripes."
        ),
        DiseaseInfo(
            42, "Wheat — Flag Smut (Urocystis agropyri)", "Wheat", False,
            ["Carboxin 37.5% + Thiram 37.5% seed treatment (Vitavax 2 g/kg)", "Tebuconazole seed dressing (1 g/kg)"],
            ["Seed treatment with Trichoderma harzianum", "Crop rotation with non-host gramineous crops", "Deep summer plowing"],
            "High",
            "Long dark grey-to-black lead-colored stripes on leaf blades and sheaths that rupture to discharge masses of black sooty teliospores."
        ),
        DiseaseInfo(
            43, "Wheat — Leaf Blight / Spot Blotch (Bipolaris sorokiniana)", "Wheat", False,
            ["Propiconazole 25EC (1 ml/L)", "Mancozeb 75WP (2.5 g/L)", "Tebuconazole (1 ml/L)"],
            ["Pseudomonas fluorescens seed treatment (10 g/kg)", "Resistant cultivars", "Avoid post-anthesis moisture stress"],
            "High",
            "Small, oval, dark brown spots enlarging into irregular lens-shaped necrotic lesions with chlorotic yellow borders."
        ),
        DiseaseInfo(
            44, "Wheat — Mite Infestation (Wheat Curl Mite / Brown Wheat Mite)", "Wheat", False,
            ["Wettable Sulfur 80WP (3 g/L)", "Propargite 57EC (2 ml/L)", "Fenazaquin 10EC (1.5 ml/L)"],
            ["Neem seed extract (5%)", "Frequent light irrigation to suppress dry mite outbreaks", "Predatory phytoseiid mites"],
            "Moderate",
            "Leaves rolling tightly inward into needle-like tubes, fine silvery-white speckling, and viral streak transmission."
        ),
        DiseaseInfo(
            45, "Wheat — Powdery Mildew (Blumeria graminis f. sp. tritici)", "Wheat", False,
            ["Propiconazole 25EC (1 ml/L)", "Triadimefon 25WP (1 g/L)", "Hexaconazole 5EC (1 ml/L)"],
            ["Wettable sulfur spray (2 g/L)", "Avoid excessive nitrogen fertilizers", "Resistant crop cultivars"],
            "Moderate",
            "White-to-greyish fluffy powdery fungal colonies spreading across leaf blades and sheaths, later turning dull tan with black cleistothecia."
        ),
        DiseaseInfo(
            46, "Wheat — Scab / Fusarium Head Blight (Fusarium graminearum)", "Wheat", False,
            ["Tebuconazole 25.9EC (1 ml/L)", "Prothioconazole", "Metconazole at anthesis/flowering"],
            ["Resistant wheat lines", "Bury corn stubble residue", "Avoid sprinkler irrigation during flowering"],
            "Critical",
            "Premature bleaching of individual spikelets or the entire earhead, with pinkish-salmon fungal sporulation at spikelet bases."
        ),
        DiseaseInfo(
            47, "Wheat — Stem Fly / Shoot Fly (Atherigona naqvii)", "Wheat", False,
            ["Chlorpyrifos 20EC (2 ml/L)", "Thiamethoxam 30FS seed dressing (3 ml/kg)", "Quinalphos 25EC (2 ml/L)"],
            ["Higher seed rate (125 kg/ha) to compensate seedling loss", "Early sowing within recommended window", "Neem cake soil application"],
            "High",
            "Maggots bore into growing shoots, cutting the central growing point and producing characteristic 'dead hearts' in young seedlings."
        ),
        DiseaseInfo(
            48, "Wheat — Yellow Rust / Stripe Rust (Puccinia striiformis)", "Wheat", False,
            ["Propiconazole 25EC (Tilt 1 ml/L)", "Tebuconazole 25.9EC (1 ml/L)", "Mancozeb 75WP (2 g/L)"],
            ["Cultivate resistant cultivars (HD 2967, DBW series)", "Sulfur dusting (25 kg/ha)", "Early detection & containment"],
            "Critical",
            "Bright lemon-yellow powdery pustules arranged in narrow, parallel continuous stripes along leaf veins resembling yellow beads."
        ),
        DiseaseInfo(
            49, "Wheat — Healthy", "Wheat", True,
            [], [], "None",
            "Healthy erect green wheat foliage with clean flag leaves, sturdy stems, and robust green earheads devoid of rust or blight."
        ),
    ]

    # Fast lookup dict
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
