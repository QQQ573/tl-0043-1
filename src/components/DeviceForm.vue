<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-bold text-gray-800">
          {{ isEdit ? '编辑设备档案' : '新增设备档案' }}
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
              品牌 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.brand"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            >
              <option value="">请选择品牌</option>
              <option v-for="b in mainstreamBrands" :key="b" :value="b">{{ b }}</option>
              <option value="其他">其他</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">
              型号 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.model"
              type="text"
              required
              placeholder="如：iPhone 15 Pro"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">
              IMEI
              <span v-if="isMainstreamBrand" class="text-red-500">*</span>
              <span v-if="isMainstreamBrand" class="ml-2 text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded">
                {{ form.brand }}为主流品牌必填
              </span>
            </label>
            <input
              v-model="form.imei"
              type="text"
              :required="isMainstreamBrand"
              :placeholder="isMainstreamBrand ? '请输入15位IMEI' : '选填'"
              maxlength="17"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all font-mono"
              @blur="validateImei"
              @input="formatImeiInput"
            />
            <p v-if="imeiError" class="text-sm text-red-500 mt-1">{{ imeiError }}</p>
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">存储容量</label>
            <select
              v-model="form.storage"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            >
              <option value="">请选择</option>
              <option v-for="s in storageOptions" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">颜色</label>
            <input
              v-model="form.color"
              type="text"
              placeholder="如：远峰蓝"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">购买日期</label>
            <input
              v-model="form.purchase_date"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
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
            <label class="block text-sm font-medium text-gray-700">成色</label>
            <select
              v-model="form.appearance"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            >
              <option value="">请选择</option>
              <option v-for="g in appearanceGrades" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">预估回收价 (元)</label>
            <input
              v-model.number="form.estimated_price"
              type="number"
              min="0"
              step="0.01"
              placeholder="如：3500"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="md:col-span-2 space-y-1">
            <label class="block text-sm font-medium text-gray-700">拆修史</label>
            <textarea
              v-model="form.repair_history"
              rows="2"
              placeholder="是否维修过、更换过部件等"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none"
            />
          </div>

          <div class="md:col-span-2 space-y-1">
            <label class="block text-sm font-medium text-gray-700">备注</label>
            <textarea
              v-model="form.notes"
              rows="2"
              placeholder="其他补充信息"
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
          {{ submitting ? '提交中...' : (isEdit ? '保存修改' : '创建设备') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { X, Loader2 } from 'lucide-vue-next'
import type { Device, DeviceCreate, DeviceUpdate } from '@/types'
import { devicesApi } from '@/lib/api'

const props = defineProps<{
  device?: Device | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', device: Device): void
}>()

const mainstreamBrands = ['苹果', '华为', '小米', 'OPPO', 'vivo', '三星', '荣耀', '一加', 'realme', '魅族']
const appearanceGrades = ['全新', '99新', '95新', '9成新', '8成新', '7成新及以下']
const storageOptions = ['64GB', '128GB', '256GB', '512GB', '1TB', '2TB']

const isEdit = computed(() => !!props.device)

const form = reactive<DeviceCreate & DeviceUpdate>({
  brand: '',
  model: '',
  imei: null,
  storage: null,
  color: null,
  purchase_date: null,
  battery_health: null,
  appearance: null,
  repair_history: null,
  notes: null,
  estimated_price: null,
})

const submitting = ref(false)
const submitError = ref('')
const imeiError = ref('')

const isMainstreamBrand = computed(() => mainstreamBrands.includes(form.brand))

function luhnCheck(imei: string): boolean {
  if (imei.length !== 15) return false
  const digits = imei.slice(0, 14).split('').map(d => parseInt(d))
  for (let i = digits.length - 1; i >= 0; i -= 2) {
    digits[i] *= 2
    if (digits[i] > 9) digits[i] -= 9
  }
  const total = digits.reduce((a, b) => a + b, 0)
  const checkDigit = (10 - (total % 10)) % 10
  return checkDigit === parseInt(imei[14])
}

function formatImeiInput(e: Event) {
  const input = e.target as HTMLInputElement
  let val = input.value.replace(/\D/g, '')
  if (val.length > 15) val = val.slice(0, 15)
  const parts = [val.slice(0, 3), val.slice(3, 8), val.slice(8, 14), val.slice(14)]
  form.imei = parts.filter(p => p).join(' ')
  imeiError.value = ''
}

function validateImei() {
  if (!form.imei) {
    if (isMainstreamBrand.value) {
      imeiError.value = `${form.brand}为主流品牌，IMEI为必填项`
    }
    return
  }
  const cleanImei = form.imei.replace(/\s/g, '')
  if (!/^\d{15}$/.test(cleanImei)) {
    imeiError.value = 'IMEI必须为15位数字'
    return
  }
  if (!luhnCheck(cleanImei)) {
    imeiError.value = 'IMEI格式校验失败，请检查号码是否正确'
    return
  }
  imeiError.value = ''
}

function cleanFormData() {
  const data: any = { ...form }
  if (data.imei) {
    data.imei = data.imei.replace(/\s/g, '')
  }
  for (const key of Object.keys(data)) {
    if (data[key] === '' || data[key] === null) {
      delete data[key]
    }
  }
  if (data.imei === undefined && isMainstreamBrand.value) {
    data.imei = ''
  }
  return data
}

async function handleSubmit() {
  if (isMainstreamBrand.value && !form.imei) {
    imeiError.value = `${form.brand}为主流品牌，IMEI为必填项`
    return
  }
  if (form.imei) {
    validateImei()
    if (imeiError.value) return
  }

  submitting.value = true
  submitError.value = ''

  try {
    const data = cleanFormData()
    let saved: Device
    if (isEdit.value && props.device) {
      saved = await devicesApi.update(props.device.id, data)
    } else {
      saved = await devicesApi.create(data)
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
  if (props.device) {
    Object.assign(form, {
      brand: props.device.brand,
      model: props.device.model,
      imei: props.device.imei,
      storage: props.device.storage,
      color: props.device.color,
      purchase_date: props.device.purchase_date,
      battery_health: props.device.battery_health,
      appearance: props.device.appearance,
      repair_history: props.device.repair_history,
      notes: props.device.notes,
      estimated_price: props.device.estimated_price,
    })
  }
})
</script>
