export interface Device {
  id: number
  brand: string
  model: string
  imei?: string | null
  storage?: string | null
  color?: string | null
  purchase_date?: string | null
  battery_health?: number | null
  appearance?: string | null
  repair_history?: string | null
  notes?: string | null
  estimated_price?: number | null
  is_deleted: boolean
  created_at: string
  updated_at?: string | null
  created_by?: string | null
  updated_by?: string | null
  inspections: Inspection[]
}

export interface DeviceListItem {
  id: number
  brand: string
  model: string
  imei?: string | null
  storage?: string | null
  color?: string | null
  battery_health?: number | null
  appearance?: string | null
  estimated_price?: number | null
  created_at: string
  inspection_count: number
}

export interface DeviceCreate {
  brand: string
  model: string
  imei?: string | null
  storage?: string | null
  color?: string | null
  purchase_date?: string | null
  battery_health?: number | null
  appearance?: string | null
  repair_history?: string | null
  notes?: string | null
  estimated_price?: number | null
}

export interface DeviceUpdate {
  brand?: string | null
  model?: string | null
  imei?: string | null
  storage?: string | null
  color?: string | null
  purchase_date?: string | null
  battery_health?: number | null
  appearance?: string | null
  repair_history?: string | null
  notes?: string | null
  estimated_price?: number | null
}

export interface Inspection {
  id: number
  device_id: number
  inspection_date: string
  appearance_grade: string
  function_items: string
  battery_health?: number | null
  estimated_value?: number | null
  appraiser_signature: string
  notes?: string | null
  is_deleted: boolean
  created_at: string
  updated_at?: string | null
  created_by?: string | null
  updated_by?: string | null
}

export interface InspectionCreate {
  device_id: number
  inspection_date: string
  appearance_grade: string
  function_items: string
  battery_health?: number | null
  estimated_value?: number | null
  appraiser_signature: string
  notes?: string | null
}

export interface InspectionUpdate {
  inspection_date?: string | null
  appearance_grade?: string | null
  function_items?: string | null
  battery_health?: number | null
  estimated_value?: number | null
  appraiser_signature?: string | null
  notes?: string | null
}

export interface PaginatedResponse {
  total: number
  page: number
  page_size: number
  pages: number
  items: DeviceListItem[]
}

export interface FunctionItemOption {
  key: string
  label: string
}

export interface MetadataResponse {
  mainstream_brands: string[]
  appearance_grades: string[]
  function_items: FunctionItemOption[]
}

export const MAINSTREAM_BRANDS = ['苹果', '华为', '小米', 'OPPO', 'vivo', '三星', '荣耀', '一加', 'realme', '魅族']

export const APPEARANCE_GRADES = ['全新', '99新', '95新', '9成新', '8成新', '7成新及以下']
