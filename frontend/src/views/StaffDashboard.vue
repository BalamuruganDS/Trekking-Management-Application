<template>
  <div class="container py-4">

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>Trek Staff Operations</h2>
        <p class="text-muted mb-0">
          Manage assigned expeditions, available slots, and traveler manifests
        </p>
      </div>

      <div class="d-flex gap-2">
        <button
          class="btn btn-outline-secondary btn-sm"
          @click="fetchAssignedTreks"
        >
          🔄 Refresh
        </button>

        <button
          class="btn btn-outline-primary"
          @click="openProfile"
        >
          👤 Update Profile
        </button>
      </div>
    </div>


    <!-- Messages -->
    <div v-if="message" class="alert alert-success">
      {{ message }}
      <button class="btn-close float-end" @click="message = ''"></button>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
      <button class="btn-close float-end" @click="error = ''"></button>
    </div>


    <!-- ================= PROFILE MODAL ================= -->

    <div
      v-if="showProfile"
      class="modal fade show d-block"
      style="background:rgba(0,0,0,.5)"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">👤 Update Staff Profile</h5>
            <button class="btn-close" @click="closeProfile"></button>
          </div>

          <div class="modal-body">

            <div v-if="profileLoading" class="text-center py-4">
              Loading profile...
            </div>

            <form v-else @submit.prevent="updateProfile">

              <div class="row">

                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">Full Name</label>
                  <input
                    v-model="profile.full_name"
                    class="form-control"
                    required
                  >
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">Email</label>
                  <input
                    v-model="profile.email"
                    type="email"
                    class="form-control"
                    required
                  >
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">Contact Number</label>
                  <input
                    v-model="profile.contact_number"
                    class="form-control"
                  >
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">Age</label>
                  <input
                    v-model.number="profile.age"
                    type="number"
                    min="1"
                    max="120"
                    class="form-control"
                  >
                </div>

                <div class="col-12 mb-3">
                  <label class="form-label fw-bold">Address</label>
                  <textarea
                    v-model="profile.address"
                    class="form-control"
                    rows="2"
                  ></textarea>
                </div>

                <div class="col-12 mb-3">
                  <label class="form-label fw-bold">
                    Specialization
                  </label>
                  <input
                    v-model="profile.specialization"
                    class="form-control"
                    placeholder="First Aid, Navigation, High Altitude..."
                  >
                </div>

                <div class="col-12 mb-3">
                  <label class="form-label fw-bold d-block">
                    Disability
                  </label>

                  <label class="me-3">
                    <input
                      v-model="profile.has_disability"
                      type="radio"
                      :value="false"
                    >
                    No
                  </label>

                  <label>
                    <input
                      v-model="profile.has_disability"
                      type="radio"
                      :value="true"
                    >
                    Yes
                  </label>
                </div>

                <div
                  v-if="profile.has_disability"
                  class="col-12 mb-3"
                >
                  <label class="form-label fw-bold">
                    Disability Description
                  </label>

                  <textarea
                    v-model="profile.disability_description"
                    class="form-control"
                    rows="3"
                    required
                  ></textarea>
                </div>

              </div>

              <div class="text-end">
                <button
                  type="button"
                  class="btn btn-secondary me-2"
                  @click="closeProfile"
                >
                  Cancel
                </button>

                <button
                  class="btn btn-primary"
                  :disabled="profileSaving"
                >
                  {{ profileSaving ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>

            </form>

          </div>
        </div>
      </div>
    </div>


    <!-- ================= ASSIGNED TREKS ================= -->

    <div class="row">

      <div
        v-for="trek in assignedTreks"
        :key="trek.id"
        class="col-md-6 mb-4"
      >

        <div class="card shadow-sm border-0 h-100">

          <div
            class="card-header bg-dark text-white
                   d-flex justify-content-between align-items-center"
          >
            <strong>{{ trek.title }}</strong>

            <span class="badge bg-success">
              {{ trek.status || 'Open' }}
            </span>
          </div>


          <div class="card-body">

            <p>
              <strong>Location:</strong>
              {{ trek.location }}
            </p>

            <p>
              <strong>Difficulty:</strong>
              {{ trek.difficulty }}
            </p>

            <p>
              <strong>Dates:</strong>
              {{ trek.start_date || 'N/A' }}
              to
              {{ trek.end_date || 'N/A' }}
            </p>

            <!-- NEW: Description -->
            <div class="mb-3">
              <strong>Description:</strong>

              <p class="text-muted mt-1 mb-0">
                {{ trek.description || 'No description provided.' }}
              </p>
            </div>

            <hr>


            <!-- Slots + Status -->
            <div class="row g-2 mb-3">

              <div class="col-6">
                <label class="form-label small fw-bold">
                  Available Slots
                </label>

                <div class="input-group input-group-sm">

                  <input
                    v-model.number="trek.available_seats"
                    type="number"
                    min="0"
                    class="form-control"
                  >

                  <button
                    class="btn btn-outline-primary"
                    @click="updateSlots(trek)"
                  >
                    Save
                  </button>

                </div>
              </div>


              <div class="col-6">
                <label class="form-label small fw-bold">
                  Status
                </label>

                <select
                  v-model="trek.status"
                  class="form-select form-select-sm"
                  @change="updateStatus(trek)"
                >
                  <option value="Open">Open</option>
                  <option value="Closed">Closed</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>

            </div>


            <button
              class="btn btn-sm btn-secondary w-100"
              @click="loadParticipants(trek)"
            >
              📋 View Registered Trekkers
            </button>

          </div>
        </div>

      </div>


      <div
        v-if="assignedTreks.length === 0"
        class="col-12"
      >
        <div class="card text-center py-5 border-0 shadow-sm">
          <p class="text-muted mb-0">
            No assigned treks for upcoming trips at this moment.
          </p>
        </div>
      </div>

    </div>


    <!-- ================= PARTICIPANTS MODAL ================= -->

    <div
      v-if="showModal"
      class="modal fade show d-block"
      style="background:rgba(0,0,0,.5)"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">

          <div class="modal-header bg-secondary text-white">

            <h5 class="modal-title">
              Participants — {{ activeTrekTitle }}
            </h5>

            <button
              class="btn-close btn-close-white"
              @click="showModal = false"
            ></button>

          </div>


          <div class="modal-body p-0">

            <div class="table-responsive">

              <table class="table table-hover align-middle mb-0">

                <thead class="table-light text-center">
                  <tr>
                    <th>Booking ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Seats</th>
                    <th>Action</th>
                  </tr>
                </thead>

                <tbody>

                  <tr
                    v-for="p in participants"
                    :key="p.booking_id"
                    class="text-center"
                  >

                    <td>
                      #{{ p.booking_id }}
                    </td>

                    <td>
                      <button
                        class="btn btn-link p-0
                               fw-bold text-dark
                               text-decoration-none"
                        @click="viewParticipant(p)"
                      >
                        {{ p.full_name }}
                      </button>
                    </td>

                    <td>
                      {{ p.email }}
                    </td>

                    <td>
                      <span class="badge bg-primary">
                        {{ p.seats_booked }}
                      </span>
                    </td>

                    <td>
                      <button
                        class="btn btn-sm btn-outline-primary"
                        @click="viewParticipant(p)"
                      >
                        View
                      </button>
                    </td>

                  </tr>


                  <tr v-if="participants.length === 0">
                    <td
                      colspan="5"
                      class="text-center py-4 text-muted"
                    >
                      No registered trekkers yet.
                    </td>
                  </tr>

                </tbody>

              </table>

            </div>

          </div>


          <div class="modal-footer">

            <button
              class="btn btn-secondary"
              @click="showModal = false"
            >
              Close
            </button>

          </div>

        </div>
      </div>
    </div>


    <!-- ================= TREKKER PROFILE MODAL ================= -->

    <div
      v-if="selectedParticipant"
      class="modal fade show d-block"
      style="background:rgba(0,0,0,.6)"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">

          <div class="modal-header bg-dark text-white">

            <h5 class="modal-title">
              👤 Trekker Profile
            </h5>

            <button
              class="btn-close btn-close-white"
              @click="selectedParticipant = null"
            ></button>

          </div>


          <div class="modal-body">

            <div class="row">

              <div class="col-md-6 mb-3">
                <strong>Name</strong>
                <div>
                  {{ selectedParticipant.full_name || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Email</strong>
                <div>
                  {{ selectedParticipant.email || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Contact</strong>
                <div>
                  {{ selectedParticipant.contact_number || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Age</strong>
                <div>
                  {{ selectedParticipant.age || 'N/A' }}
                </div>
              </div>

              <div class="col-12 mb-3">
                <strong>Address</strong>
                <div>
                  {{ selectedParticipant.address || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Disability</strong>
                <div>
                  {{ selectedParticipant.has_disability ? 'Yes' : 'No' }}
                </div>
              </div>

              <div
                v-if="selectedParticipant.has_disability"
                class="col-12 mb-3"
              >
                <strong>Disability Description</strong>
                <div>
                  {{ selectedParticipant.disability_description || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Booking ID</strong>
                <div>
                  #{{ selectedParticipant.booking_id }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Seats Booked</strong>
                <div>
                  {{ selectedParticipant.seats_booked }}
                </div>
              </div>

            </div>

          </div>


          <div class="modal-footer">

            <button
              class="btn btn-secondary"
              @click="selectedParticipant = null"
            >
              Close
            </button>

          </div>

        </div>
      </div>
    </div>

  </div>
</template>


<script>
import api from '../api';

export default {
  name: 'StaffDashboard',

  data() {
    return {
      
      assignedTreks: [],
      participants: [],
      activeTrekTitle: '',

      message: '',
      error: '',

      showModal: false,
      selectedParticipant: null,

      showProfile: false,
      profileLoading: false,
      profileSaving: false,

      profile: {
        full_name: '',
        email: '',
        contact_number: '',
        address: '',
        age: null,
        has_disability: false,
        disability_description: '',
        specialization: ''
      }
    };
  },


  mounted() {
    this.fetchAssignedTreks();
  },


  methods: {

    /* ---------- Staff Profile ---------- */

    async openProfile() {
      this.message = '';
      this.error = '';
      this.showProfile = true;
      this.profileLoading = true;

      try {
        const res = await api.get('/api/staff/profile');
        const p = res.data.profile;

        this.profile = {
          full_name: p.full_name || '',
          email: p.email || '',
          contact_number: p.contact_number || '',
          address: p.address || '',
          age: p.age || null,
          has_disability: Boolean(p.has_disability),
          disability_description: p.disability_description || '',
          specialization: p.specialization || ''
        };
      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to load profile.';
        this.showProfile = false;
      } finally {
        this.profileLoading = false;
      }
    },


    closeProfile() {
      if (!this.profileSaving) {
        this.showProfile = false;
      }
    },


    async updateProfile() {
      this.message = '';
      this.error = '';

      if (
        this.profile.age &&
        (this.profile.age < 1 || this.profile.age > 120)
      ) {
        this.error = 'Age must be between 1 and 120.';
        return;
      }

      if (
        this.profile.has_disability &&
        !this.profile.disability_description.trim()
      ) {
        this.error = 'Please describe the disability.';
        return;
      }

      this.profileSaving = true;

      try {
        const res = await api.put(
          '/api/staff/profile',
          this.profile
        );

        this.message =
          res.data.message ||
          'Profile updated successfully.';

        this.showProfile = false;

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to update profile.';
      } finally {
        this.profileSaving = false;
      }
    },


    /* ---------- Assigned Treks ---------- */

    async fetchAssignedTreks() {
      this.error = '';

      try {
        const res = await api.get(
          '/api/staff/my-treks'
        );

        this.assignedTreks =
          res.data.treks || [];

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to load assigned treks.';
      }
    },


    async updateSlots(trek) {
      this.message = '';
      this.error = '';

      try {
        const res = await api.patch(
          `/api/staff/treks/${trek.id}/slots`,
          {
            available_seats:
              trek.available_seats
          }
        );

        this.message =
          res.data.message ||
          'Available slots updated successfully.';

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to update slots.';
      }
    },


    async updateStatus(trek) {
      this.message = '';
      this.error = '';

      try {
        const res = await api.patch(
          `/api/staff/treks/${trek.id}/status`,
          {
            status: trek.status
          }
        );

        this.message =
          res.data.message ||
          'Trek status updated successfully.';

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to update trek status.';
      }
    },


    /* ---------- Participants ---------- */

    async loadParticipants(trek) {
      this.activeTrekTitle = trek.title;
      this.participants = [];
      this.selectedParticipant = null;
      this.error = '';

      try {
        const res = await api.get(
          `/api/staff/treks/${trek.id}/participants`
        );

        this.participants =
          res.data.participants || [];

        this.showModal = true;

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to fetch participants.';
      }
    },


    viewParticipant(participant) {
      this.selectedParticipant = participant;
    },
  

    async downloadBookingHistory() {
      try {
          const token = localStorage.getItem('token');

          const response = await fetch(
              'http://127.0.0.1:5000/api/user/export-bookings',
              {
                  method: 'GET',
                  headers: {
                      Authorization: `Bearer ${token}`
                  }
              }
          );

          if (!response.ok) {
              const error = await response.json();

              throw new Error(
                  error.error ||
                  'Failed to export booking history.'
              );
          }

          const blob = await response.blob();

          const url = window.URL.createObjectURL(blob);

          const link = document.createElement('a');

          link.href = url;
          link.download = 'booking_history.csv';

          document.body.appendChild(link);

          link.click();

          link.remove();

          window.URL.revokeObjectURL(url);

          this.message =
              'Booking history downloaded and sent to your email successfully!';

      } catch (error) {

          console.error(
              'Booking history export error:',
              error
          );

          this.message =
              error.message ||
              'Failed to export booking history.';
      }
      }



  }
};
</script> 