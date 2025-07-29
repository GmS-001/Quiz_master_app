<template>
  <div class="quiz-background" @copy.prevent @paste.prevent @cut.prevent>
    <div class="container py-4">
      <div v-if="isLoading" class="text-center text-white">
        <h2>Loading Quiz...</h2>
      </div>
      <div v-else-if="quiz && currentQuestion">

        <div class="row">
          <div class="col-md-9">
            <div class="quiz-header text-white mb-4 d-flex justify-content-between align-items-center">
              <h4>{{ quiz.remarks }}</h4>
              <div class="d-flex align-items-center">
                <span class="badge bg-warning me-3" v-if="tabSwitches > 0">Tab Switches: {{ tabSwitches }}</span>
                <i class="bi bi-info-circle-fill fs-4 me-3" style="cursor: pointer;" @click="showRulesModal"></i>
                <div class="timer px-3 py-2 rounded" :class="{ 'timer-warning': timeRemaining < 300 }">
                  <i class="bi bi-clock"></i> {{ formattedTime }}
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header d-flex justify-content-between">
                <span>Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}</span>
                <button class="btn btn-sm"
                  :class="questionStates[currentQuestion.id] === 'review' ? 'btn-warning' : 'btn-outline-warning'"
                  @click="toggleReview">
                  <i class="bi bi-flag-fill me-1"></i> {{ questionStates[currentQuestion.id] === 'review' ? 'Unmark' :
                  'Mark for Review' }}
                </button>
              </div>
              <div class="card-body">
                <h5 class="card-title mb-4">{{ currentQuestion.question_statement }}</h5>
                <div class="list-group">
                  <label v-for="i in 4" :key="i" class="list-group-item list-group-item-action">
                    <input class="form-check-input me-2" type="radio" :name="'q' + currentQuestion.id" :value="i"
                      v-model="userAnswers[currentQuestion.id]" @change="markAsAnswered">
                    {{ currentQuestion['option' + i] }}
                  </label>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-between mt-4">
              <button @click="prevQuestion" class="btn btn-light"
                :disabled="currentQuestionIndex === 0">Previous</button>
              <button @click="nextQuestion" class="btn btn-light"
                :disabled="currentQuestionIndex === questions.length - 1">Next</button>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card">
              <div class="card-header text-white bg-dark">
                <video ref="cameraFeed" autoplay playsinline class="w-100"></video>
              </div>
              <div class="card-body question-palette">
                <button v-for="(question, index) in questions" :key="question.id" @click="jumpToQuestion(index)"
                  class="btn m-1" :class="getPaletteClass(question.id)">
                  {{ index + 1 }}
                </button>
              </div>
              <div class="card-footer d-grid">
                <button @click="submitQuiz" class="btn btn-primary">Submit Quiz</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isRulesModalVisible" class="modal-overlay" @click="hideRulesModal">
      <div class="modal-content-custom" @click.stop>
        <div class="modal-header-custom">
          <h5 class="modal-title">Quiz Rules</h5>
          <button type="button" class="btn-close" @click="hideRulesModal"></button>
        </div>
        <div class="modal-body-custom">
          <p>1. Do not switch tabs or minimize the browser.</p>
          <p>2. Keep your camera on throughout the quiz.</p>
          <p>3. Do not copy or paste content.</p>
          <p>4. Submit the quiz before the timer runs out.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'QuizAttemptView',
  data() {
    return {
      isLoading: true,
      quiz: null,
      questions: [],
      currentQuestionIndex: 0,
      userAnswers: {},
      quizId: this.$route.params.quizId,
      timeRemaining: 0,
      timerInterval: null,
      questionStates: {},
      tabSwitches: 0,
      cameraStream: null,
      rulesModalInstance: null,
      isRulesModalVisible: false
    }
  },
  computed: {
    currentQuestion() {
      if (this.questions.length === 0) return null;
      return this.questions[this.currentQuestionIndex];
    },
    formattedTime() {
      const minutes = Math.floor(this.timeRemaining / 60);
      const seconds = this.timeRemaining % 60;
      return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
  },
  methods: {
    async fetchQuizData() {
      try {
        const quizResponse = await api.get(`/quizzes/${this.quizId}`);
        this.quiz = quizResponse.data;
        const questionsResponse = await api.get(`/quizzes/${this.quizId}/questions`);
        this.questions = questionsResponse.data;
      } catch (error) {
        console.error("Failed to load quiz data:", error);
        alert("Could not load the quiz. Please try again later.");
      } finally {
        this.isLoading = false;
      }
    },
    startTimer() {
    const [hours, minutes] = this.quiz.time_duration.split(':').map(Number);
    const totalDuration = hours * 3600 + minutes * 60;
    // If timeRemaining wasn't loaded from a refresh, start from the beginning.
    // Otherwise, use the time that was loaded in the created() hook.
    if (this.timeRemaining === 0) {
      this.timeRemaining = totalDuration;
    }
    this.timerInterval = setInterval(() => {
      if (this.timeRemaining > 0) {
        this.timeRemaining--;
        sessionStorage.setItem(`quiz_${this.quizId}_time`, this.timeRemaining);
      } else {
        clearInterval(this.timerInterval);
        sessionStorage.removeItem(`quiz_${this.quizId}_time`);
        sessionStorage.removeItem(`quiz_${this.quizId}_answers`);
        alert("Time's up!");
        this.submitQuiz(true);
      }
    }, 1000);
  },
    async startCamera() {
      try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          alert("Your browser does not support camera access.");
          return;
        }
        this.cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
        this.$refs.cameraFeed.srcObject = this.cameraStream;
      } catch (error) {
        console.error("Camera access denied:", error);
        alert("Camera access is required for this quiz. Please allow access and refresh the page.");
      }
    },
    handleVisibilityChange() {
      if (document.hidden) {
        this.tabSwitches++;
      }
    },
    async submitQuiz(isAutoSubmit = false) {
      const confirmSubmit = isAutoSubmit || confirm('Are you sure you want to submit the quiz?');
      const payload = {
        answers: this.userAnswers,
        tabSwitches: this.tabSwitches,
        timeTaken: (this.quiz.time_duration.split(':').map(Number)[1] * 60) - this.timeRemaining // Calculate elapsed seconds
      };
      if (confirmSubmit) {
        try {
          sessionStorage.removeItem(`quiz_${this.quizId}_answers`);
          const payload = { answers: this.userAnswers, tabSwitches: this.tabSwitches };
          const response = await api.post(`/quizzes/${this.quizId}/submit`, payload);
          
          this.$store.commit('SET_LATEST_RESULT', response.data);
          sessionStorage.removeItem(`quiz_${this.quizId}_time`); // Clean up on submit
          this.$router.push('/result');

        } catch (error) {
          console.error("Error submitting quiz:", error);
          alert("There was an error submitting your quiz.");
        }
      }
    },
    updateQuestionState(index) {
      const qId = this.questions[index].id;
      if (!this.questionStates[qId] || this.questionStates[qId] === 'not-visited') {
        this.questionStates[qId] = 'not-answered';
      }
    },
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
        this.updateQuestionState(this.currentQuestionIndex);
      }
    },
    prevQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
        this.updateQuestionState(this.currentQuestionIndex);
      }
    },
    jumpToQuestion(index) {
      this.currentQuestionIndex = index;
      this.updateQuestionState(index);
    },
    markAsAnswered() {
      const qId = this.currentQuestion.id;
      this.questionStates[qId] = 'answered';
      sessionStorage.setItem(`quiz_${this.quizId}_answers`, JSON.stringify(this.userAnswers));
    },
    toggleReview() {
      const qId = this.currentQuestion.id;
      if (this.questionStates[qId] === 'review') {
        this.questionStates[qId] = this.userAnswers[qId] ? 'answered' : 'not-answered';
      } else {
        this.questionStates[qId] = 'review';
      }
    },
    getPaletteClass(questionId) {
      const state = this.questionStates[questionId];
      switch (state) {
        case 'answered': return 'btn-success';
        case 'review': return 'btn-warning';
        case 'not-answered': return 'btn-danger';
        default: return 'btn-outline-secondary';
      }
    },
    closeRulesModal() {
      if (this.rulesModalInstance) {
        this.rulesModalInstance.hide();
      }
    },
    showRulesModal() {
      this.isRulesModalVisible = true;
    },
    hideRulesModal() {
      this.isRulesModalVisible = false;
    }
  },
  async created() {
    await this.fetchQuizData();
    
    if (this.quiz && this.questions.length > 0) {
      // Load saved answers from sessionStorage
      const savedAnswers = sessionStorage.getItem(`quiz_${this.quizId}_answers`);
      if (savedAnswers) {
        this.userAnswers = JSON.parse(savedAnswers);
        
        // THIS IS THE NEW, CRITICAL PART:
        // Rebuild the questionStates based on the loaded answers.
        for (const questionId in this.userAnswers) {
          if (this.userAnswers[questionId] !== null) {
            this.questionStates[questionId] = 'answered';
          }
        }
      }

      // Load saved time from sessionStorage
      const savedTime = sessionStorage.getItem(`quiz_${this.quizId}_time`);
      if (savedTime) {
        this.timeRemaining = parseInt(savedTime, 10);
      }
      
      this.startTimer();
      this.updateQuestionState(0);
    }
  },
  mounted() {
    this.startCamera();
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
  },
  unmounted() {
    clearInterval(this.timerInterval);
    if (this.cameraStream) {
      this.cameraStream.getTracks().forEach(track => track.stop());
    }
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
  },
}
</script>



<style scoped>
/* Main background and existing styles */
.quiz-background { background: linear-gradient(45deg, #4c68d7, #6a349d); min-height: 100vh; width: 100vw; position: fixed; top: 0; left: 0; overflow-y: auto; user-select: none; }
.timer { background-color: rgba(0, 0, 0, 0.2); font-size: 1.2rem; font-weight: bold; }
.timer-warning { background-color: #dc3545; }
.question-palette { display: flex; flex-wrap: wrap; gap: 5px; }
.list-group-item { cursor: pointer; }

/* Styles for our new custom modal */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 1050; }
.modal-content-custom { background-color: white; padding: 20px; border-radius: 0.5rem; width: 500px; max-width: 90%; }
.modal-header-custom { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; margin-bottom: 15px; }
</style>