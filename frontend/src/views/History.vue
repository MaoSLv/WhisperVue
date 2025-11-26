<template>
  <div class="history-container">
    <h1 class="page-title">历史记录</h1>
    <el-card shadow="never">
      <div class="empty-state" v-if="historyList.length === 0">
        <i class="el-icon-document"></i>
        <p>暂无历史记录</p>
      </div>
      <el-table
        v-else
        :data="historyList"
        stripe
        style="width: 100%">
        <el-table-column prop="fileName" label="文件名" width="300"></el-table-column>
        <el-table-column prop="uploadTime" label="上传时间" width="200"></el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === '已完成' ? 'success' : 'info'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template slot-scope="scope">
            <el-button size="mini" @click="viewDetail(scope.row)">查看</el-button>
            <el-button size="mini" type="danger" @click="deleteRecord(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'History',
  data() {
    return {
      historyList: []
    }
  },
  mounted() {
    this.loadHistory()
  },
  methods: {
    loadHistory() {
      // 这里先使用模拟数据
      this.historyList = []
    },
    viewDetail(row) {
      this.$message.info(`查看 ${row.fileName} 的详情`)
    },
    deleteRecord(row) {
      this.$confirm('确定要删除这条记录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message.success('删除成功')
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
</style>

