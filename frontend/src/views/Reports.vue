<template>
  <div>
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true">
        <el-form-item label="任务">
          <el-select v-model="selectedTask" placeholder="选择任务" @change="loadErrors" clearable>
            <el-option
              v-for="task in tasks"
              :key="task.id"
              :label="task.task_name"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="filterSeverity" @change="loadErrors" clearable>
            <el-option label="低" :value="1" />
            <el-option label="中" :value="2" />
            <el-option label="高" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否修复">
          <el-select v-model="filterFixed" @change="loadErrors" clearable>
            <el-option label="未修复" :value="0" />
            <el-option label="已修复" :value="1" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="selectedTask">
      <el-descriptions title="任务统计" :column="3" border style="margin-bottom: 20px">
        <el-descriptions-item label="总错误数">{{ statistics.total_errors }}</el-descriptions-item>
        <el-descriptions-item label="已修复">{{ statistics.fixed_errors }}</el-descriptions-item>
        <el-descriptions-item label="未修复">{{ statistics.unfixed_errors }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card style="margin-top: 20px">
      <el-table :data="errors" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="error_text" label="错误文本" />
        <el-table-column label="错误类型">
          <template #default="{ row }">
            <el-tag v-if="row.error_type === 'spelling'">拼写错误</el-tag>
            <el-tag v-else-if="row.error_type === 'grammar'" type="warning">语法错误</el-tag>
            <el-tag v-else type="info">{{ row.error_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="严重程度">
          <template #default="{ row }">
            <el-tag v-if="row.severity_level === 1" type="info">低</el-tag>
            <el-tag v-else-if="row.severity_level === 2" type="warning">中</el-tag>
            <el-tag v-else type="danger">高</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="correct_suggest" label="修正建议" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag v-if="row.is_fixed === 1" type="success">已修复</el-tag>
            <el-tag v-else type="danger">未修复</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              v-if="row.is_fixed === 0"
              type="success"
              size="small"
              @click="markAsFixed(row.id)"
            >
              标记修复
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

const tasks = ref([])
const errors = ref([])
const statistics = ref({})
const selectedTask = ref(null)
const filterSeverity = ref(null)
const filterFixed = ref(0)

const loadTasks = async () => {
  try {
    const response = await api.get('/tasks')
    tasks.value = response.data
  } catch (error) {
    ElMessage.error('加载任务失败')
  }
}

const loadErrors = async () => {
  if (!selectedTask.value) {
    errors.value = []
    return
  }
  
  try {
    const params = {
      task_id: selectedTask.value,
      limit: 100
    }
    
    if (filterSeverity.value !== null) {
      params.severity = filterSeverity.value
    }
    
    if (filterFixed.value !== null) {
      params.is_fixed = filterFixed.value
    }
    
    const response = await api.get('/reports/errors', { params })
    errors.value = response.data
  } catch (error) {
    ElMessage.error('加载错误列表失败')
  }
}

const loadStatistics = async () => {
  if (!selectedTask.value) return
  
  try {
    const response = await api.get(`/reports/statistics/${selectedTask.value}`)
    statistics.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const markAsFixed = async (errorId) => {
  try {
    await api.put(`/reports/errors/${errorId}/fix`)
    ElMessage.success('已标记为修复')
    loadErrors()
    loadStatistics()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadTasks()
})
</script>
