<template>
  <el-container v-if="$route.path !== '/login'" style="height: 100vh">
    <el-aside width="200px" style="background-color: #545c64">
      <div style="padding: 20px; color: white; font-weight: bold; font-size: 16px">
        拼写检查工具
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/interfaces">
          <span>界面配置</span>
        </el-menu-item>
        <el-menu-item index="/rules">
          <span>规则管理</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <span>报告查看</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="background-color: #fff; border-bottom: 1px solid #eee">
        <div style="display: flex; justify-content: space-between; align-items: center; height: 100%">
          <h3>{{ $route.name }}</h3>
          <el-button @click="logout" type="danger" size="small">退出登录</el-button>
        </div>
      </el-header>
      
      <el-main style="background-color: #f0f2f5">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <router-view v-else />
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
}
</style>
