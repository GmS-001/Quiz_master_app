// frontend/src/store/index.js
import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    token: localStorage.getItem('token') || null,
    latestResult: null,
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token;
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    },
    SET_LATEST_RESULT(state, result) {
      state.latestResult = result;
    }
  },
  actions: {
    async login({ commit }, credentials) {
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/login', credentials);
        const token = response.data.access_token;
        
        commit('SET_TOKEN', token);
      } catch (error) {
        console.error("Error in store login action:", error.response.data);
        throw error;
      }
    },
    logout({ commit }) {
      commit('SET_TOKEN', null);
    }
  },
  getters: {
    isAuthenticated: state => !!state.token
  },
  modules: {
  }
})