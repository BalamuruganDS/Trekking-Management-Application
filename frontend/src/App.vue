<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-3">
      <a class="navbar-brand fw-bold" href="#">🏔️ Trekking App</a>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
        <ul class="navbar-nav align-items-center">

          <li v-if="!isLoggedIn" class="nav-item">
            <router-link class="nav-link" to="/login">
              Login
            </router-link>
          </li>

          <li v-if="!isLoggedIn" class="nav-item">
            <router-link class="nav-link" to="/register">
              Register
            </router-link>
          </li>

          <li v-if="isLoggedIn" class="nav-item me-3">
            <span class="navbar-text text-light">
              <strong>{{ userName }}</strong>
              <span class="ms-2">
                Role: <strong>{{ userRole }}</strong>
              </span>
            </span>
          </li>

          <li v-if="isLoggedIn" class="nav-item">
            <button 
              class="btn btn-outline-danger btn-sm" 
              @click="handleLogout"
            >
              Logout
            </button>
          </li>

        </ul>
      </div>
    </nav>

      <main class="container my-4">
        <router-view />
      </main>
  </div>
</template>

<script>
export default {
  name: 'App',

  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token');
    },

    userName() {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      return user.full_name || '';
    },

    userRole() {
      return localStorage.getItem('role') || '';
    }
  },

  methods: {
    handleLogout() {
      localStorage.clear();
      this.$router.push('/login');
    }
  }
};
</script>