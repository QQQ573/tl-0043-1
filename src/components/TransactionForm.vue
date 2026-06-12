<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col">
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-bold text-gray-800">
          {{ isEdit ? '编辑成交记录' : '新增成交记录' }}
        </h2>
        <button
          @click="$emit('close')"
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="flex-1 overflow-y-auto p-6">
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">
                交易类型 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="form.trade_type"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              >
                <option value="">请选择</option>
                <option v-for="t in tradeTypes" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">
                交易日期 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.trade_date"
                type="date"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">
                成交金额 (元) <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="form.actual_amount"
                type="number"
                min="0"
                step="0.01"
                required
                placeholder="如：3500"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              />
            </div>

            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">
                结算方式 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="form.settlement_method"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              >
                <option value="">请选择</option>
                <option v-for="m in settlementMethods" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">
              交易对方 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.counterparty_name"
              type="text"
              required
              maxlength="100"
              placeholder="请输入对方姓名/机构名称"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <div class="space-y-1">
            <label class="block text-sm font-medium text-gray-700">备注</label>
            <textarea
              v-model="form.notes"
              rows="3"
              placeholder="交易相关备注信息..."
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
import type { Transaction, TransactionCreate, TransactionUpdate } from '@/types'
import { TRADE_TYPES, SETTLEMENT_METHODS } from '@/types'
import { transactionsApi } from '@/lib/api'

const props = defineProps<{
  deviceId: number
  transaction?: Transaction | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', transaction: Transaction): void
}>()

const tradeTypes = TRADE_TYPES
const settlementMethods = SETTLEMENT_METHODS

const isEdit = computed(() => !!props.transaction)

const form = reactive<TransactionCreate & TransactionUpdate>({
  device_id: props.deviceId,
  trade_type: '',
  actual_amount: 0,
  counterparty_name: '',
  trade_date: new Date().toISOString().split('T')[0],
  settlement_method: '',
  notes: null,
})

const submitting = ref(false)
const submitError = ref('')

function cleanFormData() {
  const data: any = {
    device_id: props.deviceId,
    trade_type: form.trade_type,
    actual_amount: form.actual_amount,
    counterparty_name: form.counterparty_name,
    trade_date: form.trade_date,
    settlement_method: form.settlement_method,
  }
  if (form.notes) data.notes = form.notes
  return data
}

async function handleSubmit() {
  if (!form.trade_type) {
    submitError.value = '请选择交易类型'
    return
  }
  if (!form.settlement_method) {
    submitError.value = '请选择结算方式'
    return
  }
  if (form.actual_amount <= 0) {
    submitError.value = '成交金额必须大于 0'
    return
  }

  submitting.value = true
  submitError.value = ''

  try {
    const data = cleanFormData()
    let saved: Transaction
    if (isEdit.value && props.transaction) {
      saved = await transactionsApi.update(props.transaction.id, data)
    } else {
      saved = await transactionsApi.create(data)
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
  if (props.transaction) {
    Object.assign(form, {
      trade_type: props.transaction.trade_type,
      actual_amount: props.transaction.actual_amount,
      counterparty_name: props.transaction.counterparty_name,
      trade_date: props.transaction.trade_date,
      settlement_method: props.transaction.settlement_method,
      notes: props.transaction.notes,
    })
  }
})
</script>
