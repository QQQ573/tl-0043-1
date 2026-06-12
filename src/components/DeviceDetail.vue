<template>
  <div class="fixed inset-0 z-50 flex justify-end">
    <div
      class="absolute inset-0 bg-black/40 backdrop-blur-sm"
      @click="$emit('close')"
    />
    <div class="relative w-full max-w-2xl bg-white shadow-2xl h-full flex flex-col animate-slide-in">
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div>
          <h2 class="text-xl font-bold text-gray-800">{{ device?.brand }} {{ device?.model }}</h2>
          <p class="text-sm text-gray-500 mt-0.5" v-if="device?.imei">
            IMEI: <span class="font-mono">{{ device.imei }}</span>
          </p>
        </div>
        <button
          @click="$emit('close')"
          class="p-2 hover:bg-white/80 rounded-lg transition-colors"
        >
          <X class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <div v-if="!device" class="flex-1 flex items-center justify-center">
        <Loader2 class="w-8 h-8 text-blue-500 animate-spin" />
      </div>

      <div v-else class="flex-1 overflow-y-auto">
        <div class="p-6">
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="p-3 bg-gray-50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">存储</p>
              <p class="font-medium text-gray-800">{{ device.storage || '-' }}</p>
            </div>
            <div class="p-3 bg-gray-50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">颜色</p>
              <p class="font-medium text-gray-800">{{ device.color || '-' }}</p>
            </div>
            <div class="p-3 bg-gray-50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">成色</p>
              <p class="font-medium text-gray-800">
                <span
                  class="px-2 py-0.5 rounded text-xs font-medium"
                  :class="appearanceClass(device.appearance)"
                >
                  {{ device.appearance || '-' }}
                </span>
              </p>
            </div>
            <div class="p-3 bg-gray-50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">电池健康</p>
              <p class="font-medium text-gray-800">
                <span :class="batteryClass(device.battery_health)">
                  {{ device.battery_health != null ? device.battery_health + '%' : '-' }}
                </span>
              </p>
            </div>
            <div class="p-3 bg-gray-50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">购买日期</p>
              <p class="font-medium text-gray-800">{{ device.purchase_date || '-' }}</p>
            </div>
            <div class="p-3 bg-green-50 rounded-lg">
              <p class="text-xs text-green-600 mb-1">预估回收价</p>
              <p class="font-bold text-green-700 text-lg">
                {{ device.estimated_price != null ? '¥' + device.estimated_price : '-' }}
              </p>
            </div>
          </div>

          <div v-if="device.repair_history" class="mb-6">
            <h4 class="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <Wrench class="w-4 h-4" /> 拆修史
            </h4>
            <div class="p-3 bg-amber-50 border border-amber-200 rounded-lg text-gray-700 text-sm">
              {{ device.repair_history }}
            </div>
          </div>

          <div v-if="device.notes" class="mb-6">
            <h4 class="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <FileText class="w-4 h-4" /> 备注
            </h4>
            <div class="p-3 bg-gray-50 rounded-lg text-gray-700 text-sm">
              {{ device.notes }}
            </div>
          </div>

          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
              <ClipboardCheck class="w-5 h-5 text-blue-500" />
              质检记录
              <span class="text-sm font-normal text-gray-500">({{ device.inspections?.length || 0 }}条)</span>
            </h3>
            <button
              @click="showInspectionForm = true; editingInspection = null"
              class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1"
            >
              <Plus class="w-4 h-4" /> 新增质检
            </button>
          </div>

          <div v-if="!device.inspections?.length" class="text-center py-8 text-gray-400">
            <ClipboardCheck class="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>暂无质检记录</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="ins in sortedInspections"
              :key="ins.id"
              class="border border-gray-200 rounded-xl overflow-hidden hover:shadow-md transition-shadow"
            >
              <div class="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
                <div class="flex items-center gap-3">
                  <Calendar class="w-4 h-4 text-gray-500" />
                  <span class="font-medium text-gray-800">{{ ins.inspection_date }}</span>
                  <span
                    class="px-2 py-0.5 rounded text-xs font-medium"
                    :class="appearanceClass(ins.appearance_grade)"
                  >
                    {{ ins.appearance_grade }}
                  </span>
                </div>
                <div class="flex items-center gap-1">
                  <button
                    @click="handleEditInspection(ins)"
                    class="p-1.5 hover:bg-gray-200 rounded text-gray-500 hover:text-gray-700 transition-colors"
                    title="编辑"
                  >
                    <Edit2 class="w-4 h-4" />
                  </button>
                  <button
                    @click="handleDeleteInspection(ins.id)"
                    class="p-1.5 hover:bg-red-100 rounded text-gray-500 hover:text-red-600 transition-colors"
                    title="删除"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div class="p-4 space-y-3">
                <div class="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span class="text-gray-500">电池健康：</span>
                    <span :class="batteryClass(ins.battery_health)">
                      {{ ins.battery_health != null ? ins.battery_health + '%' : '-' }}
                    </span>
                  </div>
                  <div>
                    <span class="text-gray-500">预估价值：</span>
                    <span class="font-medium text-green-600">
                      {{ ins.estimated_value != null ? '¥' + ins.estimated_value : '-' }}
                    </span>
                  </div>
                </div>
                <div>
                  <p class="text-xs text-gray-500 mb-1">功能检测</p>
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="func in ins.function_items.split(',').filter(Boolean)"
                      :key="func"
                      class="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs"
                    >
                      {{ func }}
                    </span>
                    <span v-if="!ins.function_items" class="text-gray-400 text-sm">无</span>
                  </div>
                </div>
                <div v-if="ins.notes" class="pt-2 border-t border-gray-100">
                  <p class="text-xs text-gray-500 mb-1">备注</p>
                  <p class="text-sm text-gray-600">{{ ins.notes }}</p>
                </div>
                <div class="flex items-center gap-2 text-xs text-gray-400 pt-2 border-t border-gray-100">
                  <UserCheck class="w-3.5 h-3.5" />
                  估价师：<span class="text-gray-600 font-medium">{{ ins.appraiser_signature }}</span>
                  <span class="mx-2">·</span>
                  <Clock class="w-3.5 h-3.5" />
                  {{ formatDate(ins.created_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="border-t border-gray-200 px-6 py-3 flex justify-end gap-3">
        <button
          @click="$emit('edit', device)"
          class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium flex items-center gap-2"
        >
          <Edit2 class="w-4 h-4" /> 编辑设备
        </button>
        <button
          @click="handleDeleteDevice"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium flex items-center gap-2"
        >
          <Trash2 class="w-4 h-4" /> 删除设备
        </button>
      </div>
    </div>

    <InspectionForm
      v-if="showInspectionForm"
      :device-id="device?.id || 0"
      :inspection="editingInspection"
      @close="showInspectionForm = false; editingInspection = null"
      @saved="handleInspectionSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  X, Loader2, Plus, Wrench, FileText, ClipboardCheck,
  Calendar, Edit2, Trash2, UserCheck, Clock
} from 'lucide-vue-next'
import type { Device, Inspection } from '@/types'
import { devicesApi, inspectionsApi } from '@/lib/api'
import InspectionForm from './InspectionForm.vue'

const props = defineProps<{
  deviceId: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'edit', device: Device): void
  (e: 'deleted'): void
  (e: 'updated'): void
}>()

const device = ref<Device | null>(null)
const showInspectionForm = ref(false)
const editingInspection = ref<Inspection | null>(null)

const sortedInspections = computed(() => {
  return [...(device.value?.inspections || [])].sort(
    (a, b) => new Date(b.inspection_date).getTime() - new Date(a.inspection_date).getTime()
  )
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
  if (health == null) return 'text-gray-600'
  if (health >= 90) return 'text-green-600 font-medium'
  if (health >= 70) return 'text-amber-600 font-medium'
  return 'text-red-600 font-medium'
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function loadDevice() {
  device.value = null
  try {
    device.value = await devicesApi.get(props.deviceId)
  } catch (err) {
    console.error('加载设备失败:', err)
  }
}

function handleEditInspection(ins: Inspection) {
  editingInspection.value = ins
  showInspectionForm.value = true
}

async function handleDeleteInspection(id: number) {
  if (!confirm('确定要删除这条质检记录吗？')) return
  try {
    await inspectionsApi.remove(id)
    await loadDevice()
    emit('updated')
  } catch (err: any) {
    alert('删除失败: ' + (err.response?.data?.detail || err.message))
  }
}

async function handleInspectionSaved() {
  showInspectionForm.value = false
  editingInspection.value = null
  await loadDevice()
  emit('updated')
}

async function handleDeleteDevice() {
  if (!device.value) return
  if (!confirm(`确定要删除【${device.value.brand} ${device.value.model}】吗？\n该设备的所有质检记录也将被删除。`)) return
  try {
    await devicesApi.remove(device.value.id)
    emit('deleted')
    emit('close')
  } catch (err: any) {
    alert('删除失败: ' + (err.response?.data?.detail || err.message))
  }
}

onMounted(() => {
  loadDevice()
})
</script>

<style scoped>
.animate-slide-in {
  animation: slideIn 0.25s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
