<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-bold text-gray-800">
          {{ isEdit ? '编辑质检记录' : '新增质检记录' }}
        </h2>
        <button
          @click="$emit('close')"
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="flex-1 overflow-y-auto p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">
              质检日期 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.inspection_date"
              type="date"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">
              外观等级 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.appearance_grade"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            >
              <option value="">请选择</option>
              <option v-for="g in appearanceGrades" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">电池健康 (%)</label>
            <input
              v-model.number="form.battery_health"
              type="number"
              min="0"
              max="100"
              placeholder="0-100"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">预估价值 (元)</label>
            <input
              v-model.number="form.estimated_value"
              type="number"
              min="0"
              step="0.01"
              placeholder="如：3200"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="md:col-span-2 space-y-1">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              功能检测项 <span class="text-red-500">*</span>
              <span class="ml-2 text-xs text-gray-500 font-normal">（勾选正常的功能项）</span>
            </label>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
              <label
                v-for="item in functionItems"
                :key="item.key"
                class="flex items-center gap-2 cursor-pointer hover:bg-white px-2 py-1.5 rounded transition-colors"
              >
                <input
                  type="checkbox"
                  :value="item.key"
                  v-model="selectedFunctions"
                  class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span class="text-sm text-gray-700">{{ item.label }}</span>
              </label>
            </div>
          </div>

          <div class="md:col-span-2 space-y-1">
            <label class="block text-sm font-medium text-gray-700">
              估价师签名 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.appraiser_signature"
              type="text"
              required
              placeholder="请输入估价师姓名"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="md:col-span-2 space-y-1">
            <label class="block text-sm font-medium text-gray-700">备注</label>
            <textarea
              v-model="form.notes"
              rows="3"
              placeholder="质检过程中的其他注意事项..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none"
            />
          </div>
        </div>

        <div v-if="submitError" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {{ submitError }}
        </div>
      </form>

      <div class="flex justify-end gap-3 px-6 py-4 border-t border-gray-200">
        <button
          type="button"
          @click="$emit('close')"
          class="px-5 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
        >
          取消
        </button>
        <button
          @click="handleSubmit"
          :disabled="submitting"
          class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
          {{ submitting ? '提交中...' : (isEdit ? '保存修改' : '创建记录') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { X, Loader2 } from 'lucide-vue-next'
import type { Inspection, InspectionCreate, InspectionUpdate, FunctionItemOption } from '@/types'
import { inspectionsApi } from '@/lib/api'

const props = defineProps<{
  deviceId: number
  inspection?: Inspection | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', inspection: Inspection): void
}>()

const appearanceGrades = ['全新', '99新', '95新', '9成新', '8成新', '7成新及以下']
const functionItems: FunctionItemOption[] = [
  { key: '屏幕显示', label: '屏幕显示' },
  { key: '触摸功能', label: '触摸功能' },
  { key: '通话功能', label: '通话功能' },
  { key: '摄像头', label: '摄像头' },
  { key: '扬声器', label: '扬声器' },
  { key: '麦克风', label: '麦克风' },
  { key: '振动马达', label: '振动马达' },
  { key: '指纹识别', label: '指纹识别' },
  { key: '面容识别', label: '面容识别' },
  { key: '充电接口', label: '充电接口' },
  { key: '耳机接口', label: '耳机接口' },
  { key: 'WIFI', label: 'WIFI' },
  { key: '蓝牙', label: '蓝牙' },
  { key: 'GPS', label: 'GPS' },
  { key: '按键', label: '按键' },
]

const isEdit = computed(() => !!props.inspection)

const form = reactive<InspectionCreate & InspectionUpdate>({
  device_id: props.deviceId,
  inspection_date: new Date().toISOString().split('T')[0],
  appearance_grade: '',
  function_items: '',
  battery_health: null,
  estimated_value: null,
  appraiser_signature: '',
  notes: null,
})

const selectedFunctions = ref<string[]>([])
const submitting = ref(false)
const submitError = ref('')

function cleanFormData() {
  const data: any = {
    device_id: props.deviceId,
    inspection_date: form.inspection_date,
    appearance_grade: form.appearance_grade,
    function_items: selectedFunctions.value.join(','),
    appraiser_signature: form.appraiser_signature,
  }
  if (form.battery_health != null) data.battery_health = form.battery_health
  if (form.estimated_value != null) data.estimated_value = form.estimated_value
  if (form.notes) data.notes = form.notes
  return data
}

async function handleSubmit() {
  if (selectedFunctions.value.length === 0) {
    submitError.value = '请至少勾选一个功能检测项'
    return
  }

  submitting.value = true
  submitError.value = ''

  try {
    const data = cleanFormData()
    let saved: Inspection
    if (isEdit.value && props.inspection) {
      saved = await inspectionsApi.update(props.inspection.id, data)
    } else {
      saved = await inspectionsApi.create(data)
    }
    emit('saved', saved)
  } catch (err: any) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') {
      submitError.value = detail
    } else if (Array.isArray(detail)) {
      submitError.value = detail.map((d: any) => d.msg || d.message).join('; ')
    } else {
      submitError.value = '提交失败，请稍后重试'
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (props.inspection) {
    Object.assign(form, {
      inspection_date: props.inspection.inspection_date,
      appearance_grade: props.inspection.appearance_grade,
      battery_health: props.inspection.battery_health,
      estimated_value: props.inspection.estimated_value,
      appraiser_signature: props.inspection.appraiser_signature,
      notes: props.inspection.notes,
    })
    if (props.inspection.function_items) {
      selectedFunctions.value = props.inspection.function_items.split(',').filter(Boolean)
    }
  }
})
</script>
