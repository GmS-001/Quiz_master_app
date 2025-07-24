// frontend/src/store/index.js
import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    // Get token from browser's local storage if it exists
    token: localStorage.getItem('token') || null,
  },
  mutations: {
    // A mutation is the only way to change the state.
    SET_TOKEN(state, token) {
      state.token = token;
      // Store the token in local storage for persistence
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    },
  },
  actions: {
    // Actions are used to commit mutations, especially for async operations.
    async login({ commit }, credentials) {
      try {
        // We call our backend API here.
        const response = await axios.post('http://127.0.0.1:5000/api/login', credentials);
        const token = response.data.access_token;
        
        // If successful, we commit the SET_TOKEN mutation.
        commit('SET_TOKEN', token);
      } catch (error) {
        // If login fails, we throw the error to be caught in the component.
        console.error("Error in store login action:", error.response.data);
        throw error;
      }
    },
    logout({ commit }) {
      // The logout action just needs to clear the token.
      // Our SET_TOKEN mutation already handles removing it from localStorage.
      commit('SET_TOKEN', null);
    }
  },
  getters: {
    // Getters are like computed properties for the store.
    isAuthenticated: state => !!state.token
  },
  modules: {
  }
})