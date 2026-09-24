/**
 * AeroCrop.ai — Agronomic Commercial Yield Utility
 *
 * Standardises crop harvest yield display to authentic Indian agricultural conventions
 * (ICAR & Maharashtra Agriculture Commissionerate standards):
 *
 * 1. Biomass / Fresh Horticultural Produce (Sugarcane, Banana, Tomato, Potato, Orange, Onion, Apple, Grape):
 *    - Standard Commercial Unit: Tonnes / Acre (टन / एकर)
 *    - Conversion: yield_t_ha / 2.47105 (or yield_t_ha * 0.4047)
 *
 * 2. Field / Grain / Oilseed / Fiber / Rhizome Crops (Cotton, Soybean, Wheat, Rice, Maize, Turmeric, Pepper):
 *    - Standard Commercial Unit: Quintal / Acre (क्विंटल / एकर)
 *    - Conversion: (yield_t_ha * 10) / 2.47105 (or yield_t_ha * 4.047)
 */

export interface FormattedYield {
  /** Primary formatted yield string, e.g. "30.4 Tonnes / Acre" or "10.5 Quintal / Acre" */
  primary: string;
  /** Primary numeric value formatted to 1 decimal place, e.g. "30.4" */
  primaryValue: string;
  /** Primary commercial unit string */
  unit: 'Tonnes / Acre' | 'Quintal / Acre';
  /** Short unit symbol, e.g. "T/Ac" or "Q/Ac" */
  unitShort: 'T/Ac' | 'Q/Ac';
  /** Secondary conversion string, e.g. "≈ 304 Q/Ac · 75.0 t/ha" or "≈ 2.6 t/ha" */
  secondary: string;
  /** Typical ICAR regional benchmark range string, e.g. "28 – 36 Tonnes / Acre" */
  benchmark: string;
  /** Crop produce category label, e.g. "Fresh Stalk Biomass (ऊस वजन)" */
  categoryLabel: string;
  /** Loss impact text if loss is present, e.g. "⚠️ ~15.0% loss impact" */
  lossImpactText?: string | null;
  /** Is this a heavy biomass / horticultural crop */
  isBiomassCrop: boolean;
}

export interface YieldSourceData {
  commercial_unit?: string | null;
  commercial_yield?: number | null;
  commercial_baseline?: number | null;
  benchmark_range?: string | null;
  yield_category_label?: string | null;
  crop_category_label?: string | null;
  yield_loss_pct?: number | null;
  baseline_yield_t_ha?: number | null;
}

interface CropYieldProfile {
  unit: 'Tonnes / Acre' | 'Quintal / Acre';
  unitShort: 'T/Ac' | 'Q/Ac';
  mult: number;
  benchmark: string;
  categoryLabel: string;
}

const CROP_PROFILES: Record<string, CropYieldProfile> = {
  sugarcane: {
    unit: 'Tonnes / Acre',
    unitShort: 'T/Ac',
    mult: 0.4047,
    benchmark: '28 – 36 Tonnes / Acre',
    categoryLabel: 'Fresh Stalk Biomass (ऊस वजन)',
  },
  banana: {
    unit: 'Tonnes / Acre',
    unitShort: 'T/Ac',
    mult: 0.4047,
    benchmark: '12 – 18 Tonnes / Acre',
    categoryLabel: 'Fresh Fruit Bunches (केळी घबाड)',
  },
  tomato: {
    unit: 'Tonnes / Acre',
    unitShort: 'T/Ac',
    mult: 0.4047,
    benchmark: '8 – 12 Tonnes / Acre',
    categoryLabel: 'Fresh Vegetable (टोमॅटो तोडणी)',
  },
  potato: {
    unit: 'Tonnes / Acre',
    unitShort: 'T/Ac',
    mult: 0.4047,
    benchmark: '6 – 9 Tonnes / Acre',
    categoryLabel: 'Fresh Tuber (बटाटा काढणी)',
  },
  orange: {
    unit: 'Tonnes / Acre',
    unitShort: 'T/Ac',
    mult: 0.4047,
    benchmark: '4 – 6.5 Tonnes / Acre',
    categoryLabel: 'Fresh Tree Fruit (संत्रे तोडणी)',
  },
  onion: {
    unit: 'Tonnes / Acre',
    unitShort: 'T/Ac',
    mult: 0.4047,
    benchmark: '5 – 8 Tonnes / Acre',
    categoryLabel: 'Fresh Bulb (कांदा)',
  },
  apple: {
    unit: 'Tonnes / Acre',
    unitShort: 'T/Ac',
    mult: 0.4047,
    benchmark: '4 – 7 Tonnes / Acre',
    categoryLabel: 'Fresh Tree Fruit (सफरचंद)',
  },
  grape: {
    unit: 'Tonnes / Acre',
    unitShort: 'T/Ac',
    mult: 0.4047,
    benchmark: '5 – 8 Tonnes / Acre',
    categoryLabel: 'Fresh Table Grapes (द्राक्षे)',
  },
  maize: {
    unit: 'Quintal / Acre',
    unitShort: 'Q/Ac',
    mult: 4.047,
    benchmark: '12 – 18 Quintal / Acre',
    categoryLabel: 'Coarse Grain (मका धान्य)',
  },
  corn: {
    unit: 'Quintal / Acre',
    unitShort: 'Q/Ac',
    mult: 4.047,
    benchmark: '12 – 18 Quintal / Acre',
    categoryLabel: 'Coarse Grain (मका धान्य)',
  },
  rice: {
    unit: 'Quintal / Acre',
    unitShort: 'Q/Ac',
    mult: 4.047,
    benchmark: '10 – 15 Quintal / Acre',
    categoryLabel: 'Paddy Grain (भात / धान)',
  },
  wheat: {
    unit: 'Quintal / Acre',
    unitShort: 'Q/Ac',
    mult: 4.047,
    benchmark: '9 – 13 Quintal / Acre',
    categoryLabel: 'Cereal Grain (गहू उत्पादन)',
  },
  turmeric: {
    unit: 'Quintal / Acre',
    unitShort: 'Q/Ac',
    mult: 4.047,
    benchmark: '8 – 12 Quintal / Acre',
    categoryLabel: 'Cured Dry Rhizome (वाळलेली हळद)',
  },
  cotton: {
    unit: 'Quintal / Acre',
    unitShort: 'Q/Ac',
    mult: 4.047,
    benchmark: '5 – 8 Quintal / Acre',
    categoryLabel: 'Seed Cotton & Lint (कापूस वेचणी)',
  },
  soybean: {
    unit: 'Quintal / Acre',
    unitShort: 'Q/Ac',
    mult: 4.047,
    benchmark: '5 – 7.5 Quintal / Acre',
    categoryLabel: 'Oilseed Grain (सोयाबीन)',
  },
  pepper: {
    unit: 'Quintal / Acre',
    unitShort: 'Q/Ac',
    mult: 4.047,
    benchmark: '8 – 14 Quintal / Acre',
    categoryLabel: 'Fresh Chili (मिरची)',
  },
};

/**
 * Normalises crop string key for agronomic lookup.
 */
function cleanCropKey(crop?: string): string {
  if (!crop) return 'tomato';
  const c = crop.toLowerCase().trim();
  if (c.includes('sugarcane') || c.includes('cane') || c.includes('ऊस')) return 'sugarcane';
  if (c.includes('banana') || c.includes('केळी')) return 'banana';
  if (c.includes('tomato') || c.includes('टोमॅटो')) return 'tomato';
  if (c.includes('potato') || c.includes('बटाटा')) return 'potato';
  if (c.includes('orange') || c.includes('citrus') || c.includes('संत्रे')) return 'orange';
  if (c.includes('onion') || c.includes('कांदा')) return 'onion';
  if (c.includes('grape') || c.includes('द्राक्षे')) return 'grape';
  if (c.includes('apple') || c.includes('सफरचंद')) return 'apple';
  if (c.includes('maize') || c.includes('corn') || c.includes('मका')) return 'maize';
  if (c.includes('rice') || c.includes('paddy') || c.includes('भात') || c.includes('धान')) return 'rice';
  if (c.includes('wheat') || c.includes('गहू')) return 'wheat';
  if (c.includes('turmeric') || c.includes('हळद') || c.includes('haldi')) return 'turmeric';
  if (c.includes('cotton') || c.includes('कापूस') || c.includes('kapas')) return 'cotton';
  if (c.includes('soybean') || c.includes('सोयाबीन')) return 'soybean';
  if (c.includes('pepper') || c.includes('chili') || c.includes('मिरची')) return 'pepper';
  return c;
}

/**
 * Formats net harvest yield into authentic agronomic units.
 */
export function formatAgronomicYield(
  crop: string,
  yield_t_ha?: number | null,
  data?: YieldSourceData | null,
): FormattedYield {
  const y = typeof yield_t_ha === 'number' && !isNaN(yield_t_ha) ? yield_t_ha : 0;
  const key = cleanCropKey(crop);
  const profile = CROP_PROFILES[key] || {
    unit: 'Quintal / Acre' as const,
    unitShort: 'Q/Ac' as const,
    mult: 4.047,
    benchmark: `${(y * 4.047).toFixed(1)} Quintal / Acre`,
    categoryLabel: 'Crop Produce',
  };

  const isBiomass = profile.unit === 'Tonnes / Acre';
  const unit = (data?.commercial_unit as 'Tonnes / Acre' | 'Quintal / Acre') || profile.unit;
  const unitShort: 'T/Ac' | 'Q/Ac' = unit.toLowerCase().startsWith('tonne') ? 'T/Ac' : 'Q/Ac';

  let primaryNum: number;
  if (typeof data?.commercial_yield === 'number' && !isNaN(data.commercial_yield)) {
    primaryNum = data.commercial_yield;
  } else {
    primaryNum = isBiomass ? y * 0.4047 : y * 4.047;
  }

  const primaryValue = primaryNum.toFixed(1);
  const primary = `${primaryValue} ${unit}`;

  // Secondary equivalent:
  // For Tonnes/Acre crops: show Quintal/Acre & metric t/ha equivalent
  // For Quintal/Acre crops: show metric t/ha equivalent
  let secondary: string;
  if (isBiomass) {
    const qAc = (y * 4.047).toFixed(0);
    secondary = `≈ ${qAc} Q/Ac · ${y.toFixed(1)} t/ha`;
  } else {
    secondary = `≈ ${y.toFixed(1)} t/ha`;
  }

  const benchmark = data?.benchmark_range || profile.benchmark;
  const categoryLabel = data?.crop_category_label || data?.yield_category_label || profile.categoryLabel;

  let lossImpactText: string | null = null;
  if (typeof data?.yield_loss_pct === 'number' && data.yield_loss_pct > 0) {
    lossImpactText = `⚠️ ~${data.yield_loss_pct.toFixed(1)}% loss impact`;
  }

  return {
    primary,
    primaryValue,
    unit,
    unitShort,
    secondary,
    benchmark,
    categoryLabel,
    lossImpactText,
    isBiomassCrop: isBiomass,
  };
}
