<template>
  <div class="welcome-panel">
    <!-- 显示 script server logo，单击时显示二维码 -->
    <img 
      :src="imageSrc" 
      alt="script server logo" 
      class="logo-image" 
      @click="handleClick"
    >

    <!-- 欢迎文本 -->
    <div class="welcome-text">
      Welcome to the Script Server. <br> To start, select one of the scripts.
    </div>
  </div>
</template>

<script>
import ConsoleImage from '@/assets/console.png';
import WechartImage from '@/assets/wechart.jpg';
import { mapActions } from 'vuex';

export default {
  name: 'AppWelcomePanel',
  data() {
    return {
      imageSrc: ConsoleImage,  // 默认显示 ConsoleImage
      wechartImageSrc: WechartImage,
      timeoutId: null  // 用于存储setTimeout的ID
    }
  },

  methods: {
    ...mapActions('page', ['setLoading']),
    handleClick() {
      this.imageSrc = this.wechartImageSrc; // 显示二维码
      clearTimeout(this.timeoutId); // 清除先前的定时器

      // 5秒后恢复显示 ConsoleImage
      this.timeoutId = setTimeout(() => {
        this.imageSrc = ConsoleImage;
      }, 5000);
    }
  },

  mounted() {
    this.setLoading(false);
  },

  beforeDestroy() {
    // 清除定时器，防止内存泄漏
    clearTimeout(this.timeoutId);
  }
}
</script>

<style scoped>
.welcome-panel {
  flex: 1;
  color: var(--font-color-medium);
  display: flex;
  text-align: center;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  overflow: hidden;
}

.logo-image {
  width: 15ch;  /* 设置宽度为15个字符的宽度 */
  height: auto; /* 自动调整高度以保持比例 */
  cursor: pointer; /* 鼠标悬停时显示手形光标 */
}

.welcome-text {
  margin-top: 15px;
}

.welcome-cookie-text {
  margin-top: 8px;
}
</style>
