<template>
  <div class="history-container">
    <h1 class="page-title">历史记录</h1>
    <el-card shadow="never" v-loading="loading">
      <div class="empty-state" v-if="!loading && total === 0">
        <i class="el-icon-document"></i>
        <p>暂无历史记录</p>
      </div>

      <div v-else>
        <el-table
          :data="historyList"
          stripe
          border
          style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" align="center" header-align="center"></el-table-column>
          <el-table-column prop="original_filename" label="原始文件名" show-overflow-tooltip align="center" header-align="center"></el-table-column>
          <el-table-column label="时长" width="120" align="center" header-align="center">
            <template slot-scope="scope">
              {{ formatDuration(scope.row.duration) }}
            </template>
          </el-table-column>
          <el-table-column label="编辑状态" width="120" align="center" header-align="center">
            <template slot-scope="scope">
              <el-tag
                type="success"
                v-show="Number(scope.row.is_edited) === 0"
              >
                未编辑
              </el-tag>
              <el-tag
                v-show="Number(scope.row.is_edited) === 1"
              >
                已编辑
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="upload_time" label="上传时间" width="200" align="center" header-align="center"></el-table-column>
          <el-table-column prop="model_config" label="模型精度" width="130" align="center" header-align="center"></el-table-column>
          <el-table-column label="文件大小" width="140" align="center" header-align="center">
            <template slot-scope="scope">
              {{ formatFileSize(scope.row.file_size_bytes) }}
            </template>
          </el-table-column>
          <el-table-column label="播放" width="120" align="center" header-align="center">
            <template slot-scope="scope">
              <el-button
                type="text"
                :icon="currentPlayingId === scope.row.id && isPlaying ? 'el-icon-video-pause' : 'el-icon-video-play'"
                @click="togglePlay(scope.row)"
              >
                {{ currentPlayingId === scope.row.id && isPlaying ? '暂停' : '播放' }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right" align="center" header-align="center">
            <template slot-scope="scope">
              <el-button size="mini" @click="viewDetail(scope.row)">查看</el-button>
              <el-button size="mini" type="danger" @click="deleteRecord(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrapper">
          <el-pagination
            background
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            :current-page.sync="page"
            :page-size="pageSize"
            :page-sizes="pageSizes"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
          </el-pagination>
        </div>
      </div>
    </el-card>

    <!-- 底部迷你播放器（居中且不超出 el-main 宽度） -->
    <div
      class="bottom-audio-player"
      v-if="currentAudioUrl"
    >
      <div class="bottom-audio-inner">
        <div class="player-info">
          <span class="player-label">正在播放：</span>
          <span class="player-filename">
            {{ currentPlayingRow && currentPlayingRow.original_filename }}
          </span>
        </div>
        <audio
          ref="bottomAudio"
          :src="currentAudioUrl"
          controls
          @ended="onAudioEnded"
        ></audio>
        <el-button
          class="player-close"
          type="text"
          icon="el-icon-close"
          @click="closePlayer"
        ></el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'History',
  data() {
    return {
      historyList: [],
      page: 1,
      pageSize: 5,
      pageSizes: [5, 10, 20, 50],
      total: 0,
      totalPages: 0,
      loading: false,
      currentPlayingId: null,
      currentAudioUrl: '',
      currentPlayingRow: null,
      isPlaying: false
    }
  },
  mounted() {
    this.loadHistory()
  },
  methods: {
    async loadHistory() {
      this.loading = true
      try {
        const res = await this.$axios.get('/history/list', {
          params: {
            page: this.page,
            page_size: this.pageSize
          }
        })
        const data = res.data || {}
        this.historyList = data.data || []
        this.total = data.total || 0
        this.totalPages = data.total_pages || 0
      } catch (e) {
        this.$message.error('获取历史记录失败')
        console.error('loadHistory error:', e)
      } finally {
        this.loading = false
      }
    },
    handleSizeChange(size) {
      this.pageSize = size
      this.page = 1
      this.loadHistory()
    },
    handleCurrentChange(p) {
      this.page = p
      this.loadHistory()
    },
    togglePlay(row) {
      const url = `http://localhost:8000/media/${row.uuid_filename}`

      // 如果当前就是这一行，做播放/暂停切换
      if (this.currentPlayingId === row.id && this.$refs.bottomAudio) {
        if (this.isPlaying) {
          this.$refs.bottomAudio.pause()
          this.isPlaying = false
        } else {
          this.$refs.bottomAudio.play()
          this.isPlaying = true
        }
        return
      }

      // 切换到新的音频
      this.currentAudioUrl = url
      this.currentPlayingId = row.id
      this.currentPlayingRow = row
      this.$nextTick(() => {
        if (this.$refs.bottomAudio) {
          this.$refs.bottomAudio.play()
          this.isPlaying = true
        }
      })
    },
    onAudioEnded() {
      this.isPlaying = false
      this.currentPlayingId = null
    },
    closePlayer() {
      if (this.$refs.bottomAudio) {
        this.$refs.bottomAudio.pause()
      }
      this.isPlaying = false
      this.currentPlayingId = null
      this.currentAudioUrl = ''
      this.currentPlayingRow = null
    },
    formatDuration(seconds) {
      if (!seconds && seconds !== 0) return '-'
      const s = Number(seconds) || 0
      if (s < 60) {
        return s.toFixed(1) + ' 秒'
      }
      const m = Math.floor(s / 60)
      const remain = Math.floor(s % 60)
      return `${m} 分 ${remain} 秒`
    },
    formatFileSize(bytes) {
      if (!bytes && bytes !== 0) return '-'
      const b = Number(bytes) || 0
      if (b < 1024) return b + ' B'
      const kb = b / 1024
      if (kb < 1024) return kb.toFixed(1) + ' KB'
      const mb = kb / 1024
      if (mb < 1024) return mb.toFixed(2) + ' MB'
      const gb = mb / 1024
      return gb.toFixed(2) + ' GB'
    },
    viewDetail(row) {
      this.$message.info(`查看 ${row.original_filename} 的详情（功能待实现）`)
    },
    deleteRecord(row) {
      this.$confirm('确定要删除这条记录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 这里暂时只做前端提示，如需真正删除可调用后端接口
        this.$message.success('删除成功（示例，未真正删除）')
        this.loadHistory()
      }).catch(() => {
        this.$message.info('已取消删除')
      })
    }
  }
}
</script>

<style scoped>
.history-container {
  padding: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0 0 20px 0;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #909399;
}

.empty-state i {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.bottom-audio-player {
  position: fixed;
  left: 240px; /* 与 el-aside 宽度保持一致，不超出 el-main */
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: transparent;
  pointer-events: none; /* 只让内部内容响应事件 */
}

.bottom-audio-inner {
  margin: 0 auto;
  max-width: 960px;
  padding: 8px 16px;
  background: #ffffff;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  border-radius: 8px 8px 0 0;
  pointer-events: auto; /* 内部可以点击 */
}

.player-info {
  font-size: 13px;
  color: #606266;
  max-width: 40%;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.player-label {
  color: #909399;
  margin-right: 4px;
}

.player-filename {
  font-weight: 500;
}

.player-close {
  margin-left: 8px;
}
</style>

