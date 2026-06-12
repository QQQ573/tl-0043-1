<template>
  <div class="relative">
    <div class="absolute left-4 top-2 bottom-2 w-0.5 bg-gray-200"></div>

    <div class="space-y-4">
      <div
        v-for="tx in sortedTransactions"
        :key="tx.id"
        class="relative pl-10"
      >
        <div
          class="absolute left-2 w-5 h-5 rounded-full border-2 border-white shadow flex items-center justify-center"
          :class="tx.trade_type === '回收' ? 'bg-emerald-500' : 'bg-blue-500'"
        >
          <ArrowDownLeft v-if="tx.trade_type === '回收'" class="w-3 h-3 text-white" />
          <ArrowUpRight v-else class="w-3 h-3 text-white" />
        </div>

        <div
          class="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-md transition-shadow"
        >
          <div class="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
            <div class="flex items-center gap-3">
              <Calendar class="w-4 h-4 text-gray-500" />
              <span class="font-medium text-gray-800">{{ tx.trade_date }}</span>
              <span
                class="px-2 py-0.5 rounded text-xs font-medium"
                :class="tx.trade_type === '回收' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'"
              >
                {{ tx.trade_type }}
              </span>
            </div>
            <div class="flex items-center gap-1">
              <button
                @click="$emit('edit', tx)"
                class="p-1.5 hover:bg-gray-200 rounded text-gray-500 hover:text-gray-700 transition-colors"
                title="编辑"
              >
                <Edit2 class="w-4 h-4" />
              </button>
              <button
                @click="$emit('delete', tx.id)"
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
                <span class="text-gray-500">成交金额：</span>
                <span
                  class="font-bold"
                  :class="tx.trade_type === '回收' ? 'text-emerald-600' : 'text-blue-600'"
                >
                  ¥{{ tx.actual_amount.toFixed(2) }}
                </span>
              </div>
              <div>
                <span class="text-gray-500">结算方式：</span>
                <span class="text-gray-700">{{ tx.settlement_method }}</span>
              </div>
              <div class="col-span-2">
                <span class="text-gray-500">交易对方：</span>
                <span class="text-gray-700 font-medium">{{ tx.counterparty_name }}</span>
              </div>
            </div>

            <div v-if="tx.notes" class="pt-2 border-t border-gray-100">
              <p class="text-xs text-gray-500 mb-1">备注</p>
              <p class="text-sm text-gray-600">{{ tx.notes }}</p>
            </div>

            <div class="flex items-center gap-2 text-xs text-gray-400 pt-2 border-t border-gray-100">
              <UserCheck class="w-3.5 h-3.5" />
              操作人：<span class="text-gray-600 font-medium">{{ tx.created_by || '-' }}</span>
              <span class="mx-2">·</span>
              <Clock class="w-3.5 h-3.5" />
              {{ formatDate(tx.created_at) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!transactions?.length" class="text-center py-12 text-gray-400">
      <Receipt class="w-12 h-12 mx-auto mb-2 opacity-50" />
      <p>暂无成交记录</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Calendar, Edit2, Trash2, UserCheck, Clock, Receipt,
  ArrowDownLeft, ArrowUpRight
} from 'lucide-vue-next'
import type { Transaction } from '@/types'

const props = defineProps<{
  transactions: Transaction[] | null | undefined
}>()

defineEmits<{
  (e: 'edit', transaction: Transaction): void
  (e: 'delete', id: number): void
}>()

const sortedTransactions = computed(() => {
  return [...(props.transactions || [])].sort(
    (a, b) => new Date(b.trade_date).getTime() - new Date(a.trade_date).getTime()
  )
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
