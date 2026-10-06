import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import AdminDashboard from '../views/AdminDashboard.vue';
import StaffDashboard from '../views/StaffDashboard.vue';
import UserDashboard from '../views/UserDashboard.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  { path: '/admin', component: AdminDashboard, meta: { requiresAuth: true, role: 'Admin' } },
  { path: '/staff', component: StaffDashboard, meta: { requiresAuth: true, role: 'Staff' } },
  { path: '/user', component: UserDashboard, meta: { requiresAuth: true, role: 'Trekker' } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('role');

  if (to.meta.requiresAuth) {
    if (!token) return next('/login');
    if (to.meta.role && to.meta.role !== userRole) return next('/login');
  }
  next();
});

export default router;

// import { createRouter, createWebHistory } from 'vue-router';
// import LoginView from '../views/LoginView.vue';
// import RegisterView from '../views/RegisterView.vue';
// import AdminDashboard from '../views/AdminDashboard.vue';
// import StaffDashboard from '../views/StaffDashboard.vue';
// import UserDashboard from '../views/UserDashboard.vue';

// const routes = [
//   { path: '/', redirect: '/login' },
//   { path: '/login', component: LoginView },
//   { path: '/register', component: RegisterView },
//   { path: '/admin', component: AdminDashboard, meta: { requiresAuth: true, role: 'Admin' } },
//   { path: '/staff', component: StaffDashboard, meta: { requiresAuth: true, role: 'Staff' } },
//   { path: '/user', component: UserDashboard, meta: { requiresAuth: true, role: 'Trekker' } },
// ];

// const router = createRouter({
//   history: createWebHistory(),
//   routes,
// });

// router.beforeEach((to, from, next) => {
//   const token = localStorage.getItem('token');
//   const userRole = localStorage.getItem('role');

//   if (to.meta.requiresAuth) {
//     if (!token) return next('/login');
//     if (to.meta.role && to.meta.role !== userRole) return next('/login');
//   }
//   next();
// });

// export default router;