<template>
  <div v-if="profile">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Welcome, {{ profile.fullName }}!</h1>
      <div>
        <button class="btn btn-info me-2" @click="handleExportCsv" :disabled="isExporting">
          <span v-if="isExporting" class="spinner-border spinner-border-sm"></span>
          {{ isExporting ? 'Generating...' : 'Export My Scores' }}
        </button>
        <button @click="handleLogout" class="btn btn-danger">Logout</button>
      </div>
    </div>

      
    <div class="row g-4">
      <div class="col-lg-5">
        <div class="card mb-4">
          <div class="card-header fw-bold">My Profile</div>
          <ul class="list-group list-group-flush">
            <li class="list-group-item"><strong>Email:</strong> {{ profile.username }}</li>
            <li class="list-group-item"><strong>Qualification:</strong> {{ profile.qualification }}</li>
            <li class="list-group-item"><strong>Date of Birth:</strong> {{ profile.dob }}</li>
          </ul>
        </div>
        
        <div class="card">
            <div class="card-header fw-bold">My Quiz History</div>
            <div class="list-group list-group-flush">
                <div v-if="scoreHistory.length === 0" class="list-group-item text-muted">No past attempts yet.</div>
                <router-link v-for="score in scoreHistory" :key="score.score_id" :to="`/result/${score.score_id}`" class="list-group-item list-group-item-action">                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">{{ score.subject_name }} - {{ score.quiz_remarks }}</h6>
                        <span class="badge bg-primary rounded-pill">{{ score.score_achieved }} / {{ score.total_questions }}</span>
                    </div>
                    <small class="text-muted">{{ score.timestamp }}</small>
                </router-link>
            </div>
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
      contentTree: [],
      isExporting: false,
      scoreHistory: []
    }
  },
  methods: {
    async fetchProfile() {
      try {
        const response = await api.get('/profile');
        this.profile = response.data;
      } catch (error) { 
        console.error("Failed to fetch profile:", error);
      }
    },
    async fetchContentTree() {
      try {
        const response = await api.get('/content-tree');
        this.contentTree = response.data;
      } catch (error) { 
        console.error("Failed to fetch content tree:", error);
      }
    },
    async fetchScoreHistory() {
      try {
        const response = await api.get('/scores/history');
        this.scoreHistory = response.data;
      } catch (error) {
        console.error("Failed to fetch score history:", error);
      }
    },
    handleLogout() {
      this.$store.dispatch('logout');
      this.$router.push('/login');
    },
    async handleExportCsv() {
      this.isExporting = true;
      try {
        const response = await api.post('/export-csv');
        const taskId = response.data.task_id;
        this.pollTaskStatus(taskId);
      } catch (error) {
        console.error("Error starting CSV export:", error);
        alert("Failed to start export.");
        this.isExporting = false;
      }
    },
    pollTaskStatus(taskId) {
      const interval = setInterval(async () => {
        try {
          const response = await api.get(`/task-status/${taskId}`);
          if (response.data.state === 'SUCCESS') {
            clearInterval(interval);
            this.isExporting = false;
            alert('Your report is ready for download!');
            this.triggerCsvDownload(response.data.result);
          } else if (response.data.state === 'FAILURE') {
            clearInterval(interval);
            this.isExporting = false;
            alert('There was an error generating your report.');
          }
        } catch (error) {
          clearInterval(interval);
          this.isExporting = false;
          console.error("Error polling task status:", error);
        }
      }, 3000);
    },
    triggerCsvDownload(csvData) {
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', 'my_scores_report.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  },
  created() {
    this.fetchProfile();
    this.fetchContentTree();
    this.fetchScoreHistory();
  }
}
</script>