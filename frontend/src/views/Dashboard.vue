<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="font-size: 32px; color: #409EFF">{{ stats.totalTasks }}</div>
            <div style="margin-top: 10px; color: #666">总任务数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="font-size: 32px; color: #67C23A">{{ stats.completedTasks }}</div>
            <div style="margin-top: 10px; color: #666">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="font-size: 32px; color: #E6A23C">{{ stats.runningTasks }}</div>
            <div style="margin-top: 10px; color: #666">运行中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="font-size: 32px; color: #F56C6C">{{ stats.totalErrors }}</div>
            <div style="margin-top: 10px; color: #666">错误总数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>快速开始</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-button type="primary" @click="$router.push('/tasks')" style="width: 100%">
            创建检查任务
          </el-button>
        </el-col>
        <el-col :span="8">
          <el-button @click="$router.push('/rules')" style="width: 100%">
            管理拼写规则
          </el-button>
        </el-col>
        <el-col :span="8">
          <el-button @click="$router.push('/reports')" style="width: 100%">
            查看报告
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>最近任务</span>
      </template>
      <el-table :data="recentTasks" style="width: 100%">
        <el-table-column prop="task_name" label="任务名称" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag v-if="row.task_status === 0">待执行</el-tag>
            <el-tag v-else-if="row.task_status === 1" type="warning">执行中</el-tag>
            <el-tag v-else-if="row.task_status === 2" type="success">已完成</el-tag>
            <el-tag v-else type="danger">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_count" label="错误数量" />
        <el-table-column prop="start_time" label="开始时间">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'

const stats = ref({
  totalTasks: 0,
  completedTasks: 0,
  runningTasks: 0,
  totalErrors: 0
})

const recentTasks = ref([])

const loadStats = async () => {
  try {
    const [tasksRes] = await Promise.all([
      api.get('/tasks')
    ])
    
    const tasks = tasksRes.data
    stats.value.totalTasks = tasks.length
    stats.value.completedTasks = tasks.filter(t => t.task_status === 2).length
    stats.value.runningTasks = tasks.filter(t => t.task_status === 1).length
    stats.value.totalErrors = tasks.reduce((sum, t) => sum + (t.error_count || 0), 0)
    
    recentTasks.value = tasks.slice(0, 5)
  } catch (error) {
    console.error(error)
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

onMounted(() => {
  loadStats()
})
</script>
