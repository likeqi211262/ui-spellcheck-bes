<template>
  <div>
    <el-card>
      <el-button type="primary" @click="showCreateDialog" style="margin-bottom: 20px">
        创建检查任务
      </el-button>
      
      <el-table :data="tasks" style="width: 100%">
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
        <el-table-column prop="executor" label="执行人" />
        <el-table-column prop="start_time" label="开始时间">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-button
              v-if="row.task_status === 2"
              type="primary"
              size="small"
              @click="generateReport(row.id, 'html')"
            >
              生成HTML报告
            </el-button>
            <el-button
              v-if="row.task_status === 2"
              type="success"
              size="small"
              @click="generateReport(row.id, 'excel')"
            >
              生成Excel
            </el-button>
            <el-button
              v-if="row.report_path"
              type="info"
              size="small"
              @click="downloadReport(row.id)"
            >
              下载报告
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createDialogVisible" title="创建检查任务" width="500px">
      <el-form :model="taskForm" :rules="rules" ref="taskFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="task_name">
          <el-input v-model="taskForm.task_name" />
        </el-form-item>
        <el-form-item label="检查范围">
          <el-select v-model="taskForm.check_scope" style="width: 100%">
            <el-option label="全部界面" value="all" />
            <el-option
              v-for="item in interfaces"
              :key="item.id"
              :label="item.interface_name"
              :value="String(item.id)"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="loading">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

const tasks = ref([])
const interfaces = ref([])
const createDialogVisible = ref(false)
const loading = ref(false)
const taskFormRef = ref()

const taskForm = ref({
  task_name: '',
  check_scope: 'all',
  executor: 'admin'
})

const rules = {
  task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }]
}

const loadTasks = async () => {
  try {
    const response = await api.get('/tasks')
    tasks.value = response.data
  } catch (error) {
    ElMessage.error('加载任务失败')
  }
}

const loadInterfaces = async () => {
  try {
    const response = await api.get('/interfaces')
    interfaces.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const showCreateDialog = () => {
  taskForm.value = {
    task_name: `任务-${new Date().toISOString().slice(0, 10)}`,
    check_scope: 'all',
    executor: 'admin'
  }
  createDialogVisible.value = true
}

const handleCreate = async () => {
  await taskFormRef.value.validate()
  
  loading.value = true
  try {
    await api.post('/tasks', taskForm.value)
    ElMessage.success('任务创建成功，正在后台执行')
    createDialogVisible.value = false
    loadTasks()
    
    setTimeout(() => loadTasks(), 3000)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    loading.value = false
  }
}

const generateReport = async (taskId, format) => {
  try {
    const response = await api.post(`/tasks/${taskId}/generate-report?format=${format}`)
    ElMessage.success('报告生成成功')
    loadTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成报告失败')
  }
}

const downloadReport = async (taskId) => {
  try {
    const response = await api.get(`/reports/download/${taskId}`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `report_${taskId}.html`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

onMounted(() => {
  loadTasks()
  loadInterfaces()
})
</script>
