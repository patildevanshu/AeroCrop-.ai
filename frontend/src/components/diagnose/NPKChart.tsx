import React, { useState, useEffect } from 'react';
import { FertilizerAdvice } from '../../types';
import { useI18n } from '../../context/I18nContext';

interface NPKChartProps {
  fertilizer: FertilizerAdvice;
  crop?: string;
  district?: string;
  diseaseName?: string;
}

interface StageDetail {
  id: string;
  stageNum: number;
  icon: string;
  titleKey: string;
  timingDays: string;
  dasRange: [number, number];
  summary: string;
  instructions: string;
  color: string;
  pPct: number;
  kPct: number;
  nPct: number;
}

export const NPKChart: React.FC<NPKChartProps> = ({
  fertilizer,
  crop = 'Crop',
  district = 'Maharashtra',
}) => {
  const { t } = useI18n();

  // ── Area & Unit State ───────────────────────────────────────────────────────
  const [unit, setUnit] = useState<'acre' | 'guntha' | 'ha'>('acre');
  const [area, setArea] = useState<number>(1.0);
  const [activeTab, setActiveTab] = useState<'timeline' | 'tracker' | 'science' | 'rules'>('timeline');

  // ── Crop Age Tracker State ─────────────────────────────────────────────────
  const [cropAgeDays, setCropAgeDays] = useState<number>(0);

  // ── Completed Stages Persistence ───────────────────────────────────────────
  const cleanCrop = crop.toLowerCase().replace(/[^a-z0-9]/g, '_');
  const storageKey = `aerocrop_fert_done_${cleanCrop}`;
  const [completedStages, setCompletedStages] = useState<Record<string, string>>(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(completedStages));
    } catch (e) {
      console.warn('Could not save stage progress to localStorage', e);
    }
  }, [completedStages, storageKey]);

  const toggleStageDone = (stageId: string) => {
    setCompletedStages((prev) => {
      const copy = { ...prev };
      if (copy[stageId]) {
        delete copy[stageId];
      } else {
        const today = new Date().toLocaleDateString('en-IN', {
          day: '2-digit',
          month: 'short',
        });
        copy[stageId] = today;
      }
      return copy;
    });
  };

  // ── Land Area Multiplier Calculation ───────────────────────────────────────
  // 1 ha = 2.47105 acres = 100 gunthas
  const multiplier = unit === 'ha' ? area : (unit === 'acre' ? area / 2.47105 : area / 100.0);
  const ferts = fertilizer.fertilizers;

  const totalUreaKg = Math.max(0, (ferts.Urea || 0) * multiplier);
  const totalDapKg = Math.max(0, (ferts.DAP || 0) * multiplier);
  const totalMopKg = Math.max(0, (ferts.MOP || 0) * multiplier);

  const totalUreaBags = totalUreaKg / 50.0;
  const totalDapBags = totalDapKg / 50.0;
  const totalMopBags = totalMopKg / 50.0;

  // ── Stage Split Dosages ────────────────────────────────────────────────────
  const stage1UreaKg = totalUreaKg * 0.33;
  const stage2UreaKg = totalUreaKg * 0.33;
  const stage3UreaKg = totalUreaKg * 0.34;

  const stage1DapKg = totalDapKg;
  const stage1MopKg = totalMopKg;

  // ── Crop-Specific Stage Metadata ───────────────────────────────────────────
  const getCropMeta = (): StageDetail[] => {
    const c = crop.toLowerCase();

    if (c.includes('tomato')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🌱',
          titleKey: 'STAGE 1: BASAL (लावणीच्या वेळी)',
          timingDays: 'Day 0 (Transplanting)',
          dasRange: [0, 15],
          summary: 'Full Phosphorus & Potash + 1/3rd Nitrogen in transplant furrow',
          instructions: 'Band-place DAP, MOP, and 1/3rd Urea 5cm below the root zone. Supplement with 5 kg/acre Zinc Sulphate for vigorous root branching.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 100,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌿',
          titleKey: 'STAGE 2: VEGETATIVE (शाकीय वाढ व फांद्या)',
          timingDays: '25–30 DAT (Days After Transplanting)',
          dasRange: [16, 45],
          summary: '1st Top-Dressing for stem vigor & lateral branching',
          instructions: 'Side-dress 1/3rd Urea 10 cm from the plant base along the furrow or raised bed before tying/staking. Follow immediately with light drip or flood irrigation.',
          color: '#10b981',
          pPct: 0,
          kPct: 0,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🍅',
          titleKey: 'STAGE 3: FLOWERING & FRUIT BULKING (फुलोरा व फळ फुगवण)',
          timingDays: '50–60 DAT',
          dasRange: [46, 120],
          summary: '2nd Top-Dressing for heavy fruit set & uniform sizing',
          instructions: 'Apply the remaining 1/3rd Urea to sustain multi-tier fruit clusters and prevent premature flower drop. Maintain consistent soil moisture to avert blossom end rot.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 0,
          nPct: 34,
        },
      ];
    }

    if (c.includes('potato')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🥔',
          titleKey: 'STAGE 1: BASAL (बटाटा लागवड वेळ)',
          timingDays: 'Day 0 (Planting)',
          dasRange: [0, 15],
          summary: 'Full P & K + 1/3rd Nitrogen 5cm below seed tubers',
          instructions: 'Apply full DAP and MOP with 1/3rd Urea in bands 5 cm to the side and below seed tubers to stimulate rapid sprout emergence and stolon formation.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 100,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌿',
          titleKey: 'STAGE 2: EARTHING-UP (मातीची भर लावणे)',
          timingDays: '30–35 DAS',
          dasRange: [16, 45],
          summary: '1st Top-Dressing right before mechanical earthing-up',
          instructions: 'Side-dress 1/3rd Urea along the ridge immediately prior to earthing-up (मातीची भर). Earthing-up covers the fertilizer, preventing volatilization and tuber greening.',
          color: '#10b981',
          pPct: 0,
          kPct: 0,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🌸',
          titleKey: 'STAGE 3: TUBER BULKING (कंद फुगवण अवस्था)',
          timingDays: '55–65 DAS',
          dasRange: [46, 100],
          summary: '2nd Top-Dressing to maximize tuber starch & size grade',
          instructions: 'Apply remaining 1/3rd Urea to fuel maximum tuber expansion. Avoid excess irrigation during this stage to prevent lenticel enlargement.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 0,
          nPct: 34,
        },
      ];
    }

    if (c.includes('maize') || c.includes('corn')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🌽',
          titleKey: 'STAGE 1: BASAL (पेरणीच्या वेळी)',
          timingDays: 'Day 0 (Sowing)',
          dasRange: [0, 15],
          summary: 'Full P & K + 1/3rd Nitrogen drilled at sowing',
          instructions: 'Apply full DAP & MOP with 1/3rd Urea using a seed-cum-fertilizer drill. Place 5 cm away from seeds to establish a deep taproot system.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 100,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌿',
          titleKey: 'STAGE 2: KNEE-HIGH STAGE (गुडघाभर वाढ अवस्था)',
          timingDays: '30–35 DAS (V6–V8 Stage)',
          dasRange: [16, 45],
          summary: '1st Top-Dressing at peak stem elongation',
          instructions: 'Side-dress 1/3rd Urea along crop rows followed by inter-cultivation weeding (कोळपणी). Irrigate immediately to accelerate nitrogen intake.',
          color: '#10b981',
          pPct: 0,
          kPct: 0,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🌾',
          titleKey: 'STAGE 3: TASSELING & SILKING (तुरा व दाणे भरणे)',
          timingDays: '55–65 DAS (Silk Emergence)',
          dasRange: [46, 110],
          summary: '2nd Top-Dressing for dense cob grain filling',
          instructions: 'Apply remaining 1/3rd Urea right before silk emergence. This critical dose prevents cob tip barrenness and ensures maximum test weight (1000-grain weight).',
          color: '#f59e0b',
          pPct: 0,
          kPct: 0,
          nPct: 34,
        },
      ];
    }

    if (c.includes('grape')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🍇',
          titleKey: 'STAGE 1: FOUNDATION PRUNING (छाटणीनंतर / डोळे फुटणे)',
          timingDays: 'Day 0 (Post-Pruning)',
          dasRange: [0, 20],
          summary: 'Full P & K + 1/3rd Nitrogen in vine root perimeter',
          instructions: 'Incorporate DAP and MOP in a shallow ring trench around vine basin along the drip perimeter. Boosts active feeder root revival.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 100,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌿',
          titleKey: 'STAGE 2: SHOOT GROWTH & PRE-BLOOM (शाकीय वाढ व फुलोरापूर्व)',
          timingDays: '35–45 Days After Pruning',
          dasRange: [21, 55],
          summary: '1st Top-Dressing for cluster elongation',
          instructions: 'Apply 1/3rd Urea via fertigation to support rapid shoot canopy coverage and flower inflorescence development.',
          color: '#10b981',
          pPct: 0,
          kPct: 0,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🍇',
          titleKey: 'STAGE 3: BERRY SIZING & VERAISON (मणी फुगवण व पक्वता)',
          timingDays: '70–85 Days After Pruning',
          dasRange: [56, 130],
          summary: '2nd Top-Dressing for uniform berry size & sugar accumulation',
          instructions: 'Apply remaining Nitrogen along with potassium sulfate to optimize berry firmness, prevent cracking, and maximize Brix degrees.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 0,
          nPct: 34,
        },
      ];
    }

    if (c.includes('soybean')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🌱',
          titleKey: 'STAGE 1: BASAL (पेरणीच्या वेळी)',
          timingDays: 'Day 0 (Sowing)',
          dasRange: [0, 15],
          summary: 'Full P & K + starter Nitrogen for nodulation',
          instructions: 'Drill DAP & MOP with starter Urea at sowing. Combine with Rhizobium and PSB bio-fertilizer seed inoculation.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 100,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌿',
          titleKey: 'STAGE 2: ACTIVE BRANCHING (शाकीय वाढ व फांद्या)',
          timingDays: '25–30 DAS',
          dasRange: [16, 45],
          summary: '1st Top-Dressing to stimulate vegetative nodes',
          instructions: 'Top-dress 1/3rd Urea if root nodule development is moderate. Ensure field has good soil moisture.',
          color: '#10b981',
          pPct: 0,
          kPct: 0,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🌸',
          titleKey: 'STAGE 3: POD FORMATION & FILLING (शेंगा भरणे अवस्था)',
          timingDays: '50–60 DAS',
          dasRange: [46, 95],
          summary: '2nd Top-Dressing to maximize seed protein & grain size',
          instructions: 'Apply remaining Urea to nourish seed development inside pods and prevent premature leaf yellowing.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 0,
          nPct: 34,
        },
      ];
    }

    if (c.includes('cotton')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🌱',
          titleKey: 'STAGE 1: BASAL (पेरणीच्या वेळी)',
          timingDays: 'Day 0 (Sowing / Dibbling)',
          dasRange: [0, 20],
          summary: 'Full P & K + 1/3rd Nitrogen placed in dibbled hills',
          instructions: 'Deep band placement of DAP & MOP with 1/3rd Urea in the planting row 7 cm away from seeds.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 100,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌿',
          titleKey: 'STAGE 2: SQUARE FORMATION (पात्या लागण्याची अवस्था)',
          timingDays: '35–45 DAS',
          dasRange: [21, 55],
          summary: '1st Top-Dressing for sympodial fruiting branches',
          instructions: 'Side-dress 1/3rd Urea 15 cm from the main stem after inter-cultivation weeding. Follow with irrigation or rain.',
          color: '#10b981',
          pPct: 0,
          kPct: 0,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🌸',
          titleKey: 'STAGE 3: PEAK FLOWERING & BOLL DEVELOPMENT (फुलोरा व बोंड वाढ)',
          timingDays: '65–75 DAS',
          dasRange: [56, 120],
          summary: '2nd Top-Dressing to maximize boll weight & fiber quality',
          instructions: 'Top-dress remaining 1/3rd Urea to prevent square/boll shedding and sustain prolonged boll retention.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 0,
          nPct: 34,
        },
      ];
    }

    if (c.includes('banana')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🍌',
          titleKey: 'STAGE 1: PLANTING & BASAL (केळी लागवड व बेसल डोस)',
          timingDays: 'Day 0–30 (Planting)',
          dasRange: [0, 45],
          summary: 'Full Phosphorus + 1/3rd Nitrogen & Potash in planting pit ring',
          instructions: 'Apply DAP, MOP, and Urea in circular bands 30 cm away from pseudostem. Add 10 kg FYM per pit to prevent rhizome rot.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 33,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌿',
          titleKey: 'STAGE 2: RAPID SHOOTING & DESUCKERING (शाकीय वाढ व पिल्ले काढणे)',
          timingDays: '75–90 DAP (Days After Planting)',
          dasRange: [46, 120],
          summary: '1st Top-Dressing for broad lamina and robust pseudostem girth',
          instructions: 'Side-dress 1/3rd Urea and 1/3rd MOP around drip circle. Concurrently remove unwanted sword suckers to direct nutrients into main plant.',
          color: '#10b981',
          pPct: 0,
          kPct: 33,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🍌',
          titleKey: 'STAGE 3: BUNCH EMERGENCE & FINGER BULKING (केळफूल व घड फुगवण)',
          timingDays: '150–180 DAP (Shooting Stage)',
          dasRange: [121, 300],
          summary: '2nd Top-Dressing for heavy hand weight & optimum bunch grade',
          instructions: 'Apply remaining 1/3rd Urea and 1/3rd MOP. Spray 0.5% Potassium Schoenite or SOP post-shooting to maximize finger size and sweetness.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 34,
          nPct: 34,
        },
      ];
    }

    if (c.includes('turmeric') || c.includes('haldi')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🌿',
          titleKey: 'STAGE 1: BASAL (हळद लागवड वेळ)',
          timingDays: 'Day 0 (Rhizome Planting)',
          dasRange: [0, 30],
          summary: 'Full P + 1/3rd Nitrogen & Potash under raised beds',
          instructions: 'Apply full DAP, 1/3rd MOP, and 1/3rd Urea before laying drip lines and mulch. Incorporate Trichoderma viride enriched FYM.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 33,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌱',
          titleKey: 'STAGE 2: TILLERING & RHIZOME INITIATION (फुटवे व गड्डा फुटणे)',
          timingDays: '45–60 DAS',
          dasRange: [31, 80],
          summary: '1st Top-Dressing right before 1st earthing-up (मातीची भर)',
          instructions: 'Apply 1/3rd Urea and 1/3rd MOP on raised beds before covering with soil. Promotes vigorous tiller formation and daughter rhizome nodes.',
          color: '#10b981',
          pPct: 0,
          kPct: 33,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🪵',
          titleKey: 'STAGE 3: RHIZOME BULKING & CURCUMIN ACCUMULATION (गड्डा फुगवण)',
          timingDays: '90–105 DAS',
          dasRange: [81, 210],
          summary: '2nd Top-Dressing for dense rhizome density & curcumin content',
          instructions: 'Apply final 1/3rd Urea and 1/3rd MOP. Maintain optimal soil moisture without waterlogging to avert Pythium rhizome rot.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 34,
          nPct: 34,
        },
      ];
    }

    if (c.includes('sugarcane')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🎋',
          titleKey: 'STAGE 1: BASAL (ऊस लागवड वेळ)',
          timingDays: 'Day 0 (Planting / Furrow Placement)',
          dasRange: [0, 35],
          summary: 'Full P + 1/3rd N & K drilled in planting furrows',
          instructions: 'Place full DAP, 1/3rd MOP, and 1/3rd Urea in the furrow bottom below setts. Supplement with 10 kg/acre Zinc Sulphate.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 33,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌿',
          titleKey: 'STAGE 2: FORMATIVE & TILLERING (फुटवे अवस्था व बाळबांधणी)',
          timingDays: '60–75 DAP',
          dasRange: [36, 100],
          summary: '1st Top-Dressing at formative tiller phase',
          instructions: 'Side-dress 1/3rd Urea and 1/3rd MOP along rows followed by partial earthing-up (बाळबांधणी) and irrigation.',
          color: '#10b981',
          pPct: 0,
          kPct: 33,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🎋',
          titleKey: 'STAGE 3: GRAND GROWTH & FINAL EARTHING UP (मोठी बांधणी)',
          timingDays: '120–135 DAP',
          dasRange: [101, 330],
          summary: 'Final Top-Dressing before canopy closes',
          instructions: 'Apply remaining 1/3rd Urea and 1/3rd MOP before heavy earthing-up (मोठी बांधणी). Prevents cane lodging and fuels high sucrose %.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 34,
          nPct: 34,
        },
      ];
    }

    if (c.includes('onion')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🧅',
          titleKey: 'STAGE 1: BASAL (कांदा पुनर्लागवड वेळ)',
          timingDays: 'Day 0 (Transplanting)',
          dasRange: [0, 20],
          summary: 'Full P & K + 50% Nitrogen incorporated in flat/raised bed',
          instructions: 'Broadcast and incorporate full DAP, full MOP, and 50% Urea into soil before transplanting seedlings. Ensure good organic matter.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 100,
          nPct: 50,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌿',
          titleKey: 'STAGE 2: VEGETATIVE VIGOR (शाकीय वाढ व मान जाड होणे)',
          timingDays: '30 DAT (Days After Transplanting)',
          dasRange: [21, 45],
          summary: '1st Top-Dressing for strong neck and leaf canopy',
          instructions: 'Side-dress 25% Urea along rows followed immediately by light irrigation. Avoid excessive water stagnancy.',
          color: '#10b981',
          pPct: 0,
          kPct: 0,
          nPct: 25,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🧅',
          titleKey: 'STAGE 3: BULB BULKING & SIZING (कांदा फुगवण अवस्था)',
          timingDays: '45–60 DAT',
          dasRange: [46, 110],
          summary: 'Final Top-Dressing for compact, high-grade bulbs',
          instructions: 'Apply remaining 25% Urea. Stop nitrogen after 60 DAT to prevent thick neck onions (डेंगळे) and enhance storage longevity.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 0,
          nPct: 25,
        },
      ];
    }

    if (c.includes('rice') || c.includes('paddy')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🌾',
          titleKey: 'STAGE 1: BASAL (भात पुनर्लागवड वेळ)',
          timingDays: 'Day 0 (Transplanting)',
          dasRange: [0, 15],
          summary: 'Full P + 50% K + 1/3rd Nitrogen in puddled soil',
          instructions: 'Incorporate full DAP, half MOP, and 1/3rd Urea into the final puddle before transplanting 21-day old seedlings.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 50,
          nPct: 33,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌱',
          titleKey: 'STAGE 2: ACTIVE TILLERING (फुटवे फुटणे)',
          timingDays: '20–25 DAT',
          dasRange: [16, 35],
          summary: '1st Top-Dressing for maximum productive tillers',
          instructions: 'Broadcast 1/3rd Urea in standing water (2-3 cm depth) after hand weeding or cono-weeder operation.',
          color: '#10b981',
          pPct: 0,
          kPct: 0,
          nPct: 33,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🌾',
          titleKey: 'STAGE 3: PANICLE INITIATION (पोंगा / लोंबी भरण्याची अवस्था)',
          timingDays: '40–45 DAT',
          dasRange: [36, 120],
          summary: '2nd Top-Dressing for long grain panicles and filled spikelets',
          instructions: 'Apply remaining 1/3rd Urea and remaining 50% MOP. Potash here ensures bold grains and disease resistance against blast.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 50,
          nPct: 34,
        },
      ];
    }

    if (c.includes('wheat')) {
      return [
        {
          id: 'stage-1',
          stageNum: 1,
          icon: '🌾',
          titleKey: 'STAGE 1: BASAL (गहू पेरणीच्या वेळी)',
          timingDays: 'Day 0 (Sowing)',
          dasRange: [0, 15],
          summary: 'Full P & K + 50% Nitrogen drilled with seed',
          instructions: 'Drill 100% DAP and 100% MOP with 50% Urea at sowing depth 5 cm using seed-cum-fertilizer drill.',
          color: '#38bdf8',
          pPct: 100,
          kPct: 100,
          nPct: 50,
        },
        {
          id: 'stage-2',
          stageNum: 2,
          icon: '🌱',
          titleKey: 'STAGE 2: CROWN ROOT INITIATION - CRI (मुकुट मुळे फुटणे)',
          timingDays: '20–25 DAS (1st Irrigation)',
          dasRange: [16, 35],
          summary: '1st Top-Dressing at critical crown root formation',
          instructions: 'Top-dress 25% Urea immediately prior to the first irrigation (मुकुट मुळे फुटण्याची वेळ). Most critical stage for yield.',
          color: '#10b981',
          pPct: 0,
          kPct: 0,
          nPct: 25,
        },
        {
          id: 'stage-3',
          stageNum: 3,
          icon: '🌾',
          titleKey: 'STAGE 3: JOINTING & BOOTING (कांडी अवस्था व लोंबी भरणे)',
          timingDays: '40–45 DAS (2nd/3rd Irrigation)',
          dasRange: [36, 115],
          summary: 'Final Top-Dressing for spikelet fertility & grain count',
          instructions: 'Apply remaining 25% Urea before jointing stage irrigation to avert spikelet abortion and boost test weight.',
          color: '#f59e0b',
          pPct: 0,
          kPct: 0,
          nPct: 25,
        },
      ];
    }

    // Generic standard 3-stage ICAR schedule for all other crops
    return [
      {
        id: 'stage-1',
        stageNum: 1,
        icon: '🌱',
        titleKey: 'STAGE 1: BASAL (पेरणी / लावणीच्या वेळी)',
        timingDays: 'Day 0 (Sowing / Planting)',
        dasRange: [0, 15],
        summary: 'Full Phosphorus & Potash + 1/3rd Nitrogen',
        instructions: 'Apply 100% DAP and 100% MOP with 1/3rd Urea directly into the root furrow or transplant hole to stimulate deep root establishment.',
        color: '#38bdf8',
        pPct: 100,
        kPct: 100,
        nPct: 33,
      },
      {
        id: 'stage-2',
        stageNum: 2,
        icon: '🌿',
        titleKey: 'STAGE 2: VEGETATIVE (वाढीची अवस्था)',
        timingDays: '30–35 DAS (Days After Sowing)',
        dasRange: [16, 45],
        summary: '1st Top-Dressing for stem vigor & canopy branching',
        instructions: 'Side-dress 1/3rd Urea along crop rows followed immediately by light irrigation or apply during moist soil conditions.',
        color: '#10b981',
        pPct: 0,
        kPct: 0,
        nPct: 33,
      },
      {
        id: 'stage-3',
        stageNum: 3,
        icon: '🌸',
        titleKey: 'STAGE 3: FLOWERING & FRUIT BULKING (फुलोरा व फळधारणा)',
        timingDays: '60–65 DAS',
        dasRange: [46, 120],
        summary: '2nd Top-Dressing to maximize harvest yield & grain filling',
        instructions: 'Top-dress remaining 1/3rd Urea to nourish blooming, fruit set, and grain filling. Helps prevent early foliage senescence.',
        color: '#f59e0b',
        pPct: 0,
        kPct: 0,
        nPct: 34,
      },
    ];
  };

  const stages = getCropMeta();

  // Determine current active stage based on cropAgeDays
  const activeStage = stages.find(
    (s) => cropAgeDays >= s.dasRange[0] && cropAgeDays <= s.dasRange[1]
  ) || stages[0];

  // ── Share Schedule to WhatsApp ─────────────────────────────────────────────
  const handleShareWhatsApp = () => {
    const text = `*AeroCrop.ai — ICAR Fertilizer Application Schedule* 📅
🌱 *Crop*: ${crop}
📍 *District*: ${district}
📐 *Plot Size*: ${area} ${unit}

🌱 *STAGE 1: BASAL (${stages[0].timingDays})*
• DAP: ${stage1DapKg.toFixed(1)} kg (${(stage1DapKg / 50).toFixed(1)} bags)
• MOP: ${stage1MopKg.toFixed(1)} kg (${(stage1MopKg / 50).toFixed(1)} bags)
• Urea: ${stage1UreaKg.toFixed(1)} kg (${(stage1UreaKg / 50).toFixed(1)} bags)
ℹ️ Method: ${stages[0].instructions}

🌿 *STAGE 2: VEGETATIVE (${stages[1].timingDays})*
• Urea: ${stage2UreaKg.toFixed(1)} kg (${(stage2UreaKg / 50).toFixed(1)} bags)
ℹ️ Method: ${stages[1].instructions}

🌸 *STAGE 3: FLOWERING & BULKING (${stages[2].timingDays})*
• Urea: ${stage3UreaKg.toFixed(1)} kg (${(stage3UreaKg / 50).toFixed(1)} bags)
ℹ️ Method: ${stages[2].instructions}

💰 *Total Input Quantity*:
• Urea: ${totalUreaKg.toFixed(1)} kg (${Math.ceil(totalUreaBags)} bags)
• DAP: ${totalDapKg.toFixed(1)} kg (${Math.ceil(totalDapBags)} bags)
• MOP: ${totalMopKg.toFixed(1)} kg (${Math.ceil(totalMopBags)} bags)

💡 *ICAR Rule*: Splitting nitrogen prevents up to 35% fertilizer leaching loss.
Generated via AeroCrop.ai Precision Agriculture Platform`;

    const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
    window.open(url, '_blank');
  };

  // ── Print Schedule ─────────────────────────────────────────────────────────
  const handlePrint = () => {
    window.print();
  };

  // ── Download .ics Calendar Reminder ─────────────────────────────────────────
  const handleDownloadCalendar = () => {
    const now = new Date();
    const formatDateForIcs = (d: Date) =>
      d.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';

    const stage2Date = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
    const stage3Date = new Date(now.getTime() + 60 * 24 * 60 * 60 * 1000);

    const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AeroCrop.ai//Farmer Nutrient Schedule//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:aerocrop-stage2-${Date.now()}@aerocrop.ai
DTSTAMP:${formatDateForIcs(now)}
DTSTART:${formatDateForIcs(stage2Date)}
DTEND:${formatDateForIcs(new Date(stage2Date.getTime() + 3600000))}
SUMMARY:AeroCrop: Stage 2 Urea Top-Dressing for ${crop}
DESCRIPTION:Apply ${stage2UreaKg.toFixed(1)} kg Urea (${(stage2UreaKg / 50).toFixed(1)} bags) for ${crop} (${area} ${unit}). Side-dress along rows followed by irrigation.
STATUS:CONFIRMED
END:VEVENT
BEGIN:VEVENT
UID:aerocrop-stage3-${Date.now()}@aerocrop.ai
DTSTAMP:${formatDateForIcs(now)}
DTSTART:${formatDateForIcs(stage3Date)}
DTEND:${formatDateForIcs(new Date(stage3Date.getTime() + 3600000))}
SUMMARY:AeroCrop: Stage 3 Urea Top-Dressing for ${crop}
DESCRIPTION:Apply ${stage3UreaKg.toFixed(1)} kg Urea (${(stage3UreaKg / 50).toFixed(1)} bags) for ${crop} (${area} ${unit}) during flowering/bulking.
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR`;

    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.setAttribute('download', `AeroCrop_${crop}_Fertilizer_Schedule.ics`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="card glass chart-card fert-schedule-container" style={{ gridColumn: '1 / -1', marginTop: '1.25rem' }}>
      
      {/* ── Top Header & Interactive Area Controls ───────────────────────── */}
      <div className="fert-sched-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <h2 className="card-title" style={{ margin: 0, fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span aria-hidden="true">📅</span>
              <span>{t('fertilizer_schedule')}</span>
            </h2>
            <span
              style={{
                fontSize: '0.78rem',
                color: '#10b981',
                background: 'rgba(16,185,129,0.12)',
                padding: '2px 8px',
                borderRadius: '6px',
                border: '1px solid rgba(16,185,129,0.25)',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <span className="fert-pulse" />
              <span>{t('fert_icar_certified')}</span>
            </span>
            <span
              style={{
                fontSize: '0.78rem',
                color: '#38bdf8',
                background: 'rgba(56,189,248,0.12)',
                padding: '2px 8px',
                borderRadius: '6px',
                border: '1px solid rgba(56,189,248,0.25)',
              }}
            >
              🌱 {crop} &bull; {district}
            </span>
          </div>
          <p style={{ margin: '0.4rem 0 0 0', fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
            {t('fert_schedule_subtitle')}
          </p>
        </div>

        {/* Land Area & Unit Controls */}
        <div className="fert-sched-controls">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>📐 {t('land_size')}</span>
          <input
            type="number"
            min="0.1"
            step="0.5"
            value={area}
            onChange={(e) => setArea(Math.max(0.1, parseFloat(e.target.value) || 0.1))}
            style={{
              width: '56px',
              padding: '0.25rem 0.4rem',
              borderRadius: '6px',
              border: '1px solid rgba(140,195,165,0.4)',
              background: '#fff',
              color: 'var(--text-primary)',
              fontSize: '0.85rem',
            }}
          />
          <select
            value={unit}
            onChange={(e) => setUnit(e.target.value as any)}
            style={{
              padding: '0.25rem 0.5rem',
              borderRadius: '6px',
              border: '1px solid rgba(140,195,165,0.4)',
              background: '#fff',
              color: 'var(--text-primary)',
              fontSize: '0.85rem',
            }}
          >
            <option value="acre">{t('unit_acre')}</option>
            <option value="guntha">{t('unit_guntha')}</option>
            <option value="ha">{t('unit_ha')}</option>
          </select>

          {/* Quick Presets */}
          <div style={{ display: 'flex', gap: '4px' }}>
            {[0.5, 1.0, 2.0, 5.0].map((preset) => (
              <button
                key={preset}
                type="button"
                className={`fert-preset-btn ${area === preset && unit === 'acre' ? 'active' : ''}`}
                onClick={() => {
                  setArea(preset);
                  setUnit('acre');
                }}
              >
                {preset} Ac
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Sub Navigation Tabs ─────────────────────────────────────────────── */}
      <div className="fert-tab-nav">
        <button
          type="button"
          className={`fert-tab-btn ${activeTab === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveTab('timeline')}
        >
          <span>🗓️</span>
          <span>Growth Stage Timeline (वाढीचे टप्पे)</span>
        </button>

        <button
          type="button"
          className={`fert-tab-btn ${activeTab === 'tracker' ? 'active' : ''}`}
          onClick={() => setActiveTab('tracker')}
        >
          <span>⏱️</span>
          <span>{t('fert_crop_age_label')}</span>
        </button>

        <button
          type="button"
          className={`fert-tab-btn ${activeTab === 'science' ? 'active' : ''}`}
          onClick={() => setActiveTab('science')}
        >
          <span>🧪</span>
          <span>Nutrient Split Science (नत्र विभाजन का?)</span>
        </button>

        <button
          type="button"
          className={`fert-tab-btn ${activeTab === 'rules' ? 'active' : ''}`}
          onClick={() => setActiveTab('rules')}
        >
          <span>📜</span>
          <span>{t('fert_rules_title')}</span>
        </button>
      </div>

      {/* ── Tab 2: Interactive Crop Age Tracker ────────────────────────────── */}
      {activeTab === 'tracker' && (
        <div
          style={{
            background: 'rgba(240,253,244,0.7)',
            border: '1px solid rgba(6,182,212,0.2)',
            borderRadius: '10px',
            padding: '1rem',
            marginBottom: '1.25rem',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <label style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              🌱 {t('fert_crop_age_label')}: <strong style={{ color: 'var(--accent-cyan)', fontSize: '1.05rem' }}>{cropAgeDays} Days (दिवस)</strong>
            </label>
            <div style={{ display: 'flex', gap: '6px' }}>
              {[0, 15, 30, 45, 60, 75].map((d) => (
                <button
                  key={d}
                  type="button"
                  className="fert-preset-btn"
                  onClick={() => setCropAgeDays(d)}
                >
                  {d} DAS
                </button>
              ))}
            </div>
          </div>

          <input
            type="range"
            min="0"
            max="90"
            step="1"
            value={cropAgeDays}
            onChange={(e) => setCropAgeDays(parseInt(e.target.value, 10))}
            style={{ width: '100%', accentColor: '#06b6d4', cursor: 'pointer' }}
          />

          <div
            style={{
              marginTop: '0.85rem',
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              background: 'rgba(16,185,129,0.12)',
              border: '1px solid rgba(16,185,129,0.3)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
            }}
          >
            <span style={{ fontSize: '1.5rem' }}>{activeStage.icon}</span>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#15803d', textTransform: 'uppercase' }}>
                📍 {t('active_stage_now', 'Active Stage Now')}: {activeStage.titleKey} ({activeStage.timingDays})
              </div>
              <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                {t('fert_active_stage_alert')}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 3: Nutrient Split Science ─────────────────────────────────── */}
      {activeTab === 'science' && (
        <div
          style={{
            background: 'rgba(240,253,244,0.7)',
            border: '1px solid rgba(140,195,165,0.3)',
            borderRadius: '10px',
            padding: '1.1rem',
            marginBottom: '1.25rem',
          }}
        >
          <h3 style={{ fontSize: '0.95rem', color: '#0369a1', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span>🧪</span> Why Split Nitrogen into 3 Stages? (नत्र विभाजन का आवश्यक आहे?)
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '0.85rem' }}>
            Nitrate (NO₃⁻) is highly mobile in soil. If the entire Nitrogen dose is dumped during sowing, up to <strong>40% of it is lost</strong> through rainwater leaching below the root zone and volatilization as ammonia gas. ICAR research proves that splitting Nitrogen matches the plant&apos;s biological uptake curve, increasing nitrogen-use efficiency (NUE) by 25–35%.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
            <div style={{ background: 'rgba(255,255,255,0.9)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.8rem', color: '#0369a1', fontWeight: 600 }}>🟡 Nitrogen (N) Distribution</div>
              <div style={{ height: '8px', background: 'rgba(140,195,165,0.2)', borderRadius: '4px', margin: '6px 0', overflow: 'hidden', display: 'flex' }}>
                <div style={{ width: '33%', background: '#0284c7' }} title="Stage 1: 33%" />
                <div style={{ width: '33%', background: '#15803d' }} title="Stage 2: 33%" />
                <div style={{ width: '34%', background: '#d97706' }} title="Stage 3: 34%" />
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>33% Basal &bull; 33% Veg &bull; 34% Flower</div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.9)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.8rem', color: '#15803d', fontWeight: 600 }}>🟤 Phosphorus (P₂O₅) Distribution</div>
              <div style={{ height: '8px', background: 'rgba(140,195,165,0.2)', borderRadius: '4px', margin: '6px 0', overflow: 'hidden' }}>
                <div style={{ width: '100%', background: '#15803d' }} title="100% at Basal" />
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>100% Basal (Immobile in soil, builds roots)</div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.9)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.8rem', color: '#d97706', fontWeight: 600 }}>🔴 Potassium (K₂O) Distribution</div>
              <div style={{ height: '8px', background: 'rgba(140,195,165,0.2)', borderRadius: '4px', margin: '6px 0', overflow: 'hidden' }}>
                <div style={{ width: '100%', background: '#d97706' }} title="100% at Basal" />
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>100% Basal (Aids water regulation & disease immunity)</div>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 4: ICAR Golden Rules ───────────────────────────────────────── */}
      {activeTab === 'rules' && (
        <div
          style={{
            background: 'rgba(240,253,244,0.7)',
            border: '1px solid rgba(140,195,165,0.3)',
            borderRadius: '10px',
            padding: '1.1rem',
            marginBottom: '1.25rem',
          }}
        >
          <h3 style={{ fontSize: '0.95rem', color: '#15803d', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span>📜</span> {t('fert_rules_title')}
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '0.75rem' }}>
            <div style={{ background: 'rgba(255,255,255,0.9)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#0369a1' }}>💧 Soil Moisture Rule</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                Never apply dry granular Urea on dry soil or in baking afternoon heat. Always broadcast in moist soil and follow with light irrigation.
              </div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.9)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#15803d' }}>🌿 Neem-Coated Urea (NCU)</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                Always insist on Neem-Coated Urea (NCU). Neem oil inhibits nitrifying bacteria, resulting in a 15–20% boost in grain uptake.
              </div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.9)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#d97706' }}>🌾 Inter-Cultivation &amp; Weeding</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                Perform weeding (खुरपणी) 2–3 days prior to top-dressing so fertilizers nourish your crop rather than opportunistic weeds.
              </div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.9)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.82rem', fontWeight: 600, color: '#b91c1c' }}>🚜 Band Placement vs Broadcast</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                Placing fertilizers 5–7 cm below the soil surface delivers 30% higher nutrient absorption than broad surface broadcasting.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── 3-Stage Connected Timeline Track ──────────────────────────────── */}
      <div style={{ position: 'relative', marginBottom: '1rem' }}>
        
        {/* Progress Tracker Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'relative',
            padding: '0 1rem',
            marginBottom: '1rem',
          }}
        >
          {/* Connector Line */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '10%',
              right: '10%',
              height: '2px',
              background: 'rgba(140,195,165,0.3)',
              zIndex: 0,
            }}
          />

          {stages.map((stg) => {
            const isCompleted = !!completedStages[stg.id];
            const isCurrent = activeStage.id === stg.id;

            return (
              <div
                key={stg.id}
                style={{
                  zIndex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  cursor: 'pointer',
                }}
                onClick={() => setCropAgeDays(stg.dasRange[0])}
              >
                <div
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    background: isCompleted
                      ? '#10b981'
                      : isCurrent
                      ? '#0284c7'
                      : '#ffffff',
                    border: `2px solid ${isCompleted ? '#10b981' : isCurrent ? '#0284c7' : 'rgba(140,195,165,0.6)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.9rem',
                    color: isCompleted || isCurrent ? '#ffffff' : 'var(--text-primary)',
                    fontWeight: 700,
                    boxShadow: isCurrent ? '0 0 10px rgba(2,132,199,0.4)' : 'none',
                    transition: 'all 0.2s ease',
                  }}
                >
                  {isCompleted ? '✓' : stg.stageNum}
                </div>
                <span style={{ fontSize: '0.72rem', color: isCurrent ? '#0284c7' : 'var(--text-secondary)', marginTop: '4px', fontWeight: isCurrent ? 700 : 500 }}>
                  {stg.timingDays.split(' ')[0]} {stg.timingDays.split(' ')[1] || ''}
                </span>
              </div>
            );
          })}
        </div>

        {/* Stage Cards Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: '1rem' }}>
          
          {/* ── STAGE 1 CARD ── */}
          <div className={`fert-stage-card ${activeStage.id === 'stage-1' ? 'is-active' : ''} ${completedStages['stage-1'] ? 'is-completed' : ''}`} style={{ borderLeft: `4px solid ${stages[0].color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
              <div>
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: stages[0].color, display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>{stages[0].icon}</span>
                  <span>{stages[0].titleKey}</span>
                </span>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>{stages[0].timingDays}</span>
              </div>

              {/* Mark Done Button */}
              <button
                type="button"
                className="btn btn-sm"
                onClick={() => toggleStageDone('stage-1')}
                style={{
                  fontSize: '0.74rem',
                  padding: '3px 8px',
                  background: completedStages['stage-1'] ? 'rgba(16,185,129,0.15)' : 'rgba(255,255,255,0.8)',
                  border: `1px solid ${completedStages['stage-1'] ? '#10b981' : 'rgba(140,195,165,0.5)'}`,
                  color: completedStages['stage-1'] ? '#15803d' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  borderRadius: '6px',
                  fontWeight: 600,
                }}
              >
                {completedStages['stage-1'] ? `✓ Done (${completedStages['stage-1']})` : `[ ] ${t('fert_mark_done')}`}
              </button>
            </div>

            <p style={{ margin: '0.2rem 0 0.5rem 0', fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {stages[0].summary}
            </p>

            {/* Dosages Pill Container */}
            <div style={{ background: 'rgba(240,253,244,0.7)', padding: '0.65rem 0.8rem', borderRadius: '8px', fontSize: '0.82rem', display: 'flex', flexDirection: 'column', gap: '5px', margin: '0.4rem 0', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>🟤 <strong>DAP (18-46-0):</strong></span>
                <strong style={{ color: '#0369a1' }}>
                  {stage1DapKg.toFixed(1)} kg <span style={{ fontSize: '0.74rem', fontWeight: 400, color: 'var(--text-muted)' }}>({(stage1DapKg / 50).toFixed(1)} bags)</span>
                </strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>🔴 <strong>MOP (60% K):</strong></span>
                <strong style={{ color: '#d97706' }}>
                  {stage1MopKg.toFixed(1)} kg <span style={{ fontSize: '0.74rem', fontWeight: 400, color: 'var(--text-muted)' }}>({(stage1MopKg / 50).toFixed(1)} bags)</span>
                </strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>🟡 <strong>Urea (46% N):</strong></span>
                <strong style={{ color: '#15803d' }}>
                  {stage1UreaKg.toFixed(1)} kg <span style={{ fontSize: '0.74rem', fontWeight: 400, color: 'var(--text-muted)' }}>({(stage1UreaKg / 50).toFixed(1)} bags)</span>
                </strong>
              </div>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', borderTop: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                <strong>{t('fert_method')}:</strong> {stages[0].instructions}
              </div>
            </div>
          </div>

          {/* ── STAGE 2 CARD ── */}
          <div className={`fert-stage-card ${activeStage.id === 'stage-2' ? 'is-active' : ''} ${completedStages['stage-2'] ? 'is-completed' : ''}`} style={{ borderLeft: `4px solid ${stages[1].color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
              <div>
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: stages[1].color, display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>{stages[1].icon}</span>
                  <span>{stages[1].titleKey}</span>
                </span>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>{stages[1].timingDays}</span>
              </div>

              {/* Mark Done Button */}
              <button
                type="button"
                className="btn btn-sm"
                onClick={() => toggleStageDone('stage-2')}
                style={{
                  fontSize: '0.74rem',
                  padding: '3px 8px',
                  background: completedStages['stage-2'] ? 'rgba(16,185,129,0.15)' : 'rgba(255,255,255,0.8)',
                  border: `1px solid ${completedStages['stage-2'] ? '#10b981' : 'rgba(140,195,165,0.5)'}`,
                  color: completedStages['stage-2'] ? '#15803d' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  borderRadius: '6px',
                  fontWeight: 600,
                }}
              >
                {completedStages['stage-2'] ? `✓ Done (${completedStages['stage-2']})` : `[ ] ${t('fert_mark_done')}`}
              </button>
            </div>

            <p style={{ margin: '0.2rem 0 0.5rem 0', fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {stages[1].summary}
            </p>

            {/* Dosages Pill Container */}
            <div style={{ background: 'rgba(240,253,244,0.7)', padding: '0.65rem 0.8rem', borderRadius: '8px', fontSize: '0.82rem', display: 'flex', flexDirection: 'column', gap: '5px', margin: '0.4rem 0', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>🟡 <strong>Urea (46% N):</strong></span>
                <strong style={{ color: '#15803d' }}>
                  {stage2UreaKg.toFixed(1)} kg <span style={{ fontSize: '0.74rem', fontWeight: 400, color: 'var(--text-muted)' }}>({(stage2UreaKg / 50).toFixed(1)} bags)</span>
                </strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
                <span>🟤 DAP (18-46-0):</span>
                <span>Not Required (0 kg)</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
                <span>🔴 MOP (60% K):</span>
                <span>Not Required (0 kg)</span>
              </div>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', borderTop: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                <strong>{t('fert_method')}:</strong> {stages[1].instructions}
              </div>
            </div>
          </div>

          {/* ── STAGE 3 CARD ── */}
          <div className={`fert-stage-card ${activeStage.id === 'stage-3' ? 'is-active' : ''} ${completedStages['stage-3'] ? 'is-completed' : ''}`} style={{ borderLeft: `4px solid ${stages[2].color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
              <div>
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: stages[2].color, display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>{stages[2].icon}</span>
                  <span>{stages[2].titleKey}</span>
                </span>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>{stages[2].timingDays}</span>
              </div>

              {/* Mark Done Button */}
              <button
                type="button"
                className="btn btn-sm"
                onClick={() => toggleStageDone('stage-3')}
                style={{
                  fontSize: '0.74rem',
                  padding: '3px 8px',
                  background: completedStages['stage-3'] ? 'rgba(16,185,129,0.15)' : 'rgba(255,255,255,0.8)',
                  border: `1px solid ${completedStages['stage-3'] ? '#10b981' : 'rgba(140,195,165,0.5)'}`,
                  color: completedStages['stage-3'] ? '#15803d' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  borderRadius: '6px',
                  fontWeight: 600,
                }}
              >
                {completedStages['stage-3'] ? `✓ Done (${completedStages['stage-3']})` : `[ ] ${t('fert_mark_done')}`}
              </button>
            </div>

            <p style={{ margin: '0.2rem 0 0.5rem 0', fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {stages[2].summary}
            </p>

            {/* Dosages Pill Container */}
            <div style={{ background: 'rgba(240,253,244,0.7)', padding: '0.65rem 0.8rem', borderRadius: '8px', fontSize: '0.82rem', display: 'flex', flexDirection: 'column', gap: '5px', margin: '0.4rem 0', border: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>🟡 <strong>Urea (46% N):</strong></span>
                <strong style={{ color: '#15803d' }}>
                  {stage3UreaKg.toFixed(1)} kg <span style={{ fontSize: '0.74rem', fontWeight: 400, color: 'var(--text-muted)' }}>({(stage3UreaKg / 50).toFixed(1)} bags)</span>
                </strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
                <span>🟤 DAP (18-46-0):</span>
                <span>Not Required (0 kg)</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
                <span>🔴 MOP (60% K):</span>
                <span>Not Required (0 kg)</span>
              </div>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: '0.5rem', borderTop: '1px solid rgba(140,195,165,0.25)' }}>
              <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                <strong>{t('fert_method')}:</strong> {stages[2].instructions}
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* ── Total Field Requirement Summary & Action Buttons ──────────────── */}
      <div
        style={{
          marginTop: '1rem',
          padding: '0.85rem 1.1rem',
          borderRadius: '10px',
          background: 'rgba(240,253,244,0.7)',
          border: '1px solid rgba(140,195,165,0.3)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.85rem',
        }}
      >
        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Total Season Dose ({area} {unit}):
          </div>
          <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <span>🟡 Urea: <strong>{totalUreaKg.toFixed(1)} kg</strong> ({Math.ceil(totalUreaBags)} bags)</span>
            <span>🟤 DAP: <strong>{totalDapKg.toFixed(1)} kg</strong> ({Math.ceil(totalDapBags)} bags)</span>
            <span>🔴 MOP: <strong>{totalMopKg.toFixed(1)} kg</strong> ({Math.ceil(totalMopBags)} bags)</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn btn-sm"
            onClick={handleShareWhatsApp}
            style={{
              background: '#25D366',
              color: '#fff',
              border: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.3rem',
              fontWeight: 600,
            }}
            title={t('fert_share_whatsapp')}
          >
            <span aria-hidden="true">💬</span>
            <span>{t('fert_share_whatsapp')}</span>
          </button>

          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={handleDownloadCalendar}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}
            title={t('fert_add_calendar')}
          >
            <span aria-hidden="true">📅</span>
            <span>{t('fert_add_calendar')}</span>
          </button>

          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={handlePrint}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}
            title={t('fert_print_schedule')}
          >
            <span aria-hidden="true">🖨️</span>
            <span>{t('fert_print_schedule')}</span>
          </button>
        </div>
      </div>

    </div>
  );
};

