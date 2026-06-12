import { APPEARANCE_GRADES } from '@/types'

export const DEVIATION_WARNING_THRESHOLD = 0.12

export const APPEARANCE_FLOAT_COEFFICIENTS: Record<string, number> = {
  '全新': 0.05,
  '99新': 0.06,
  '95新': 0.07,
  '9成新': 0.08,
  '8成新': 0.10,
  '7成新及以下': 0.12,
}

export function calculateDeviation(currentPrice: number, benchmarkPrice: number): number {
  if (!benchmarkPrice || benchmarkPrice === 0) return 0
  return (currentPrice - benchmarkPrice) / benchmarkPrice
}

export function isDeviationWarning(
  deviationRate: number,
  threshold: number = DEVIATION_WARNING_THRESHOLD
): boolean {
  return Math.abs(deviationRate) > threshold
}

export function getAppearanceFloatCoefficient(appearance?: string | null): number {
  if (!appearance) return 0.08
  return APPEARANCE_FLOAT_COEFFICIENTS[appearance] ?? 0.08
}

export function getSuggestedPriceRange(
  avgPrice?: number | null,
  appearance?: string | null
): { min: number; max: number } | null {
  if (avgPrice == null) return null
  const coeff = getAppearanceFloatCoefficient(appearance)
  return {
    min: Math.round(avgPrice * (1 - coeff)),
    max: Math.round(avgPrice * (1 + coeff)),
  }
}

export function formatDeviation(deviationRate: number): string {
  const percent = (deviationRate * 100).toFixed(1)
  const sign = deviationRate > 0 ? '+' : ''
  return `${sign}${percent}%`
}

export function getDeviationLevel(deviationRate: number): 'high' | 'normal' | 'low' {
  if (Math.abs(deviationRate) > DEVIATION_WARNING_THRESHOLD) {
    return deviationRate > 0 ? 'high' : 'low'
  }
  return 'normal'
}

export function getAppearanceIndex(appearance?: string | null): number {
  if (!appearance) return -1
  return APPEARANCE_GRADES.indexOf(appearance)
}

export function getNextAppearance(appearance?: string | null): string | null {
  const idx = getAppearanceIndex(appearance)
  if (idx < 0 || idx >= APPEARANCE_GRADES.length - 1) return null
  return APPEARANCE_GRADES[idx + 1]
}

export function getPrevAppearance(appearance?: string | null): string | null {
  const idx = getAppearanceIndex(appearance)
  if (idx <= 0) return null
  return APPEARANCE_GRADES[idx - 1]
}
