import axios from 'axios';
import store from '../store'; // We need to access the store to get the token

const apiClient = axios.create({
  baseURL: '/api',
});

// This is an Axios interceptor. It's a function that runs
// before each request is sent.
apiClient.interceptors.request.use(config => {
  const token = store.state.token;
  if (token) {
    // If a token exists, add it to the Authorization header
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default apiClient;