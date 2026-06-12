<template>
  <div class="fixed inset-0 z-50 flex justify-end">
    <div
      class="absolute inset-0 bg-black/40 backdrop-blur-sm"
      @click="$emit('close')"
    />
    <div class="relative w-full max-w-md bg-white shadow-2xl h-full flex flex-col animate-slide-in">
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
        <div>
          <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2">
            <TrendingUp class="w-5 h-5 text-indigo-500" />
            同款行情基准
          </h2>
          <p class="text-sm text-gray-500 mt-0.5">
            {{ brand }} {{ model }}
            <span v-if="appearance" class="ml-1">· {{ appearance }}</span>
          </p>
        </div>
        <button
          @click="$emit('close')"
          class="p-2 hover:bg-white/80 rounded-lg transition-colors"
        >
          <X class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <div v-if="loading" class="flex-1 flex items-center justify-center">
        <Loader2 class="w-8 h-8 text-indigo-500 animate-spin" />
      </div>

      <div v-else-if="error" class="flex-1 flex items-center justify-center">
        <div class="text-center text-gray-500">
          <AlertCircle class="w-10 h-10 mx-auto mb-2 text-red-400" />
          <p>{{ error }}</p>
          <button
            @click="loadBenchmark"
            class="mt-3 px-4 py-1.5 text-sm text-indigo-600 hover:text-indigo-700 font-medium"
          >
            重试
          </button>
        </div>
      </div>

      <div v-else class="flex-1 overflow-y-auto p-6">
        <div v-if="!benchmark || benchmark.count === 0" class="text-center py-12 text-gray-400">
          <BarChart3 class="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p class="mb-1">暂无同款成交数据不足</p>
          <p class="text-sm">近 {{ days }} 天内暂无成交记录</p>
        </div>

        <template v-else>
          <div class="mb-6">
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm text-gray-500">统计周期</span>
              <span class="text-sm font-medium text-gray-700">近 {{ benchmark.days }} 天</span>
            </div>
            <div class="flex items-center justify-between mb-3">
              <span class="text-sm text-gray-500">成交笔数</span>
              <span class="text-sm font-medium text-gray-700">{{ benchmark.count }} 笔</span>
            </div>
          </div>

          <div class="mb-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <DollarSign class="w-4 h-4" />
              价格分布
            </h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-100">
                <div class="flex items-center gap-2">
                  <TrendingUp class="w-4 h-4 text-green-600" />
                  <span class="text-sm text-gray-600">最高价</span>
                </div>
                <span class="font-bold text-green-700">¥{{ benchmark.max_price?.toFixed(0) }}</span>
              </div>

              <div class="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-100">
                <div class="flex items-center gap-2">
                  <Minus class="w-4 h-4 text-blue-600" />
                  <span class="text-sm text-gray-600">均价</span>
                </div>
                <span class="font-bold text-blue-700">¥{{ benchmark.avg_price?.toFixed(0) }}</span>
              </div>

              <div class="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-100">
                <div class="flex items-center gap-2">
                  <TrendingDown class="w-4 h-4 text-orange-600" />
                  <span class="text-sm text-gray-600">最低价</span>
                </div>
                <span class="font-bold text-orange-700">¥{{ benchmark.min_price?.toFixed(0) }}</span>
              </div>

              <div class="flex items-center justify-between p-3 bg-purple-50 rounded-lg border border-purple-100">
                <div class="flex items-center gap-2">
                  <BarChart3 class="w-4 h-4 text-purple-600" />
                  <span class="text-sm text-gray-600">中位价</span>
                </div>
                <span class="font-bold text-purple-700">¥{{ benchmark.median_price?.toFixed(0) }}</span>
              </div>
            </div>
          </div>

          <div v-if="currentPrice != null" class="mb-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <Target class="w-4 h-4" />
              当前估价对比
            </h3>

            <div class="p-4 rounded-xl border-2" :class="deviationLevelClass">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm text-gray-600">当前估价</span>
                <span class="font-bold text-lg" :class="deviationTextClass">
                  ¥{{ currentPrice.toFixed(0) }}
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">偏差率</span>
                <span class="font-semibold" :class="deviationTextClass">
                  {{ formatDeviation(deviationRate) }}
                </span>
              </div>
            </div>

            <div v-if="isWarning" class="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <div class="flex items-start gap-2">
                <AlertTriangle class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div class="text-sm">
                  <p class="font-medium text-amber-800 mb-1">价格偏离较大</p>
                  <p class="text-amber-700">
                    建议调整至合理区间：
                    <span class="font-bold">¥{{ suggestedRange?.min }}</span>
                    ~
                    <span class="font-bold">¥{{ suggestedRange?.max }}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div v-if="suggestedRange" class="mb-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <Lightbulb class="w-4 h-4" />
              建议调价区间
            </h3>
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-200">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">基于成色浮动系数</span>
                <span class="text-xs text-gray-400">±{{ (appearanceCoefficient * 100).toFixed(0) }}%</span>
              </div>
              <div class="mt-2 flex items-center justify-between">
                <span class="text-gray-500 text-sm">下限</span>
                <span class="font-bold text-gray-800">¥{{ suggestedRange.min }}</span>
              </div>
              <div class="my-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-orange-400 via-green-400 to-emerald-500 rounded-full"
                  :style="{ width: currentPricePercent + '%' }"
                ></div>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-500 text-sm">上限</span>
                <span class="font-bold text-gray-800">¥{{ suggestedRange.max }}</span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <div class="border-t border-gray-200 px-6 py-3 flex justify-end">
        <button
          @click="$emit('close')"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  X, Loader2, TrendingUp, TrendingDown, AlertCircle, AlertTriangle,
  DollarSign, Minus, BarChart3, Target, Lightbulb
} from 'lucide-vue-next'
import type { BenchmarkResponse } from '@/types'
import { transactionsApi } from '@/lib/api'
import {
  calculateDeviation, isDeviationWarning, formatDeviation,
  getAppearanceFloatCoefficient, getSuggestedPriceRange, getDeviationLevel
} from '@/utils/priceDeviation'

const props = defineProps<{
  brand: string
  model: string
  appearance?: string | null
  currentPrice?: number | null
  days?: number
}>()

defineEmits<{
  (e: 'close'): void
}>()

const benchmark = ref<BenchmarkResponse | null>(null)
const loading = ref(false)
const error = ref('')

const days = computed(() => props.days || 90)

const deviationRate = computed(() => {
  if (props.currentPrice == null || !benchmark.value?.avg_price) return 0
  return calculateDeviation(props.currentPrice, benchmark.value.avg_price)
})

const isWarning = computed(() => isDeviationWarning(deviationRate.value))

const deviationLevel = computed(() => getDeviationLevel(deviationRate.value))

const deviationLevelClass = computed(() => {
  switch (deviationLevel.value) {
    case 'high': return 'border-amber-300 bg-amber-50'
    case 'low': return 'border-amber-300 bg-amber-50'
    default: return 'border-green-200 bg-green-50'
  }
})

const deviationTextClass = computed(() => {
  switch (deviationLevel.value) {
    case 'high': return 'text-amber-700'
    case 'low': return 'text-amber-700'
    default: return 'text-green-700'
  }
})

const appearanceCoefficient = computed(() => getAppearanceFloatCoefficient(props.appearance))

const suggestedRange = computed(() => {
  if (!benchmark.value?.avg_price) return null
  return getSuggestedPriceRange(benchmark.value.avg_price, props.appearance)
})

const currentPricePercent = computed(() => {
  if (!suggestedRange.value || props.currentPrice == null) return 50
  const { min, max } = suggestedRange.value
  if (max === min) return 50
  const percent = (props.currentPrice - min) / (max - min) * 100
  return Math.max(0, Math.min(100, percent))
})

async function loadBenchmark() {
  if (!props.brand || !props.model) return

  loading.value = true
  error.value = ''

  try {
    benchmark.value = await transactionsApi.getBenchmark({
      brand: props.brand,
      model: props.model,
      appearance: props.appearance || undefined,
      days: days.value,
    })
  } catch (err: any) {
    error.value = err.response?.data?.detail || '加载行情数据失败'
    benchmark.value = null
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.brand, props.model, props.appearance, props.days],
  () => {
    loadBenchmark()
  }
)

onMounted(() => {
  loadBenchmark()
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
