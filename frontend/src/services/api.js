import axios from 'axios';
import store from '../store'; // We need to access the store to get the token

const apiClient = axios.create({
  baseURL: 'https://quiz-master-backend-iv0n.onrender.com/api',
});

apiClient.interceptors.request.use(config => {
  const token = store.state.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default apiClient;