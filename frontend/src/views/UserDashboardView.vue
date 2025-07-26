<template>
    <div v-if="profile">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Welcome, {{ profile.fullName }}!</h1>
        <button @click="handleLogout" class="btn btn-danger">Logout</button>
      </div>
      
      <div class="row">
        <div class="col-md-5">
          <div class="card">
            <div class="card-header fw-bold">My Profile</div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item"><strong>Email:</strong> {{ profile.username }}</li>
              <li class="list-group-item"><strong>Qualification:</strong> {{ profile.qualification }}</li>
              <li class="list-group-item"><strong>Date of Birth:</strong> {{ profile.dob }}</li>
            </ul>
          </div>
        </div>
  
        <div class="col-md-7">
          <div class="card">
            <div class="card-header fw-bold">Available Quizzes</div>
            <div class="card-body">
              <div class="accordion" id="quizAccordion">
                <div v-for="subject in contentTree" :key="subject.id" class="accordion-item">
                  <h2 class="accordion-header" :id="'heading' + subject.id">
                    <button class="accordion-button collapsed" type="button" :data-bs-toggle="'collapse'" :data-bs-target="'#collapse' + subject.id">
                      {{ subject.name }}
                    </button>
                  </h2>
                  <div :id="'collapse' + subject.id" class="accordion-collapse collapse" :data-bs-parent="'#quizAccordion'">
                    <div class="accordion-body">
                      <div v-for="chapter in subject.chapters" :key="chapter.id" class="mb-3">
                        <strong>{{ chapter.name }}</strong>
                        <ul class="list-group mt-2">
                            <ul v-if="chapter.quizzes.length > 0" class="list-group mt-2">
                                <li v-for="quiz in chapter.quizzes" :key="quiz.id" class="list-group-item d-flex justify-content-between align-items-center">
                                    {{ quiz.remarks || 'Quiz' }}
                                    <router-link :to="`/attempt/quiz/${quiz.id}`" class="btn btn-success btn-sm">Start Quiz</router-link>
                                </li>
                            </ul>
                            <p v-else class="text-muted fst-italic mt-2">
                            No quizzes available in this chapter yet.
                            </p>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../services/api';
  
  export default {
    name: 'UserDashboardView',
    data() {
      return {
        profile: null,
        contentTree: [] // To store the nested quiz list
      }
    },
    methods: {
      async fetchProfile() {
        try {
          const response = await api.get('/profile');
          this.profile = response.data;
        } catch (error) { console.error("Failed to fetch profile:", error); }
      },
      async fetchContentTree() {
        try {
          const response = await api.get('/content-tree');
          this.contentTree = response.data;
        } catch (error) { console.error("Failed to fetch content tree:", error); }
      },
      handleLogout() {
        this.$store.dispatch('logout');
        this.$router.push('/login');
      }
    },
    created() {
      this.fetchProfile();
      this.fetchContentTree();
    }
  }
  </script>