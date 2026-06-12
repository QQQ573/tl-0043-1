<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Smartphone class="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-800">回收门店设备管理</h1>
              <p class="text-xs text-gray-500">设备档案 · 质检记录 · 历史成交价</p>
            </div>
          </div>
          <button
            @click="showDeviceForm = true; editingDevice = null"
            class="px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all font-medium flex items-center gap-2 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30"
          >
            <Plus class="w-5 h-5" />
            新增设备
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 mb-6">
        <div class="flex flex-col lg:flex-row gap-4">
          <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700 mb-1.5">关键词搜索</label>
            <div class="relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                v-model="filters.keyword"
                type="text"
                placeholder="搜索型号或 IMEI..."
                class="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                @keyup.enter="loadDevices"
              />
            </div>
          </div>

          <div class="w-full lg:w-44">
            <label class="block text-sm font-medium text-gray-700 mb-1.5">品牌</label>
            <select
              v-model="filters.brand"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              @change="loadDevices"
            >
              <option value="">全部品牌</option>
              <option v-for="b in mainstreamBrands" :key="b" :value="b">{{ b }}</option>
              <option value="其他">其他</option>
            </select>
          </div>

          <div class="w-full lg:w-40">
            <label class="block text-sm font-medium text-gray-700 mb-1.5">最低成色</label>
            <select
              v-model="filters.appearance_min"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              @change="loadDevices"
            >
              <option value="">不限</option>
              <option v-for="g in appearanceGrades" :key="g" :value="g">{{ g }}以上</option>
            </select>
          </div>

          <div class="w-full lg:w-40">
            <label class="block text-sm font-medium text-gray-700 mb-1.5">最高成色</label>
            <select
              v-model="filters.appearance_max"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              @change="loadDevices"
            >
              <option value="">不限</option>
              <option v-for="g in appearanceGrades" :key="g" :value="g">{{ g }}以下</option>
            </select>
          </div>

          <div class="flex items-end gap-2">
            <button
              @click="loadDevices"
              class="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-medium flex items-center gap-2"
            >
              <Search class="w-4 h-4" />
              搜索
            </button>
            <button
              @click="resetFilters"
              class="px-5 py-2.5 border border-gray-300 text-gray-600 rounded-xl hover:bg-gray-50 transition-colors font-medium"
            >
              重置
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between mb-4">
        <div class="text-sm text-gray-600">
          共 <span class="font-semibold text-gray-800">{{ total }}</span> 条设备记录
          <span v-if="total > 0" class="ml-2 text-gray-400">
            （第 {{ page }} / {{ pages }} 页）
          </span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">每页显示</span>
          <select
            v-model.number="pageSize"
            class="px-2 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            @change="handlePageSizeChange"
          >
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
          <span class="text-sm text-gray-500">条</span>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center py-16">
        <Loader2 class="w-10 h-10 text-blue-500 animate-spin" />
      </div>

      <Empty v-else-if="!devices.length" class="py-16" />

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-6">
        <div
          v-for="device in devices"
          :key="device.id"
          class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg hover:border-blue-200 transition-all cursor-pointer group"
          @click="openDetail(device.id)"
        >
          <div class="p-5">
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center gap-2">
                <span class="px-2.5 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-lg">
                  {{ device.brand }}
                </span>
                <span
                  v-if="device.appearance"
                  class="px-2 py-0.5 text-xs font-medium rounded"
                  :class="appearanceClass(device.appearance)"
                >
                  {{ device.appearance }}
                </span>
              </div>
              <span class="text-xs text-gray-400">
                #{{ device.id }}
              </span>
            </div>

            <h3 class="text-lg font-bold text-gray-800 mb-2 group-hover:text-blue-600 transition-colors">
              {{ device.model }}
            </h3>

            <div v-if="device.imei" class="text-xs text-gray-500 mb-3 font-mono">
              IMEI: {{ device.imei }}
            </div>

            <div class="grid grid-cols-2 gap-2 mb-4">
              <div class="text-sm">
                <span class="text-gray-400">存储：</span>
                <span class="text-gray-700">{{ device.storage || '-' }}</span>
              </div>
              <div class="text-sm">
                <span class="text-gray-400">颜色：</span>
                <span class="text-gray-700">{{ device.color || '-' }}</span>
              </div>
              <div class="text-sm">
                <span class="text-gray-400">电池：</span>
                <span :class="batteryClass(device.battery_health)">
                  {{ device.battery_health != null ? device.battery_health + '%' : '-' }}
                </span>
              </div>
              <div class="text-sm">
                <span class="text-gray-400">质检：</span>
                <span class="text-gray-700">{{ device.inspection_count }} 次</span>
              </div>
            </div>

            <div v-if="device.estimated_price != null" class="pt-3 border-t border-gray-100">
              <div class="flex items-baseline gap-1">
                <span class="text-xs text-gray-400">预估回收价</span>
                <span class="text-xl font-bold text-green-600">
                  ¥{{ device.estimated_price.toLocaleString() }}
                </span>
              </div>
            </div>
          </div>

          <div class="px-5 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
            <span class="text-xs text-gray-400">
              {{ formatDate(device.created_at) }}
            </span>
            <div class="flex items-center gap-1 text-blue-600 text-sm font-medium group-hover:gap-2 transition-all">
              查看详情
              <ChevronRight class="w-4 h-4" />
            </div>
          </div>
        </div>
      </div>

      <div v-if="pages > 1" class="flex items-center justify-center gap-2">
        <button
          @click="changePage(1)"
          :disabled="page === 1"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronsLeft class="w-4 h-4" />
        </button>
        <button
          @click="changePage(page - 1)"
          :disabled="page === 1"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>

        <div class="flex items-center gap-1">
          <button
            v-for="p in visiblePages"
            :key="p"
            @click="changePage(p)"
            :class="[
              'px-3.5 py-2 rounded-lg text-sm font-medium transition-colors',
              p === page
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
                : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
            ]"
          >
            {{ p }}
          </button>
        </div>

        <button
          @click="changePage(page + 1)"
          :disabled="page === pages"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
        <button
          @click="changePage(pages)"
          :disabled="page === pages"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronsRight class="w-4 h-4" />
        </button>
      </div>
    </main>

    <DeviceForm
      v-if="showDeviceForm"
      :device="editingDevice"
      @close="showDeviceForm = false; editingDevice = null"
      @saved="handleDeviceSaved"
    />

    <DeviceDetail
      v-if="selectedDeviceId"
      :device-id="selectedDeviceId"
      @close="selectedDeviceId = 0"
      @edit="handleEditDevice"
      @deleted="handleDeviceDeleted"
      @updated="loadDevices"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Smartphone, Plus, Search, Loader2, ChevronRight,
  ChevronLeft, ChevronsLeft, ChevronsRight
} from 'lucide-vue-next'
import type { DeviceListItem, Device } from '@/types'
import { devicesApi } from '@/lib/api'
import DeviceForm from '@/components/DeviceForm.vue'
import DeviceDetail from '@/components/DeviceDetail.vue'
import Empty from '@/components/Empty.vue'

const mainstreamBrands = ['苹果', '华为', '小米', 'OPPO', 'vivo', '三星', '荣耀', '一加', 'realme', '魅族']
const appearanceGrades = ['全新', '99新', '95新', '9成新', '8成新', '7成新及以下']

const devices = ref<DeviceListItem[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const pages = ref(0)

const filters = reactive({
  keyword: '',
  brand: '',
  appearance_min: '',
  appearance_max: '',
})

const showDeviceForm = ref(false)
const editingDevice = ref<Device | null>(null)
const selectedDeviceId = ref(0)

const visiblePages = computed(() => {
  const result: number[] = []
  const totalPages = pages.value
  const current = page.value
  
  let start = Math.max(1, current - 2)
  let end = Math.min(totalPages, current + 2)
  
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(5, totalPages)
    } else if (end === totalPages) {
      start = Math.max(1, totalPages - 4)
    }
  }
  
  for (let i = start; i <= end; i++) {
    result.push(i)
  }
  return result
})

function appearanceClass(grade?: string | null) {
  switch (grade) {
    case '全新': return 'bg-green-100 text-green-700'
    case '99新': return 'bg-emerald-100 text-emerald-700'
    case '95新': return 'bg-teal-100 text-teal-700'
    case '9成新': return 'bg-blue-100 text-blue-700'
    case '8成新': return 'bg-amber-100 text-amber-700'
    case '7成新及以下': return 'bg-orange-100 text-orange-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

function batteryClass(health?: number | null) {
  if (health == null) return 'text-gray-500'
  if (health >= 90) return 'text-green-600 font-medium'
  if (health >= 70) return 'text-amber-600 font-medium'
  return 'text-red-600 font-medium'
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

async function loadDevices() {
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.brand) params.brand = filters.brand
    if (filters.appearance_min) params.appearance_min = filters.appearance_min
    if (filters.appearance_max) params.appearance_max = filters.appearance_max

    const res = await devicesApi.list(params)
    devices.value = res.items
    total.value = res.total
    pages.value = res.pages
  } catch (err) {
    console.error('加载设备列表失败:', err)
  } finally {
    loading.value = false
  }
}

function changePage(p: number) {
  if (p < 1 || p > pages.value || p === page.value) return
  page.value = p
  loadDevices()
}

function handlePageSizeChange() {
  page.value = 1
  loadDevices()
}

function resetFilters() {
  filters.keyword = ''
  filters.brand = ''
  filters.appearance_min = ''
  filters.appearance_max = ''
  page.value = 1
  loadDevices()
}

function openDetail(id: number) {
  selectedDeviceId.value = id
}

function handleEditDevice(device: Device) {
  editingDevice.value = device
  showDeviceForm.value = true
  selectedDeviceId.value = 0
}

async function handleDeviceSaved() {
  showDeviceForm.value = false
  editingDevice.value = null
  await loadDevices()
}

async function handleDeviceDeleted() {
  selectedDeviceId.value = 0
  await loadDevices()
}

onMounted(() => {
  loadDevices()
})
</script>
