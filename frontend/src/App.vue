<template>
  <div id="app">
    <el-container style="height: 100vh;">
      <el-aside width="240px" class="sidebar">
        <div class="sidebar-header">
          <div class="logo">
            <img src="/static/favicon.ico" alt="WhisperVue Logo" class="logo-img">
          </div>
          <h1 class="app-title">WhisperVue</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          class="sidebar-menu"
          background-color="#f8f9fa"
          text-color="#333"
          active-text-color="#409EFF">
          <el-menu-item index="/upload">
            <i class="el-icon-upload2"></i>
            <span slot="title">上传</span>
          </el-menu-item>
          <el-menu-item index="/history">
            <i class="el-icon-time"></i>
            <span slot="title">历史记录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main-content">
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    activeMenu() {
      return this.$route.path
    }
  }
}
</script>

<style>
body {
  margin: 0;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #1f2d3d;
  background: #ffffff;
  min-height: 100vh;
}
  
.sidebar {
  background-color: #f8f9fa;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #e4e7ed;
}

.logo {
  margin-bottom: 12px;
}

.logo-img {
  width: 48px;
  height: 48px;
  margin: 0 auto;
  display: block;
  border-radius: 12px;
  object-fit: contain;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0;
  letter-spacing: -0.5px;
}

.sidebar-menu {
  border-right: none;
  padding: 10px 0;
}

.sidebar-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  margin: 4px 12px;
  border-radius: 8px;
}

.sidebar-menu .el-menu-item:hover {
  background-color: #EBEDEE !important;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #E7E9E9 !important;
  color: #000 !important;
}

.sidebar-menu .el-menu-item i {
  margin-right: 8px;
  font-size: 18px;
}

.main-content {
  background-color: #ffffff;
  padding: 0;
  overflow-y: auto;
}

body > .el-container {
  margin-bottom: 40px;
}

</style>
