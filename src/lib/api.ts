import axios from 'axios'
import type {
  Device, DeviceCreate, DeviceUpdate, PaginatedResponse,
  Inspection, InspectionCreate, InspectionUpdate, MetadataResponse
} from '@/types'

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const metadataApi = {
  get: () => api.get<MetadataResponse>('/metadata').then(r => r.data),
}

export const devicesApi = {
  list: (params: {
    page?: number
    page_size?: number
    brand?: string
    appearance_min?: string
    appearance_max?: string
    keyword?: string
  }) => api.get<PaginatedResponse>('/devices', { params }).then(r => r.data),

  get: (id: number) => api.get<Device>(`/devices/${id}`).then(r => r.data),

  create: (data: DeviceCreate) => api.post<Device>('/devices', data).then(r => r.data),

  update: (id: number, data: DeviceUpdate) => api.put<Device>(`/devices/${id}`, data).then(r => r.data),

  remove: (id: number) => api.delete(`/devices/${id}`).then(r => r.data),
}

export const inspectionsApi = {
  list: (deviceId?: number) =>
    api.get<Inspection[]>('/inspections', {
      params: deviceId ? { device_id: deviceId } : undefined,
    }).then(r => r.data),

  get: (id: number) => api.get<Inspection>(`/inspections/${id}`).then(r => r.data),

  create: (data: InspectionCreate) => api.post<Inspection>('/inspections', data).then(r => r.data),

  update: (id: number, data: InspectionUpdate) => api.put<Inspection>(`/inspections/${id}`, data).then(r => r.data),

  remove: (id: number) => api.delete(`/inspections/${id}`).then(r => r.data),
}

export default api
