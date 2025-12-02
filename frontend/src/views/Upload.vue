<template>
  <div class="upload-container" v-loading="loading" element-loading-text="音频识别中，请稍等">
    <el-card class="upload-card" shadow="always">
        <div class="header">
          <h1 class="title">上传音频</h1>
          <p class="subtitle">支持拖拽上传，格式 mp3 / wav / m4a / aac / mp4 / mov / mkv 等，最大 10 MB</p>
        </div>

        <el-upload class="uploader" drag action="#" :auto-upload="false" :limit="1" :on-exceed="onExceed"
          :on-change="onFileChange" :file-list="fileList" :accept="acceptTypes">
          <i class="el-icon-upload"></i>
          <div class="el-upload__text">将文件拖到此处，或<em>点击选择</em></div>
          <div class="el-upload__tip" slot="tip">请选择音频文件，单次仅限 1 个</div>
        </el-upload>

        <div class="actions">
          <el-button type="primary" @click="doUpload" :disabled="!fileList.length" :loading="loading">开始处理</el-button>
          <el-button @click="reset" :disabled="loading">重置</el-button>
        </div>
      </el-card>
  </div>
</template>

<script>
export default {
  name: 'Upload',
  data() {
    return {
      fileList: [],
      acceptTypes: 'audio/*,video/*,.mp3,.wav,.m4a,.aac,.mp4,.webm,.mov,.mkv',
      loading: false
    }
  },
  methods: {
    onExceed() {
      this.$message.warning('仅允许上传 1 个文件，请先移除已选文件')
    },
    onFileChange(file, fileList) {
      // keep only latest
      const latest = fileList.slice(-1)
      // validate type: audio or video
      const isMedia =
        /^(audio|video)\//.test(file.raw.type) ||
        /\.(mp3|wav|m4a|aac|mp4|webm|mov|mkv)$/i.test(file.name)
      const MAX_SIZE_MB = localStorage.getItem('MAX_UPLOAD_SIZE_MB') || 10;
      const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

      if (!isMedia) {
        this.$message.error('请选择音频或视频文件')
        this.reset()
        return
      }
      if (file.size > MAX_SIZE_BYTES) {
        this.$message.error(`文件大小不能超过 ${MAX_SIZE_MB} MB`);
        this.reset();
        return;
      }
      this.fileList = latest
    },
    async doUpload() {
      if (!this.fileList.length) {
        this.$message.warning('请先选择文件')
        return
      }
      
      this.loading = true
      try {
        const rawFile = this.fileList[0].raw
        const formData = new FormData()
        formData.append('file', rawFile)
        
        // 创建本地音频URL用于播放
        const audioUrl = URL.createObjectURL(rawFile)
        
        const response = await this.$axios.post('/upload/audio', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        this.$message.success('上传成功')
        
        // 跳转到 Edit 页面
        this.$router.push({ name: 'Edit', query: { id: response.data } })
      } catch (error) {
        this.$message.error('上传失败，请重试')
        console.error('Upload error:', error)
      } finally {
        this.loading = false
      }
    },
    reset() {
      this.fileList = []
    }
  },
  beforeDestroy() {
    if (this.audioUrl) {
      URL.revokeObjectURL(this.audioUrl)
    }
  }
}
</script>

<style scoped>
.upload-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  position: relative;
}

.upload-card {
  width: 680px;
  max-width: 100%;
  border-radius: 12px;
  border: 1px solid #ebeef5;
  transform: translateY(-35%);
}

.header {
  text-align: center;
  margin-bottom: 12px;
}

.title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #1f2d3d;
}

.subtitle {
  margin: 6px 0 0 0;
  font-size: 13px;
  color: #909399;
}

.uploader {
  margin-top: 20px;
  max-width: 420px;
  margin-left: auto;
  margin-right: auto;
  text-align: center;
}

.uploader .el-upload {
  display: inline-block;
}

.uploader .el-upload-dragger {
  margin-left: auto;
  margin-right: auto;
}

.actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
</style>

