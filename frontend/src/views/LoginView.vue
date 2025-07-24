<template>
    <div class="login-container">
      <div class="card shadow-sm">
        <div class="card-body">
          <h3 class="card-title text-center mb-4">Login</h3>
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label for="username" class="form-label">Email address</label>
              <input type="email" class="form-control" id="username" v-model="username" required>
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input type="password" class="form-control" id="password" v-model="password" required>
            </div>
            <div class="d-grid">
              <button type="submit" class="btn btn-primary">Login</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'LoginView',
    data() {
      return {
        username: '',
        password: '',
        error: null
      }
    },
    methods: {
      async handleLogin() {
        this.error = null; // Reset error message
        try {
          const credentials = {
            username: this.username,
            password: this.password
          };
          // This 'dispatches' the login action in our Vuex store.
          await this.$store.dispatch('login', credentials);
  
          // On success, redirect the user to the dashboard.
          this.$router.push('/dashboard');
        } catch (err) {
          this.error = 'Login failed. Please check your credentials.';
          console.error('Login component error:', err);
        }
      }
    }
  }
  </script>
  
  <style scoped>
  /* The 'scoped' attribute means these styles will only apply
     to this component, preventing conflicts with other components. */
  .login-container {
    max-width: 400px;
    margin: auto;
    margin-top: 5rem;
  }
  </style>