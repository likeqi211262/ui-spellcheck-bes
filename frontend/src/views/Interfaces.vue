<template>
  <div>
    <el-card>
      <el-button type="primary" @click="showCreateDialog" style="margin-bottom: 20px">
        添加界面
      </el-button>
      
      <el-table :data="interfaces" style="width: 100%">
        <el-table-column prop="interface_name" label="界面名称" />
        <el-table-column prop="interface_path" label="访问路径" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag v-if="row.status === 1" type="success">启用</el-tag>
            <el-tag v-else-if="row.status === 0" type="info">未启用</el-tag>
            <el-tag v-else type="danger">废弃</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="jump_rule" label="跳转规则" />
        <el-table-column label="截图">
          <template #default="{ row }">
            <el-button 
              v-if="row.screenshot_path" 
              type="info" 
              size="small" 
              @click="viewScreenshot(row.id)"
            >
              查看截图
            </el-button>
            <span v-else style="color: #999">暂无</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑界面' : '添加界面'" width="600px">
      <el-form :model="interfaceForm" :rules="formRules" ref="interfaceFormRef" label-width="100px">
        <el-form-item label="界面名称" prop="interface_name">
          <el-input v-model="interfaceForm.interface_name" />
        </el-form-item>
        <el-form-item label="访问路径" prop="interface_path">
          <el-input v-model="interfaceForm.interface_path" placeholder="例如: /admin/login" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="interfaceForm.status" style="width: 100%">
            <el-option label="未启用" :value="0" />
            <el-option label="启用" :value="1" />
            <el-option label="废弃" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="跳转规则">
          <el-input v-model="interfaceForm.jump_rule" type="textarea" placeholder="描述如何访问此界面" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="screenshotDialogVisible" title="界面截图" width="80%">
      <div style="text-align: center">
        <img 
          :src="screenshotUrl" 
          style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px"
          alt="界面截图"
        />
      </div>
      <template #footer>
        <el-button @click="screenshotDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'

const interfaces = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const isEdit = ref(false)
const interfaceFormRef = ref()
const editId = ref(null)
const screenshotDialogVisible = ref(false)
const screenshotUrl = ref('')

const interfaceForm = ref({
  interface_name: '',
  interface_path: '',
  status: 1,
  jump_rule: '',
  creator: 'admin'
})

const formRules = {
  interface_name: [{ required: true, message: '请输入界面名称', trigger: 'blur' }],
  interface_path: [{ required: true, message: '请输入访问路径', trigger: 'blur' }]
}

const loadInterfaces = async () => {
  try {
    const response = await api.get('/interfaces')
    interfaces.value = response.data
  } catch (error) {
    ElMessage.error('加载界面失败')
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  editId.value = null
  interfaceForm.value = {
    interface_name: '',
    interface_path: '',
    status: 1,
    jump_rule: '',
    creator: 'admin'
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  interfaceForm.value = {
    interface_name: row.interface_name,
    interface_path: row.interface_path,
    status: row.status,
    jump_rule: row.jump_rule
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await interfaceFormRef.value.validate()
  
  loading.value = true
  try {
    if (isEdit.value) {
      await api.put(`/interfaces/${editId.value}`, interfaceForm.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/interfaces', interfaceForm.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadInterfaces()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除此界面吗？', '提示', {
      type: 'warning'
    })
    
    await api.delete(`/interfaces/${id}`)
    ElMessage.success('删除成功')
    loadInterfaces()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewScreenshot = (interfaceId) => {
  const token = localStorage.getItem('token')
  screenshotUrl.value = `/api/screenshots/${interfaceId}?token=${token}`
  screenshotDialogVisible.value = true
}

onMounted(() => {
  loadInterfaces()
})
</script>
