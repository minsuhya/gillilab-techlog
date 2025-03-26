<template>
  <div class="ad-container" :class="position">
    <ins
      class="adsbygoogle"
      :style="{ display: 'block' }"
      :data-ad-client="'ca-pub-YOUR_PUBLISHER_ID'"
      :data-ad-slot="adSlot"
      :data-ad-format="format"
      :data-full-width-responsive="responsive"
    ></ins>
  </div>
</template>

<script setup>
import { onMounted, defineProps } from 'vue'

const props = defineProps({
  adSlot: {
    type: String,
    required: true
  },
  format: {
    type: String,
    default: 'auto'
  },
  position: {
    type: String,
    default: 'horizontal' // 'horizontal' 또는 'vertical'
  },
  responsive: {
    type: String,
    default: 'true'
  }
})

onMounted(() => {
  try {
    // 광고 로드
    ;(window.adsbygoogle = window.adsbygoogle || []).push({})
  } catch (error) {
    console.error('AdSense 광고 로드 실패:', error)
  }
})
</script>

<style scoped>
.ad-container {
  width: 100%;
  margin: 2rem auto;
  text-align: center;
  overflow: hidden;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  min-height: 100px;
}

.ad-container.horizontal {
  max-width: 100%;
  height: auto;
}

.ad-container.vertical {
  max-width: 300px;
  min-height: 600px;
}

@media (max-width: 768px) {
  .ad-container {
    margin: 1rem auto;
  }
  
  .ad-container.vertical {
    max-width: 100%;
    min-height: 250px;
  }
}
</style> 