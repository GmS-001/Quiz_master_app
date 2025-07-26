<template>
    <div class="register-container">
      <div class="card shadow-sm">
        <div class="card-body">
          <h3 class="card-title text-center mb-4">Create Account</h3>
          <form @submit.prevent="handleRegister">
            <div class="row">
              <div class="col-md-6 mb-3"><label class="form-label">Full Name</label><input type="text" class="form-control" v-model="formData.fullName" required></div>
              <div class="col-md-6 mb-3"><label class="form-label">Email Address</label><input type="email" class="form-control" v-model="formData.username" required></div>
              <div class="col-md-6 mb-3"><label class="form-label">Password</label><input type="password" class="form-control" v-model="formData.password" required></div>
              <div class="col-md-6 mb-3"><label class="form-label">Qualification</label><input type="text" class="form-control" v-model="formData.qualification"></div>
              <div class="col-md-6 mb-3"><label class="form-label">Date of Birth</label><input type="date" class="form-control" v-model="formData.dob"></div>
              <div class="col-md-6 mb-3"><label class="form-label">Gender</label><select class="form-select" v-model="formData.gender"><option>Male</option><option>Female</option><option>Other</option></select></div>
              <div class="col-12 mb-3"><label class="form-label">Phone Number</label><input type="tel" class="form-control" v-model="formData.phoneNumber"></div>
              <div class="col-12 mb-3"><label class="form-label">Address</label><input type="text" class="form-control" v-model="formData.address"></div>
              <div class="col-md-4 mb-3"><label class="form-label">City</label><input type="text" class="form-control" v-model="formData.city"></div>
              <div class="col-md-4 mb-3"><label class="form-label">State</label><input type="text" class="form-control" v-model="formData.state"></div>
              <div class="col-md-4 mb-3"><label class="form-label">Country</label><input type="text" class="form-control" v-model="formData.country"></div>
            </div>
            <div class="d-grid mt-2">
              <button type="submit" class="btn btn-primary">Register</button>
            </div>
            <div class="text-center mt-3">
              <p>Already have an account? <router-link to="/login">Login here</router-link></p>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../services/api';
  
  export default {
    name: 'RegisterView',
    data() {
      return {
        formData: {
          username: '', password: '', fullName: '', qualification: '',
          dob: '', gender: '', phoneNumber: '', address: '',
          city: '', state: '', country: ''
        }
      }
    },
    methods: {
      async handleRegister() {
        try {
          await api.post('/register', this.formData);
          alert('Registration successful! Please log in.');
          this.$router.push('/login');
        } catch (error) {
          console.error("Registration failed:", error.response.data);
          alert(`Registration failed: ${error.response.data.message}`);
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .register-container {
    max-width: 800px;
    margin: 2rem auto;
  }
  </style>