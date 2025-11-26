import Vue from 'vue'
import VueRouter from 'vue-router'
import Upload from '@/views/Upload.vue'
import History from '@/views/History.vue'
import Edit from '@/views/Edit.vue'

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
    path: '/edit',
    name: 'Edit',
    component: Edit
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

