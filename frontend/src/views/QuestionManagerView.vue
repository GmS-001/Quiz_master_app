<template>
    <div>
      <div class="mb-4">
        <a href="#" @click.prevent="$router.go(-1)">&larr; Back to Chapter</a>
        <h1 v-if="quiz" class="mt-2">Manage Questions for: <span class="text-primary">{{ quiz.remarks }}</span></h1>
      </div>
  
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Add New Question</h5>
          <form @submit.prevent="addQuestion" class="p-3 bg-light rounded">
            <div class="mb-3">
              <label class="form-label">Question Statement</label>
              <textarea class="form-control" v-model="newQuestion.question_statement" required></textarea>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3"><label class="form-label">Option 1</label><input type="text" class="form-control" v-model="newQuestion.option1" required></div>
              <div class="col-md-6 mb-3"><label class="form-label">Option 2</label><input type="text" class="form-control" v-model="newQuestion.option2" required></div>
              <div class="col-md-6 mb-3"><label class="form-label">Option 3</label><input type="text" class="form-control" v-model="newQuestion.option3" required></div>
              <div class="col-md-6 mb-3"><label class="form-label">Option 4</label><input type="text" class="form-control" v-model="newQuestion.option4" required></div>
            </div>
            <div class="mb-3">
              <label class="form-label">Correct Option</label>
              <select class="form-select" v-model.number="newQuestion.correct_option" required>
                <option :value="1">Option 1</option>
                <option :value="2">Option 2</option>
                <option :value="3">Option 3</option>
                <option :value="4">Option 4</option>
              </select>
            </div>
            <button type="submit" class="btn btn-primary">Add Question</button>
          </form>
        </div>
      </div>
  
      <div class="mt-4">
        <h5>Existing Questions</h5>
        <div v-for="(question, index) in questions" :key="question.id" class="card mb-3">
          <div class="card-body">
            <p><strong>Q{{ index + 1 }}: {{ question.question_statement }}</strong></p>
            <ul class="list-group list-group-flush">
              <li class="list-group-item" :class="{'list-group-item-success': question.correct_option === 1}">1. {{ question.option1 }}</li>
              <li class="list-group-item" :class="{'list-group-item-success': question.correct_option === 2}">2. {{ question.option2 }}</li>
              <li class="list-group-item" :class="{'list-group-item-success': question.correct_option === 3}">3. {{ question.option3 }}</li>
              <li class="list-group-item" :class="{'list-group-item-success': question.correct_option === 4}">4. {{ question.option4 }}</li>
            </ul>
            <div class="mt-3">
              <button @click="deleteQuestion(question.id)" class="btn btn-sm btn-outline-danger">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import api from '../services/api';
  
  export default {
    name: 'QuestionManagerView',
    data() {
      return {
        quiz: null,
        questions: [],
        newQuestion: {
          question_statement: '',
          option1: '',
          option2: '',
          option3: '',
          option4: '',
          correct_option: null
        },
        quizId: this.$route.params.quizId,
      }
    },
    methods: {
      async fetchQuizDetails() {
        const response = await api.get(`/quizzes/${this.quizId}`);
        this.quiz = response.data;
      },
      async fetchQuestions() {
        const response = await api.get(`/quizzes/${this.quizId}/questions`);
        this.questions = response.data;
      },
      async addQuestion() {
        await api.post(`/quizzes/${this.quizId}/questions`, this.newQuestion);
        this.newQuestion = { question_statement: '', option1: '', option2: '', option3: '', option4: '', correct_option: null };
        await this.fetchQuestions();
      },
      async deleteQuestion(questionId) {
        if (confirm('Are you sure?')) {
          await api.delete(`/questions/${questionId}`);
          await this.fetchQuestions();
        }
      },
    },
    created() {
      this.fetchQuizDetails();
      this.fetchQuestions();
    }
  }
  </script>