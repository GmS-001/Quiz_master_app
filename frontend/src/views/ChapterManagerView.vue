<template>
    <div>
      <div class="mb-4">
        <router-link to="/dashboard">&larr; Back to Dashboard</router-link>
        <h1 v-if="subject" class="mt-2">Manage Chapters for: <span class="text-primary">{{ subject.name }}</span></h1>      </div>
  
      <div class="row">
        <div class="col-md-5">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Chapters</h5>
              <form @submit.prevent="addChapter" class="mb-4">
                <div class="input-group"><input type="text" class="form-control" placeholder="New Chapter Name" v-model="newChapter.name" required><button type="submit" class="btn btn-primary">Add</button></div>
              </form>
              <div class="list-group">
                <div v-for="chapter in chapters" :key="chapter.id" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" :class="{ 'active': selectedChapter && selectedChapter.id === chapter.id }">
                  <a href="#" @click.prevent="selectChapter(chapter)" class="text-decoration-none" :class="selectedChapter && selectedChapter.id === chapter.id ? 'text-white' : 'text-dark'">{{ chapter.name }}</a>
                  <div>
                    <button @click="openChapterEditModal(chapter)" class="btn btn-sm btn-light me-2">Edit</button>
                    <button @click="deleteChapter(chapter.id)" class="btn btn-sm btn-warning">Delete</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <div class="col-md-7">
          <div v-if="selectedChapter" class="card">
            <div class="card-body">
              <h5 class="card-title">Quizzes for {{ selectedChapter.name }}</h5>
              <form @submit.prevent="addQuiz" class="row g-3 mb-4">
                <div class="col-md-5"><input type="text" class="form-control" placeholder="Duration (HH:MM)" v-model="newQuiz.time_duration" required></div>
                <div class="col-md-5"><input type="text" class="form-control" placeholder="Remarks" v-model="newQuiz.remarks"></div>
                <div class="col-md-2 d-grid"><button type="submit" class="btn btn-success">Add Quiz</button></div>
              </form>
              <ul class="list-group">
                <li v-for="quiz in quizzes" :key="quiz.id" class="list-group-item d-flex justify-content-between align-items-center">
                    <router-link :to="`/quizzes/${quiz.id}/questions`" class="text-decoration-none text-dark">
                        <span>{{ quiz.remarks || 'Quiz' }} ({{ quiz.time_duration }})</span>
                    </router-link>
                  <div>
                    <button @click="openQuizEditModal(quiz)" class="btn btn-sm btn-outline-secondary me-2">Edit</button>
                    <button @click="deleteQuiz(quiz.id)" class="btn btn-sm btn-outline-danger">Delete</button>
                  </div>
                </li>
              </ul>
            </div>
          </div>
          <div v-else class="text-center text-muted mt-5"><p>Select a chapter to see its quizzes.</p></div>
        </div>
      </div>
  
      <div class="modal fade" id="editChapterModal"><div class="modal-dialog"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Edit Chapter</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <form @submit.prevent="updateChapter">
            <div class="mb-3"><label class="form-label">Chapter Name</label><input type="text" class="form-control" v-model="editingChapter.name" required></div>
            <div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button><button type="submit" class="btn btn-primary">Save changes</button></div>
          </form>
        </div>
      </div></div></div>
  
      <div class="modal fade" id="editQuizModal"><div class="modal-dialog"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Edit Quiz</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
          <form @submit.prevent="updateQuiz">
            <div class="mb-3"><label class="form-label">Duration (HH:MM)</label><input type="text" class="form-control" v-model="editingQuiz.time_duration" required></div>
            <div class="mb-3"><label class="form-label">Remarks</label><input type="text" class="form-control" v-model="editingQuiz.remarks"></div>
            <div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button><button type="submit" class="btn btn-primary">Save changes</button></div>
          </form>
        </div>
      </div></div></div>
    </div>
  </template>
  
<script>
  import api from '../services/api';
  import { Modal } from 'bootstrap';

  export default {
    name: 'ChapterManagerView',
    data() {
      return {
        subject: {},
        chapters: [],
        newChapter: { name: '', description: '' },
        editingChapter: { id: null, name: '', description: '' },
        subjectId: this.$route.params.subjectId,
        selectedChapter: null,
        quizzes: [],
        newQuiz: { time_duration: '', remarks: '' },
        editingQuiz: { id: null, time_duration: '', remarks: '' },
        chapterEditModal: null,
        quizEditModal: null,
      }
    },
    methods: {
      async fetchSubjectDetails() {
        const response = await api.get(`/subjects/${this.subjectId}`);
        this.subject = response.data;
      },
      async fetchChapters() {
        const response = await api.get(`/subjects/${this.subjectId}/chapters`);
        this.chapters = response.data;
      },
      async addChapter() {
        await api.post(`/subjects/${this.subjectId}/chapters`, this.newChapter);
        this.newChapter = { name: '', description: '' };
        await this.fetchChapters();
      },
      async deleteChapter(chapterId) {
        if (confirm('Are you sure? This will delete the chapter and all its quizzes.')) {
          await api.delete(`/chapters/${chapterId}`);
          await this.fetchChapters();
          this.selectedChapter = null;
        }
      },
      openChapterEditModal(chapter) {
        this.editingChapter = { ...chapter };
        this.chapterEditModal.show();
      },
      async updateChapter() {
        await api.put(`/chapters/${this.editingChapter.id}`, this.editingChapter);
        this.chapterEditModal.hide();
        await this.fetchChapters();
      },
      // --- Quiz Methods ---
      async selectChapter(chapter) {
        this.selectedChapter = chapter;
        await this.fetchQuizzes();
      },
      async fetchQuizzes() {
        if (!this.selectedChapter) return;
        const response = await api.get(`/chapters/${this.selectedChapter.id}/quizzes`);
        this.quizzes = response.data;
      },
      async addQuiz() {
        if (!this.selectedChapter) return;
        await api.post(`/chapters/${this.selectedChapter.id}/quizzes`, this.newQuiz);
        this.newQuiz = { time_duration: '', remarks: '' };
        await this.fetchQuizzes();
      },
      async deleteQuiz(quizId) {
        if (confirm('Are you sure?')) {
          await api.delete(`/quizzes/${quizId}`);
          await this.fetchQuizzes();
        }
      },
      openQuizEditModal(quiz) {
        this.editingQuiz = { ...quiz };
        this.quizEditModal.show();
      },
      async updateQuiz() {
        await api.put(`/quizzes/${this.editingQuiz.id}`, this.editingQuiz);
        this.quizEditModal.hide();
        await this.fetchQuizzes();
      }
    },
    mounted() {
      this.chapterEditModal = new Modal(document.getElementById('editChapterModal'));
      this.quizEditModal = new Modal(document.getElementById('editQuizModal'));
    },
    created() {
      this.fetchSubjectDetails();
      this.fetchChapters();
    }
  }
</script>
  