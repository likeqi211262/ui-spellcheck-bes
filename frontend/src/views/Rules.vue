<template>
  <div>
    <el-card>
      <el-button type="primary" @click="showCreateDialog" style="margin-bottom: 20px">
        添加规则
      </el-button>
      
      <el-table :data="rules" style="width: 100%">
        <el-table-column prop="word" label="词汇" />
        <el-table-column label="类型">
          <template #default="{ row }">
            <el-tag v-if="row.word_type === 'common'">通用</el-tag>
            <el-tag v-else-if="row.word_type === 'industry'" type="success">行业术语</el-tag>
            <el-tag v-else type="info">自定义</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="白名单">
          <template #default="{ row }">
            <el-tag v-if="row.is_whitelist === 1" type="success">是</el-tag>
            <el-tag v-else type="info">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="language" label="语言" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑规则' : '添加规则'" width="500px">
      <el-form :model="ruleForm" :rules="formRules" ref="ruleFormRef" label-width="100px">
        <el-form-item label="词汇" prop="word">
          <el-input v-model="ruleForm.word" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="ruleForm.word_type" style="width: 100%">
            <el-option label="通用词汇" value="common" />
            <el-option label="行业术语" value="industry" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="白名单">
          <el-switch v-model="ruleForm.is_whitelist" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="语言">
          <el-select v-model="ruleForm.language" style="width: 100%">
            <el-option label="英文" value="en" />
            <el-option label="中文" value="zh" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="ruleForm.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'

const rules = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const isEdit = ref(false)
const ruleFormRef = ref()
const editId = ref(null)

const ruleForm = ref({
  word: '',
  word_type: 'common',
  is_whitelist: 0,
  language: 'en',
  remark: ''
})

const formRules = {
  word: [{ required: true, message: '请输入词汇', trigger: 'blur' }]
}

const loadRules = async () => {
  try {
    const response = await api.get('/rules')
    rules.value = response.data
  } catch (error) {
    ElMessage.error('加载规则失败')
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  editId.value = null
  ruleForm.value = {
    word: '',
    word_type: 'common',
    is_whitelist: 0,
    language: 'en',
    remark: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  ruleForm.value = {
    word: row.word,
    word_type: row.word_type,
    is_whitelist: row.is_whitelist,
    language: row.language,
    remark: row.remark
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await ruleFormRef.value.validate()
  
  loading.value = true
  try {
    if (isEdit.value) {
      await api.put(`/rules/${editId.value}`, ruleForm.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/rules', ruleForm.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadRules()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除此规则吗？', '提示', {
      type: 'warning'
    })
    
    await api.delete(`/rules/${id}`)
    ElMessage.success('删除成功')
    loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadRules()
})
</script>
