# AeroCrop.ai — Dataset Specifications & Distribution

**Audit Timestamp**: 2026-09-06  
- **Total Dataset Images**: **98,963**
- **Training Images (80%)**: **79,166**
- **Validation Images (20%)**: **19,797**
- **Marked (Diseased / Symptomatic)**: **67,771** (68.5%)
- **Unmarked (Healthy / Asymptomatic)**: **31,192** (31.5%)
- **Total Diagnostic Classes**: **56**
- **Total Crops Covered**: **19**

## 1. Crop-Wise Breakdown

| Crop | Total Images | Train (80%) | Valid (20%) | Classes | Primary Regional Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tomato** | 22,598 | 18,078 | 4,520 | 10 | Maharashtra & Pan-India |
| **Corn_(maize)** | 11,220 | 8,975 | 2,245 | 4 | Maharashtra & Pan-India |
| **Apple** | 9,819 | 7,851 | 1,968 | 4 | Maharashtra & Pan-India |
| **Grape** | 9,027 | 7,222 | 1,805 | 4 | Maharashtra (Nashik/Sangli) |
| **Potato** | 6,652 | 5,321 | 1,331 | 3 | Maharashtra & Pan-India |
| **Pepper,_bell** | 4,876 | 3,901 | 975 | 2 | Maharashtra & Pan-India |
| **Strawberry** | 4,498 | 3,598 | 900 | 2 | Maharashtra & Pan-India |
| **Peach** | 4,457 | 3,566 | 891 | 2 | Maharashtra & Pan-India |
| **Cherry_(including_sour)** | 4,386 | 3,509 | 877 | 2 | Maharashtra & Pan-India |
| **Banana** | 3,108 | 2,491 | 617 | 4 | Maharashtra & Pan-India |
| **Soybean** | 2,527 | 2,022 | 505 | 1 | Maharashtra & Pan-India |
| **Sugarcane** | 2,521 | 2,015 | 506 | 5 | Maharashtra & Pan-India |
| **Orange** | 2,513 | 2,010 | 503 | 1 | Maharashtra & Pan-India |
| **Cotton** | 2,386 | 1,907 | 479 | 2 | Maharashtra & Pan-India |
| **Blueberry** | 2,270 | 1,816 | 454 | 1 | Maharashtra & Pan-India |
| **Raspberry** | 2,226 | 1,781 | 445 | 1 | Maharashtra & Pan-India |
| **Squash** | 2,170 | 1,736 | 434 | 1 | Maharashtra & Pan-India |
| **Turmeric** | 781 | 623 | 158 | 4 | Maharashtra & Pan-India |
| **Rice** | 120 | 96 | 24 | 3 | Maharashtra & Pan-India |

## 2. Complete 56-Class Distribution (Marked vs Unmarked)

| Index | Canonical Class Identifier | Crop | Category | Train | Valid | Total |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | `Apple___Apple_scab` | Apple | Marked (Diseased) | 2016 | 504 | 2520 |
| `1` | `Apple___Black_rot` | Apple | Marked (Diseased) | 1987 | 497 | 2484 |
| `2` | `Apple___Cedar_apple_rust` | Apple | Marked (Diseased) | 1810 | 455 | 2265 |
| `3` | `Apple___healthy` | Apple | Unmarked (Healthy) | 2038 | 512 | 2550 |
| `4` | `Blueberry___healthy` | Blueberry | Unmarked (Healthy) | 1816 | 454 | 2270 |
| `5` | `Cherry_(including_sour)___healthy` | Cherry_(including_sour) | Unmarked (Healthy) | 1826 | 456 | 2282 |
| `6` | `Cherry_(including_sour)___Powdery_mildew` | Cherry_(including_sour) | Marked (Diseased) | 1683 | 421 | 2104 |
| `7` | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Corn_(maize) | Marked (Diseased) | 2155 | 539 | 2694 |
| `8` | `Corn_(maize)___Common_rust_` | Corn_(maize) | Marked (Diseased) | 1907 | 477 | 2384 |
| `9` | `Corn_(maize)___healthy` | Corn_(maize) | Unmarked (Healthy) | 2285 | 572 | 2857 |
| `10` | `Corn_(maize)___Northern_Leaf_Blight` | Corn_(maize) | Marked (Diseased) | 2628 | 657 | 3285 |
| `11` | `Grape___Black_rot` | Grape | Marked (Diseased) | 1888 | 472 | 2360 |
| `12` | `Grape___Esca_(Black_Measles)` | Grape | Marked (Diseased) | 1920 | 480 | 2400 |
| `13` | `Grape___healthy` | Grape | Unmarked (Healthy) | 1692 | 423 | 2115 |
| `14` | `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | Grape | Marked (Diseased) | 1722 | 430 | 2152 |
| `15` | `Orange___Haunglongbing_(Citrus_greening)` | Orange | Marked (Diseased) | 2010 | 503 | 2513 |
| `16` | `Peach___Bacterial_spot` | Peach | Marked (Diseased) | 1838 | 459 | 2297 |
| `17` | `Peach___healthy` | Peach | Unmarked (Healthy) | 1728 | 432 | 2160 |
| `18` | `Pepper,_bell___Bacterial_spot` | Pepper,_bell | Marked (Diseased) | 1913 | 478 | 2391 |
| `19` | `Pepper,_bell___healthy` | Pepper,_bell | Unmarked (Healthy) | 1988 | 497 | 2485 |
| `20` | `Potato___Early_blight` | Potato | Marked (Diseased) | 1939 | 485 | 2424 |
| `21` | `Potato___healthy` | Potato | Unmarked (Healthy) | 1824 | 456 | 2280 |
| `22` | `Potato___Late_blight` | Potato | Marked (Diseased) | 1939 | 485 | 2424 |
| `23` | `Raspberry___healthy` | Raspberry | Unmarked (Healthy) | 1781 | 445 | 2226 |
| `24` | `Soybean___healthy` | Soybean | Unmarked (Healthy) | 2022 | 505 | 2527 |
| `25` | `Squash___Powdery_mildew` | Squash | Marked (Diseased) | 1736 | 434 | 2170 |
| `26` | `Strawberry___healthy` | Strawberry | Unmarked (Healthy) | 1824 | 456 | 2280 |
| `27` | `Strawberry___Leaf_scorch` | Strawberry | Marked (Diseased) | 1774 | 444 | 2218 |
| `28` | `Tomato___Bacterial_spot` | Tomato | Marked (Diseased) | 1702 | 425 | 2127 |
| `29` | `Tomato___Early_blight` | Tomato | Marked (Diseased) | 1920 | 480 | 2400 |
| `30` | `Tomato___healthy` | Tomato | Unmarked (Healthy) | 1926 | 481 | 2407 |
| `31` | `Tomato___Late_blight` | Tomato | Marked (Diseased) | 1851 | 463 | 2314 |
| `32` | `Tomato___Leaf_Mold` | Tomato | Marked (Diseased) | 1882 | 470 | 2352 |
| `33` | `Tomato___Septoria_leaf_spot` | Tomato | Marked (Diseased) | 1745 | 436 | 2181 |
| `34` | `Tomato___Spider_mites Two-spotted_spider_mite` | Tomato | Marked (Diseased) | 1741 | 435 | 2176 |
| `35` | `Tomato___Target_Spot` | Tomato | Marked (Diseased) | 1827 | 457 | 2284 |
| `36` | `Tomato___Tomato_mosaic_virus` | Tomato | Marked (Diseased) | 1790 | 448 | 2238 |
| `37` | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | Tomato | Marked (Diseased) | 1961 | 490 | 2451 |
| `38` | `Cotton___Bacterial_blight` | Cotton | Marked (Diseased) | 1081 | 272 | 1353 |
| `39` | `Cotton___healthy` | Cotton | Unmarked (Healthy) | 826 | 207 | 1033 |
| `40` | `Banana___Cordana_leaf_spot` | Banana | Marked (Diseased) | 273 | 69 | 342 |
| `41` | `Banana___Panama_disease` | Banana | Marked (Diseased) | 668 | 167 | 835 |
| `42` | `Banana___Sigatoka` | Banana | Marked (Diseased) | 750 | 180 | 930 |
| `43` | `Banana___healthy` | Banana | Unmarked (Healthy) | 800 | 201 | 1001 |
| `44` | `Sugarcane___Mosaic` | Sugarcane | Marked (Diseased) | 369 | 93 | 462 |
| `45` | `Sugarcane___Red_rot` | Sugarcane | Marked (Diseased) | 414 | 104 | 518 |
| `46` | `Sugarcane___Rust` | Sugarcane | Marked (Diseased) | 411 | 103 | 514 |
| `47` | `Sugarcane___Yellow_leaf` | Sugarcane | Marked (Diseased) | 404 | 101 | 505 |
| `48` | `Sugarcane___healthy` | Sugarcane | Unmarked (Healthy) | 417 | 105 | 522 |
| `49` | `Rice___Bacterial_leaf_blight` | Rice | Marked (Diseased) | 32 | 8 | 40 |
| `50` | `Rice___Brown_spot` | Rice | Marked (Diseased) | 32 | 8 | 40 |
| `51` | `Rice___Leaf_smut` | Rice | Marked (Diseased) | 32 | 8 | 40 |
| `52` | `Turmeric___Dry_leaf` | Turmeric | Marked (Diseased) | 162 | 41 | 203 |
| `53` | `Turmeric___Leaf_blotch` | Turmeric | Marked (Diseased) | 159 | 40 | 199 |
| `54` | `Turmeric___Rhizome_rot` | Turmeric | Marked (Diseased) | 145 | 37 | 182 |
| `55` | `Turmeric___healthy` | Turmeric | Unmarked (Healthy) | 157 | 40 | 197 |
