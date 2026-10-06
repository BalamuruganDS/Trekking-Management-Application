<template>
  <div class="row justify-content-center mt-4">
    <div class="col-md-5">
      <div class="card shadow-sm">
        <div class="card-body">
          <h3 class="card-title text-center mb-4">Create Trekker Account</h3>
          
          <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
          <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

          <form @submit.prevent="handleRegister">
            <div class="mb-3">
              <label class="form-label">Full Name</label>
              <input v-model="fullName" type="text" class="form-control" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="email" type="email" class="form-control" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Contact Number</label>
              <input v-model="contactNumber" type="text" class="form-control" placeholder="Optional" />
            </div>

            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" required />
            </div>

            <button type="submit" class="btn btn-success w-100">Register</button>
          </form>

          <p class="text-center mt-3 mb-0 text-muted">
            Already have an account? 
            <router-link to="/login">Login here</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api';

export default {
  name: 'RegisterView',
  data() {
    return {
      fullName: '',
      email: '',
      contactNumber: '',
      password: '',
      errorMessage: '',
      successMessage: ''
    };
  },
  methods: {
    async handleRegister() {
      this.errorMessage = '';
      this.successMessage = '';
      try {
        const response = await api.post('/api/user/register', {
          full_name: this.fullName,
          email: this.email,
          contact_number: this.contactNumber,
          password: this.password
        });

        this.successMessage = response.data.message || 'Registration successful!';
        setTimeout(() => {
          this.$router.push('/login');
        }, 1500);
      } catch (err) {
        this.errorMessage = err.response?.data?.error || 'Registration failed.';
      }
    }
  }
};
</script>