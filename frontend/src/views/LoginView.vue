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
          <div class="text-center mt-3">
            <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
    import { jwtDecode } from 'jwt-decode'; 

    export default {
      name: 'LoginView',
      data() { /* ... unchanged ... */ },
      methods: {
        async handleLogin() {
          this.error = null;
          try {
            const credentials = { username: this.username, password: this.password };
            await this.$store.dispatch('login', credentials);

            // Decode the token to check the user's role
            const token = this.$store.state.token;
            const decodedToken = jwtDecode(token);

            // Redirect based on the is_admin claim
            if (decodedToken.is_admin) {
              this.$router.push('/dashboard'); // Admin dashboard
            } else {
              this.$router.push('/user-dashboard'); // User dashboard
            }

          } catch (err) { /* ... unchanged ... */ }
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