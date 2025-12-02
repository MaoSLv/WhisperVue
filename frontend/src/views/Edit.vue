<template>
  <div class="edit-container">
    <div class="subtitle-editor-table">
      <el-table 
        :data="segments" 
        style="width: 100%" 
        class="clean-table"
        :show-header="true" 
        stripe
      >
        <el-table-column
          type="index"
          label="#"
          width="60"
          align="center"
          header-align="center"
          class-name="index-column"
        ></el-table-column>
        
        <el-table-column label="开始时间" width="140" header-align="center">
          <template slot-scope="scope">
            <el-input 
              v-model="scope.row.startFormatted" 
              size="small" 
              placeholder="00:00:00"
              class="time-input"
              @blur="updateStartTime(scope.$index, scope.row.startFormatted)"
            ></el-input>
          </template>
        </el-table-column>

        <el-table-column label="结束时间" width="140" header-align="center">
          <template slot-scope="scope">
            <el-input 
              v-model="scope.row.endFormatted" 
              size="small" 
              placeholder="00:00:00"
              class="time-input"
              @blur="updateEndTime(scope.$index, scope.row.endFormatted)"
            ></el-input>
          </template>
        </el-table-column>

        <el-table-column label="字幕内容" header-align="center">
          <template slot-scope="scope">
            <el-input 
              type="textarea"
              :autosize="autosizeConfig"
              v-model="scope.row.text"
              placeholder="请输入字幕内容"
            ></el-input>
          </template>
        </el-table-column>

        <el-table-column label="音频试听" width="120" align="center" header-align="center">
          <template slot-scope="scope">
            <el-button 
              @click="playAudio(scope.row)" 
              type="text" 
              size="small" 
              icon="el-icon-video-play"
              :disabled="!audioUrl"
            >
              试听
            </el-button>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" align="center" header-align="center">
          <template slot-scope="scope">
            <el-button
              type="danger"
              size="small"
              icon="el-icon-delete"
              @click="deleteSegment(scope.$index)"
              circle
            >
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
// 辅助函数：将秒数转换为 M:SS.ms 格式
const formatSeconds = (seconds) => {
  const totalMs = Math.round(seconds * 1000)
  const ms = (totalMs % 1000).toString().padStart(3, '0')
  const s = Math.floor(totalMs / 1000)
  const m = Math.floor(s / 60)
  const sec = (s % 60).toString().padStart(2, '0')
  return `${m}:${sec}.${ms}`
}

// 辅助函数：将时间字符串转换为秒数
const parseTime = (timeStr) => {
  const parts = timeStr.split(':')
  if (parts.length === 2) {
    const m = parseInt(parts[0]) || 0
    const sParts = parts[1].split('.')
    const s = parseInt(sParts[0]) || 0
    const ms = parseInt(sParts[1]) || 0
    return m * 60 + s + ms / 1000
  }
  return 0
}

export default {
  name: 'Edit',
  data() {
    return {
      segments: [],
      audioUrl: '',
      audioPlayer: null,
      info: {},
      autosizeConfig: { minRows: 1, maxRows: 1 }
    }
  },
  mounted() {
    const id = this.$route.query.id
    if (!id) {
      this.$message.error('缺少历史记录 ID')
      return
    }

    this.$axios
      .get(`/history/detail/${id}`)
      .then(response => {
        const record = response.data || {}

        // 处理音频 URL（从服务端获取）
        if (record.uuid_filename) {
          this.audioUrl = `http://localhost:8000/media/${record.uuid_filename}`
        } else {
          console.warn('未找到音频文件名 uuid_filename')
        }

        // 处理 segments 数据（original_segments_json 为字符串化的 JSON）
        let segmentsRaw = []
        if (record.original_segments_json) {
          try {
            segmentsRaw = JSON.parse(record.original_segments_json)
          } catch (e) {
            console.error('解析 original_segments_json 失败:', e)
            this.$message.error('字幕数据解析失败')
          }
        }

        if (Array.isArray(segmentsRaw) && segmentsRaw.length > 0) {
          this.segments = segmentsRaw.map(s => ({
            ...s,
            // 清理文本中的多余换行符和空白字符，但保留必要的空格
            text: (s.text || '')
              .replace(/\r\n/g, ' ')
              .replace(/\n/g, ' ')
              .replace(/\r/g, ' ')
              .replace(/\s+/g, ' ')
              .trim(),
            startFormatted: formatSeconds(s.start),
            endFormatted: formatSeconds(s.end)
          }))
          this.$nextTick(() => {
            this.autosizeConfig = { minRows: 1, maxRows: 5 }
          })
        } else {
          this.$message.warning('未找到字幕数据')
        }
      })
      .catch(error => {
        console.error('获取数据失败:', error)
        this.$message.error('获取数据失败')
      })
  },
  methods: {
    updateStartTime(index, timeStr) {
      const seconds = parseTime(timeStr)
      if (seconds >= 0) {
        this.segments[index].start = seconds
        this.segments[index].startFormatted = formatSeconds(seconds)
      }
    },
    updateEndTime(index, timeStr) {
      const seconds = parseTime(timeStr)
      if (seconds >= 0) {
        this.segments[index].end = seconds
        this.segments[index].endFormatted = formatSeconds(seconds)
      }
    },
    deleteSegment(index) {
      if (index >= 0 && index < this.segments.length) {
        this.segments.splice(index, 1)
      }
    },
    playAudio(row) {
      if (!this.audioUrl) {
        this.$message.warning('音频文件不存在')
        return
      }
      
      // 创建或获取音频播放器
      if (!this.audioPlayer) {
        this.audioPlayer = new Audio(this.audioUrl)
      } else {
        this.audioPlayer.src = this.audioUrl
      }
      
      // 设置播放起始时间
      this.audioPlayer.currentTime = row.start
      
      // 播放音频
      this.audioPlayer.play().catch(err => {
        console.error('播放失败:', err)
        this.$message.error('音频播放失败')
      })
      
      // 播放到结束时间时停止
      const checkTime = () => {
        if (this.audioPlayer.currentTime >= row.end) {
          this.audioPlayer.pause()
          this.audioPlayer.removeEventListener('timeupdate', checkTime)
        }
      }
      this.audioPlayer.addEventListener('timeupdate', checkTime)
    }
  },
  beforeDestroy() {
    // 清理音频播放器
    if (this.audioPlayer) {
      this.audioPlayer.pause()
      this.audioPlayer = null
    }
    // 释放音频URL对象
    if (this.audioUrl && this.audioUrl.startsWith('blob:')) {
      URL.revokeObjectURL(this.audioUrl)
    }
  }
}
</script>

<style scoped>
.edit-container {
  padding: 20px;
  min-height: 100%;
  background-color: #f5f7fa;
}

/* 容器居中 */
.subtitle-editor-table {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 优化表格样式，使其更像编辑工具而不是数据报表 */
.clean-table ::v-deep .el-table__header-wrapper {
  background-color: #f5f7fa; /* 表头浅灰背景 */
}

/* 隐藏表格内部的边框，使外观更简洁 */
.clean-table ::v-deep .el-table__row > td,
.clean-table ::v-deep .el-table__header-wrapper th {
  border: none;
}

/* 恢复底部分割线 */
.clean-table ::v-deep .el-table__body tr {
  border-bottom: 1px solid #ebeef5;
}

/* 序号列和时间列的字体优化 */
.clean-table ::v-deep .index-column {
  color: #909399; /* 灰色，不突出 */
  font-weight: bold;
}

/* 时间输入框样式优化 */
.time-input ::v-deep .el-input__inner {
  padding: 0 5px;
  text-align: center;
  font-family: monospace; /* 时间用等宽字体更好看 */
  color: #606266;
  border: 1px solid transparent; /* 默认边框透明 */
}

.time-input ::v-deep .el-input__inner:focus {
  border: 1px solid #409eff; /* 聚焦时显示边框 */
}

/* 文本域聚焦时突出显示 */
.clean-table ::v-deep .el-textarea__inner {
  border: none !important; /* 移除内部边框 */
  padding: 5px 0;
  line-height: 1.6;
  font-size: 14px;
  resize: none;
  white-space: pre-wrap; /* 保留空格，但允许换行 */
  word-wrap: break-word; /* 长单词自动换行 */
  overflow-wrap: break-word; /* 兼容性 */
}

/* 文本域聚焦时，给单元格增加高亮效果 */
.clean-table ::v-deep .el-table__row.current-row > td {
  background-color: #e6f7ff; /* 浅蓝高亮行 */
}
</style>

