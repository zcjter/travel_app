import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/trips',
    name: 'TripList',
    component: () => import('../views/TripList.vue'),
  },
  {
    path: '/trips/:id',
    name: 'TripDetail',
    component: () => import('../views/TripDetail.vue'),
  },
  {
    path: '/editor',
    name: 'Editor',
    component: () => import('../views/Editor.vue'),
  },
  {
    path: '/editor/:tripId',
    name: 'EditorWithTrip',
    component: () => import('../views/Editor.vue'),
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
