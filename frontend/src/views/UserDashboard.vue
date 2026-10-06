<template>
  <div class="container py-4">

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>Trekker Dashboard</h2>
        <p class="text-muted mb-0">
          Discover upcoming adventures, manage bookings, and download passes
        </p>
      </div>
      <button
      class="btn btn-outline-primary"
      @click="downloadBookingHistory"
      >
      📥 Download Booking History
      </button>

      <button
        type="button"
        class="btn btn-outline-primary"
        @click="openProfile"
      >
        👤 Update Profile
      </button>
      
    </div>

    <!-- Messages -->
    <div
      v-if="message"
      class="alert alert-success alert-dismissible fade show"
      role="alert"
    >
      {{ message }}
      <button
        type="button"
        class="btn-close"
        @click="message = ''"
      ></button>
    </div>

    <div
      v-if="error"
      class="alert alert-danger alert-dismissible fade show"
      role="alert"
    >
      {{ error }}
      <button
        type="button"
        class="btn-close"
        @click="error = ''"
      ></button>
    </div>

    <!-- Profile Modal -->
    <div
      v-if="showProfile"
      class="modal fade show d-block"
      tabindex="-1"
      style="background: rgba(0,0,0,.5);"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">👤 Update Profile</h5>

            <button
              type="button"
              class="btn-close"
              @click="closeProfile"
            ></button>
          </div>

          <div class="modal-body">

            <div
              v-if="profileLoading"
              class="text-center py-4"
            >
              <div class="spinner-border text-primary"></div>
              <p class="mt-2 mb-0">Loading profile...</p>
            </div>

            <form
              v-else
              @submit.prevent="updateProfile"
            >
              <div class="row">

                <!-- Name -->
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">
                    Full Name
                  </label>

                  <input
                    v-model="profile.full_name"
                    type="text"
                    class="form-control"
                    required
                  />
                </div>

                <!-- Email -->
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">
                    Email
                  </label>

                  <input
                    v-model="profile.email"
                    type="email"
                    class="form-control"
                    required
                  />
                </div>

                <!-- Contact -->
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">
                    Contact Number
                  </label>

                  <input
                    v-model="profile.contact_number"
                    type="text"
                    class="form-control"
                  />
                </div>

                <!-- Age -->
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">
                    Age
                  </label>

                  <input
                    v-model.number="profile.age"
                    type="number"
                    min="1"
                    max="120"
                    class="form-control"
                  />
                </div>

                <!-- Address -->
                <div class="col-12 mb-3">
                  <label class="form-label fw-bold">
                    Address
                  </label>

                  <textarea
                    v-model="profile.address"
                    class="form-control"
                    rows="2"
                  ></textarea>
                </div>

                <!-- Disability -->
                <div class="col-12 mb-3">

                  <label class="form-label fw-bold d-block">
                    Do you have a disability?
                  </label>

                  <div class="form-check form-check-inline">
                    <input
                      id="disabilityNo"
                      v-model="profile.has_disability"
                      class="form-check-input"
                      type="radio"
                      :value="false"
                    />

                    <label
                      for="disabilityNo"
                      class="form-check-label"
                    >
                      No
                    </label>
                  </div>

                  <div class="form-check form-check-inline">
                    <input
                      id="disabilityYes"
                      v-model="profile.has_disability"
                      class="form-check-input"
                      type="radio"
                      :value="true"
                    />

                    <label
                      for="disabilityYes"
                      class="form-check-label"
                    >
                      Yes
                    </label>
                  </div>

                </div>

                <!-- Disability Description -->
                <div
                  v-if="profile.has_disability"
                  class="col-12 mb-3"
                >
                  <label class="form-label fw-bold">
                    Disability Description
                    <span class="text-danger">*</span>
                  </label>

                  <textarea
                    v-model="profile.disability_description"
                    class="form-control"
                    rows="3"
                    required
                    placeholder="Please describe the disability"
                  ></textarea>
                </div>

              </div>

              <div class="d-flex justify-content-end gap-2">

                <button
                  type="button"
                  class="btn btn-secondary"
                  @click="closeProfile"
                  :disabled="profileSaving"
                >
                  Cancel
                </button>

                <button
                  type="submit"
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

    <!-- Navigation -->
    <div class="border-bottom mb-4">
      <div class="d-flex gap-2">

        <button
          type="button"
          class="btn fw-bold"
          :class="activeTab === 'available'
            ? 'btn-primary'
            : 'btn-light'"
          @click="switchTab('available')"
        >
          🏔️ Explore Treks
        </button>

        <button
          type="button"
          class="btn fw-bold"
          :class="activeTab === 'history'
            ? 'btn-primary'
            : 'btn-light'"
          @click="switchTab('history')"
        >
          🎫 My Bookings & Tickets
        </button>

      </div>
    </div>

    <!-- ========================= -->
    <!-- AVAILABLE TREKS -->
    <!-- ========================= -->

    <div v-if="activeTab === 'available'">

      <!-- Search / Filters -->
      <div class="row g-2 mb-4">

        <div class="col-md-4">
          <input
            v-model="searchQuery"
            @input="fetchTreks"
            type="text"
            class="form-control"
            placeholder="Search title or location..."
          />
        </div>

        <div class="col-md-3">
          <select
            v-model="difficulty"
            @change="fetchTreks"
            class="form-select"
          >
            <option value="">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Moderate">Moderate</option>
            <option value="Hard">Hard</option>
          </select>
        </div>

        <div class="col-md-3">
          <select
            v-model="duration"
            @change="fetchTreks"
            class="form-select"
          >
            <option value="">All Durations</option>
            <option value="1-3">1–3 days</option>
            <option value="4-7">4–7 days</option>
            <option value="8+">8+ days</option>
          </select>
        </div>

        <div class="col-md-2">
          <button
            type="button"
            class="btn btn-outline-secondary w-100"
            @click="clearFilters"
          >
            Clear
          </button>
        </div>

      </div>

      <!-- No Treks -->
      <div
        v-if="treks.length === 0"
        class="text-muted text-center py-5"
      >
        No upcoming treks currently available.
      </div>

      <!-- Trek Cards -->
      <div class="row">

        <div
          v-for="trek in treks"
          :key="trek.id"
          class="col-md-6 col-lg-4 mb-4"
        >

          <div class="card h-100 shadow-sm border-0">

            <div class="card-body d-flex flex-column">

              <h5 class="card-title text-primary fw-bold">
                {{ trek.title }}
              </h5>

              <h6 class="card-subtitle mb-2 text-muted">
                📍 {{ trek.location }}
              </h6>

              <p class="card-text flex-grow-1 text-secondary small">
                {{ trek.description || 'No description provided.' }}
              </p>

              <div class="mb-3">

                <span class="badge bg-info text-dark me-2">
                  {{ trek.difficulty }}
                </span>

                <span class="badge bg-secondary me-2">
                  ⏱️ {{ trek.duration }} days
                </span>

                <span
                  class="badge"
                  :class="trek.available_seats > 0
                    ? 'bg-success'
                    : 'bg-danger'"
                >
                  {{ trek.available_seats > 0
                    ? trek.available_seats + ' Seats Left'
                    : 'Sold Out'
                  }}
                </span>

              </div>

              <div
                class="d-flex justify-content-between align-items-center"
              >

                <span class="fw-bold fs-5">
                  ₹{{ trek.price }}
                </span>

                <button
                  type="button"
                  class="btn btn-sm"
                  :class="isBooked(trek.id)
                    ? 'btn-success'
                    : 'btn-primary'"
                  @click="bookTrek(trek.id)"
                  :disabled="
                    bookingInProgress === trek.id ||
                    trek.available_seats <= 0 ||
                    isBooked(trek.id)
                  "
                >
                  {{
                    bookingInProgress === trek.id
                      ? 'Booking...'
                      : isBooked(trek.id)
                        ? 'Booked ✓'
                        : trek.available_seats > 0
                          ? 'Book Now'
                          : 'Sold Out'
                  }}
                </button>

              </div>

            </div>

            <div class="card-footer bg-light text-muted small">
              📅
              {{ trek.start_date || 'TBA' }}
              to
              {{ trek.end_date || 'TBA' }}
            </div>

          </div>

        </div>

      </div>

    </div>

    <!-- ========================= -->
    <!-- BOOKING HISTORY -->
    <!-- ========================= -->

    <div v-if="activeTab === 'history'">

      <div
        v-if="history.length === 0"
        class="text-muted text-center py-5"
      >
        You haven't booked any treks yet.
      </div>

      <div
        v-else
        class="table-responsive shadow-sm border rounded"
      >

        <table class="table table-hover align-middle mb-0">

          <thead class="table-dark">

            <tr>
              <th>Booking ID</th>
              <th>Trek Title</th>
              <th>Location</th>
              <th>Seats</th>
              <th>Total Amount</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>

          </thead>

          <tbody>

            <tr
              v-for="booking in history"
              :key="booking.id"
            >

              <td>
                #{{ booking.id }}
              </td>

              <td class="fw-bold">
                {{ booking.trek_title }}
              </td>

              <td>
                {{ booking.trek_location }}
              </td>

              <td>
                {{ booking.seats_booked || 1 }}
              </td>

              <td>
                ₹{{ booking.total_price }}
              </td>

              <td>
                <span
                  class="badge"
                  :class="booking.status === 'Booked'
                    ? 'bg-success'
                    : 'bg-secondary'"
                >
                  {{ booking.status }}
                </span>
              </td>

              <td>
                {{ booking.created_at || 'N/A' }}
              </td>

              <td>

                <button
                  v-if="booking.status === 'Booked'"
                  type="button"
                  class="btn btn-sm btn-outline-success me-2"
                  @click="downloadTicket(booking.id)"
                >
                  📄 Pass
                </button>

                <button
                  v-if="booking.status === 'Booked'"
                  type="button"
                  class="btn btn-sm btn-outline-danger"
                  @click="cancelBooking(booking.id)"
                >
                  Cancel
                </button>

                <span
                  v-if="booking.status !== 'Booked'"
                  class="text-muted small"
                >
                  N/A
                </span>

              </td>

            </tr>

          </tbody>

        </table>

      </div>

    </div>

  </div>
</template>


<script>
import api from '../api';

export default {
  name: 'UserDashboard',

  data() {
    return {
      
      activeTab: 'available',

      treks: [],
      history: [],
      bookedTrekIds: [],

      searchQuery: '',
      difficulty: '',
      duration: '',

      message: '',
      error: '',

      bookingInProgress: null,

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
        disability_description: ''
      }
    };
  },

  mounted() {
    this.fetchTreks();
    this.fetchHistory();
  },

  methods: {

    /* =========================
       PROFILE
    ========================= */

    async openProfile() {
      this.message = '';
      this.error = '';
      this.showProfile = true;
      this.profileLoading = true;

      try {
        const response = await api.get('/api/user/profile');
        const data = response.data.profile;

        this.profile = {
          full_name: data.full_name || '',
          email: data.email || '',
          contact_number: data.contact_number || '',
          address: data.address || '',
          age: data.age || null,
          has_disability: Boolean(data.has_disability),
          disability_description:
            data.disability_description || ''
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
        this.profile.age !== null &&
        this.profile.age !== '' &&
        (
          Number(this.profile.age) < 1 ||
          Number(this.profile.age) > 120
        )
      ) {
        this.error = 'Age must be between 1 and 120.';
        return;
      }

      if (
        this.profile.has_disability &&
        !this.profile.disability_description.trim()
      ) {
        this.error =
          'Please provide a description of the disability.';
        return;
      }

      this.profileSaving = true;

      try {
        const response = await api.put(
          '/api/user/profile',
          {
            full_name: this.profile.full_name,
            email: this.profile.email,
            contact_number: this.profile.contact_number,
            address: this.profile.address,
            age: this.profile.age,
            has_disability: this.profile.has_disability,
            disability_description:
              this.profile.has_disability
                ? this.profile.disability_description
                : null
          }
        );

        this.message =
          response.data.message ||
          'Profile updated successfully.';

        const data = response.data.profile;

        if (data) {
          this.profile = {
            full_name: data.full_name || '',
            email: data.email || '',
            contact_number: data.contact_number || '',
            address: data.address || '',
            age: data.age || null,
            has_disability: Boolean(data.has_disability),
            disability_description:
              data.disability_description || ''
          };
        }

        this.showProfile = false;

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to update profile.';

      } finally {
        this.profileSaving = false;
      }
    },


    /* =========================
       TABS
    ========================= */

    switchTab(tab) {
      this.activeTab = tab;
      this.message = '';
      this.error = '';

      if (tab === 'available') {
        this.fetchTreks();
      }

      if (tab === 'history') {
        this.fetchHistory();
      }
    },


    /* =========================
       TREKS
    ========================= */

    async fetchTreks() {
      try {
        const params = new URLSearchParams();

        params.append('search', this.searchQuery);

        if (this.difficulty) {
          params.append('difficulty', this.difficulty);
        }

        if (this.duration) {
          params.append('duration', this.duration);
        }

        const response = await api.get(
          `/api/user/treks?${params.toString()}`
        );

        this.treks = response.data.treks || [];

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to load treks.';
      }
    },

    clearFilters() {
      this.searchQuery = '';
      this.difficulty = '';
      this.duration = '';
      this.fetchTreks();
    },


    /* =========================
       BOOKING
    ========================= */

    isBooked(trekId) {
      return this.bookedTrekIds.includes(
        Number(trekId)
      );
    },

    async bookTrek(trekId) {
      this.message = '';
      this.error = '';
      this.bookingInProgress = trekId;

      try {
        const response = await api.post(
          '/api/user/bookings',
          {
            trek_id: trekId
          }
        );

        this.message =
          response.data.message ||
          'Trek booked successfully!';

        await this.fetchHistory();
        await this.fetchTreks();

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Booking failed.';

      } finally {
        this.bookingInProgress = null;
      }
    },

    async fetchHistory() {
      try {
        const response = await api.get(
          '/api/user/my-bookings'
        );

        this.history =
          response.data.history || [];

        this.bookedTrekIds =
          this.history
            .filter(
              booking =>
                booking.status === 'Booked'
            )
            .map(
              booking =>
                Number(booking.trek_id)
            );

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to load booking history.';
      }
    },

    async cancelBooking(bookingId) {
      if (
        !confirm(
          'Are you sure you want to cancel this booking?'
        )
      ) {
        return;
      }

      this.message = '';
      this.error = '';

      try {
        const response = await api.delete(
          `/api/user/bookings/${bookingId}`
        );

        this.message =
          response.data.message ||
          'Booking cancelled successfully.';

        await this.fetchHistory();
        await this.fetchTreks();

      } catch (err) {
        this.error =
          err.response?.data?.error ||
          'Failed to cancel booking.';
      }
    },


    /* =========================
       TICKET
    ========================= */
    async downloadBookingHistory() {
      this.message = '';
      this.error = '';

      try {
        const response = await api.get(
          '/api/user/export-bookings',
          {
            responseType: 'blob'
          }
        );

        const blob = new Blob(
          [response.data],
          { type: 'text/csv' }
        );

        const link = document.createElement('a');

        link.href = window.URL.createObjectURL(blob);

        link.download = 'booking_history.csv';

        document.body.appendChild(link);

        link.click();

        document.body.removeChild(link);

        window.URL.revokeObjectURL(link.href);

        this.message =
          'Booking history downloaded successfully.';

      } catch (err) {
        console.error(
          'Booking history export error:',
          err
        );

        this.error =
          'Failed to download booking history.';
      }
    },

    async downloadTicket(bookingId) {
      this.message = '';
      this.error = '';

      try {
        const response = await api.get(
          `/api/user/download-ticket/${bookingId}`,
          {
            responseType: 'blob'
          }
        );

        const blob = new Blob(
          [response.data],
          { type: 'application/pdf' }
        );

        const link =
          document.createElement('a');

        link.href =
          window.URL.createObjectURL(blob);

        link.download =
          `ticket_${bookingId}.pdf`;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        window.URL.revokeObjectURL(
          link.href
        );

      } catch (err) {
        this.error =
          'Ticket PDF is currently generating or unavailable. Please try again in a moment.';
      }
    }
  }
};
</script>