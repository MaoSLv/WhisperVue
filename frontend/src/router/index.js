import Vue from 'vue'
import VueRouter from 'vue-router'
import Upload from '@/views/Upload.vue'
import History from '@/views/History.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/upload',
    name: 'Upload',
    component: Upload
  },
  {
    path: '/history',
    name: 'History',
    component: History
  },
  {
    path: '/',
    redirect: '/upload'
  }
]

const router = new VueRouter({
  mode: 'history',
  base: '/',
  routes
})

export default router

