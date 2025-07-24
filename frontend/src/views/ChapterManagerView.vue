<template>
    <div>
      <div class="mb-4">
        <router-link to="/dashboard">&larr; Back to Dashboard</router-link>
        <h1 class="mt-2">Manage Chapters for: <span class="text-primary">{{ subject.name }}</span></h1>
      </div>
  
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Chapters</h5>
  
          <form @submit.prevent="addChapter" class="row g-3 mb-4">
            <div class="col-md-5"><input type="text" class="form-control" placeholder="New Chapter Name" v-model="newChapter.name" required></div>
            <div class="col-md-5"><input type="text" class="form-control" placeholder="Description" v-model="newChapter.description"></div>
            <div class="col-md-2 d-grid"><button type="submit" class="btn btn-primary">Add Chapter</button></div>
          </form>
  
          <ul class="list-group">
            <li v-for="chapter in chapters" :key="chapter.id" class="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <strong>{{ chapter.name }}</strong>
                <div class="text-muted small">{{ chapter.description }}</div>
              </div>
              <div>
                <button @click="openEditModal(chapter)" class="btn btn-sm btn-outline-secondary me-2">Edit</button>
                <button @click="deleteChapter(chapter.id)" class="btn btn-sm btn-outline-danger">Delete</button>
              </div>
            </li>
          </ul>
        </div>
      </div>
  
      <div class="modal fade" id="editChapterModal">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header"><h5 class="modal-title">Edit Chapter</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
            <div class="modal-body">
              <form @submit.prevent="updateChapter">
                <div class="mb-3">
                  <label class="form-label">Chapter Name</label>
                  <input type="text" class="form-control" v-model="editingChapter.name" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Description</label>
                  <input type="text" class="form-control" v-model="editingChapter.description">
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                  <button type="submit" class="btn btn-primary">Save changes</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
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
        editModalInstance: null,
        subjectId: this.$route.params.subjectId
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
        if (confirm('Are you sure?')) {
          await api.delete(`/chapters/${chapterId}`);
          await this.fetchChapters();
        }
      },
      openEditModal(chapter) {
        this.editingChapter = { ...chapter };
        this.editModalInstance.show();
      },
      async updateChapter() {
        await api.put(`/chapters/${this.editingChapter.id}`, this.editingChapter);
        this.editModalInstance.hide();
        await this.fetchChapters();
      }
    },
    mounted() {
      const modalElement = document.getElementById('editChapterModal');
      this.editModalInstance = new Modal(modalElement);
    },
    created() {
      this.fetchSubjectDetails();
      this.fetchChapters();
    }
  }
  </script>