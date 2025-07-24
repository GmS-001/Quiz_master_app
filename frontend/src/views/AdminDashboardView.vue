<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Admin Dashboard</h1>
      <button @click="handleLogout" class="btn btn-danger">Logout</button>
    </div>
    
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">Manage Subjects</h5>
        
        <form @submit.prevent="addSubject" class="row g-3 mb-4">
          <div class="col-md-5">
            <input type="text" class="form-control" placeholder="New Subject Name" v-model="newSubject.name" required>
          </div>
          <div class="col-md-5">
            <input type="text" class="form-control" placeholder="Description" v-model="newSubject.description">
          </div>
          <div class="col-md-2 d-grid">
            <button type="submit" class="btn btn-primary">Add Subject</button>
          </div>
        </form>

        <ul class="list-group">
          <li v-for="subject in subjects" :key="subject.id" class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <router-link :to="`/subjects/${subject.id}/chapters`" class="text-decoration-none text-dark">
                <strong>{{ subject.name }}</strong>
                <div class="text-muted small">{{ subject.description }}</div>
              </router-link>
            </div>
            <div>
              <button @click="openEditModal(subject)" class="btn btn-sm btn-outline-secondary me-2">Edit</button>
              <button @click="deleteSubject(subject.id)" class="btn btn-sm btn-outline-danger">Delete</button>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <div class="modal fade" id="editSubjectModal" tabindex="-1" aria-labelledby="editSubjectModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editSubjectModalLabel">Edit Subject</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateSubject">
              <div class="mb-3">
                <label for="editSubjectName" class="form-label">Subject Name</label>
                <input type="text" class="form-control" id="editSubjectName" v-model="editingSubject.name" required>
              </div>
              <div class="mb-3">
                <label for="editSubjectDesc" class="form-label">Description</label>
                <input type="text" class="form-control" id="editSubjectDesc" v-model="editingSubject.description">
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
import { Modal } from 'bootstrap'; // Import Bootstrap's Modal component

export default {
  name: 'AdminDashboardView',
  data() {
    return {
      subjects: [],
      newSubject: { name: '', description: '' },
      editingSubject: { id: null, name: '', description: '' },
      editModalInstance: null
    }
  },
  methods: {
    handleLogout() {
      this.$store.dispatch('logout');
      this.$router.push('/login');
    },
    async fetchSubjects() {
      try {
        const response = await api.get('/subjects');
        this.subjects = response.data;
      } catch (error) { console.error("Error fetching subjects:", error); }
    },
    async addSubject() {
      try {
        await api.post('/subjects', this.newSubject);
        this.newSubject = { name: '', description: '' };
        await this.fetchSubjects();
      } catch (error) { console.error("Error adding subject:", error); }
    },
    async deleteSubject(id) {
      if (confirm('Are you sure you want to delete this subject?')) {
        try {
          await api.delete(`/subjects/${id}`);
          await this.fetchSubjects();
        } catch (error) { console.error("Error deleting subject:", error); }
      }
    },
    openEditModal(subject) {
      // Create a copy of the subject object to avoid modifying the original list directly
      this.editingSubject = { ...subject };
      this.editModalInstance.show();
    },
    async updateSubject() {
      try {
        await api.put(`/subjects/${this.editingSubject.id}`, this.editingSubject);
        await this.fetchSubjects();
        this.editModalInstance.hide();
      } catch (error) { console.error("Error updating subject:", error); }
    }
  },
  mounted() {
    // We need to initialize the Bootstrap modal instance when the component is mounted
    const modalElement = document.getElementById('editSubjectModal');
    this.editModalInstance = new Modal(modalElement);
  },
  created() {
    this.fetchSubjects();
  }
}
</script>