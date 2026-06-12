<template>
  <div class="text-center py-16">
    <div class="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
      <Package class="w-10 h-10 text-gray-300" />
    </div>
    <p class="text-gray-400 text-lg">{{ text }}</p>
    <p v-if="subtitle" class="text-gray-300 text-sm mt-1">{{ subtitle }}</p>
  </div>
</template>

<script setup lang="ts">
import { Package } from 'lucide-vue-next'

withDefaults(defineProps<{
  text?: string
  subtitle?: string
}>(), {
  text: '暂无数据',
  subtitle: '',
})
</script>
