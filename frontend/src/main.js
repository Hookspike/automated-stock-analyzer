import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 创建Vue应用
const app = createApp(App)

// 注册全局属性
app.config.globalProperties.$api = api
app.config.globalProperties.$echarts = window.echarts

// 挂载应用
app.mount('#app')
