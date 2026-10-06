<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-4">
      <div class="card shadow-sm">
        <div class="card-body">
          <h3 class="card-title text-center mb-4">Trekking App Login</h3>
          <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="email" type="email" class="form-control" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" required />
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api';

export default {
  name: 'LoginView',
  data() {
    return {
      
      email: '',
      password: '',
      errorMessage: '',
    };
  },
  methods: {
    async handleLogin() {
      this.errorMessage = '';
      try {
        const response = await api.post('/api/user/login', {
          email: this.email,
          password: this.password,
        });

        const { access_token, user } = response.data;
        
        // Save auth data
        localStorage.setItem('token', access_token);
        localStorage.setItem('role', user.role);
        localStorage.setItem('user', JSON.stringify(user));

        // Route based on user role
        if (user.role === 'Admin') {
          this.$router.push('/admin');
        } else if (user.role === 'Staff') {
          this.$router.push('/staff');
        } else {
          this.$router.push('/user');
        }
      } catch (err) {
        this.errorMessage = 
          err.response?.data?.error || 
          err.response?.data?.message || 
          'Login failed. Please check your credentials.';
      }
    },
  },
};
</script>


