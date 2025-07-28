<template>
    <div class="container my-5">
      <div v-if="result" class="text-center">
        <h1 class="display-4">Quiz Completed!</h1>
        <p class="lead">Here's how you did.</p>
  
        <div class="row my-5">
          <div class="col-md-4">
            <div class="card h-100 shadow-sm">
              <div class="card-body">
                <h5 class="card-title">Your Score</h5>
                <p class="display-1 fw-bold text-primary">{{ result.score_achieved }}/{{ result.total_questions }}</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card h-100 shadow-sm">
              <div class="card-body">
                <h5 class="card-title">Performance</h5>
                <div style="position: relative; height: 250px">
                    <Doughnut :data="chartData" :options="chartOptions" />
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
             <div class="card h-100 shadow-sm">
              <div class="card-body">
                <h5 class="card-title">Proctoring</h5>
                <p class="display-3">{{ result.tab_switches }}</p>
                <p class="text-muted">Tab Switches Detected</p>
              </div>
            </div>
          </div>
        </div>
  
        <div class="text-start">
          <h3 class="mb-4">Answer Breakdown</h3>
          <div v-for="(item, index) in result.breakdown" :key="item.question_id" class="card mb-3">
            <div class="card-body">
              <p><strong>Q{{ index + 1 }}: {{ item.question_statement }}</strong></p>
              <ul class="list-group">
                <li v-for="i in 4" :key="i" class="list-group-item" :class="getOptionClass(item, i)">
                  {{ item['option' + i] }}
                  <span v-if="item.correct_answer === i" class="badge bg-success float-end">Correct Answer</span>
                  <span v-if="!item.is_correct && item.user_answer === i" class="badge bg-danger float-end">Your Answer</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
  
        <router-link to="/user-dashboard" class="btn btn-primary mt-4">Back to Dashboard</router-link>
      </div>
    </div>
  </template>
  
  <script>
  import { Doughnut } from 'vue-chartjs'
  import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
  import api from '../services/api';
  
  ChartJS.register(ArcElement, Tooltip, Legend)
  
  export default {
    name: 'ResultsView',
    components: { Doughnut },
    data() {
      return {
        questionsMap: {} // To store question details for answer text lookup
      }
    },
    computed: {
      result() {
        return this.$store.state.latestResult;
      },
      chartData() {
        if (!this.result) return {};
        return {
          labels: ['Correct', 'Incorrect'],
          datasets: [
            {
              backgroundColor: ['#198754', '#dc3545'],
              data: [
                this.result.score_achieved, 
                this.result.total_questions - this.result.score_achieved
              ]
            }
          ]
        }
      },
      chartOptions() {
        return {
          responsive: true,
          maintainAspectRatio: false
        }
      }
    },
    methods: {
      getOptionClass(item, optionIndex) {
      const isCorrect = item.correct_answer === optionIndex;
      const isUserAnswer = item.user_answer === optionIndex;

      if (isCorrect) {
        return 'list-group-item-success';
      }
      if (isUserAnswer && !isCorrect) {
        return 'list-group-item-danger'; 
      }
      return ''; // Default style for other options
    },
      getOptionText(breakdownItem, optionNumber) {
      if (!optionNumber) return 'Not Answered';
      // Now we can access the option text directly from the breakdown item
      return breakdownItem['option' + optionNumber];
    },
    async fetchPastResult(scoreId) {
      try {
        const response = await api.get(`/result/${scoreId}`);
        this.$store.commit('SET_LATEST_RESULT', response.data);
      } catch (error) {
        console.error("Failed to fetch past result:", error);
        this.$router.push('/user-dashboard');
      }
    },
      async fetchQuestionDetailsForBreakdown() {
        // We need the full question details to display the option text
        const questionIds = this.result.breakdown.map(b => b.question_id);
        // This assumes a new backend endpoint. Let's create it.
        // For now, let's just use the answer number. We will enhance this.
      },
      async fetchPastResult(scoreId) {
      try {
        const response = await api.get(`/result/${scoreId}`);
        this.$store.commit('SET_LATEST_RESULT', response.data);
      } catch (error) {
        console.error("Failed to fetch past result:", error);
        this.$router.push('/user-dashboard');
      }
    }
  },
    async created() {
    const scoreId = this.$route.params.scoreId;
    if (scoreId) {
      // If a scoreId is in the URL, fetch that specific result
      await this.fetchPastResult(scoreId);
    } else if (!this.$store.state.latestResult) {
      // If there's no ID and no result in the store, redirect away
      this.$router.push('/user-dashboard');
    }
  }
  }
  </script>