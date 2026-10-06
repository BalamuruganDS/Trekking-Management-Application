<template>
  <div class="container py-4">

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2>Admin Dashboard</h2>
        <p class="text-muted mb-0">
          System Control, Trek Scheduling & Staff Allocations
        </p>
      </div>

      <button
        class="btn btn-outline-dark"
        @click="triggerExport"
      >
        📥 Export Bookings CSV
      </button>
    </div>


    <!-- Alerts -->
    <div v-if="message" class="alert alert-success">
      {{ message }}
      <button
        class="btn-close float-end"
        @click="message = ''"
      ></button>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
      <button
        class="btn-close float-end"
        @click="error = ''"
      ></button>
    </div>


    <!-- Statistics -->
    <div class="row mb-4">

      <div class="col-md-3">
        <div class="card text-white bg-primary mb-3 shadow-sm border-0">
          <div class="card-body">
            <h6>Total Trekkers</h6>
            <p class="fs-3 fw-bold mb-0">
              {{ stats.total_users || 0 }}
            </p>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card text-white bg-success mb-3 shadow-sm border-0">
          <div class="card-body">
            <h6>Total Staff</h6>
            <p class="fs-3 fw-bold mb-0">
              {{ stats.total_staff || 0 }}
            </p>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card text-white bg-info mb-3 shadow-sm border-0">
          <div class="card-body">
            <h6>Total Treks</h6>
            <p class="fs-3 fw-bold mb-0">
              {{ stats.total_treks || 0 }}
            </p>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card text-white bg-warning mb-3 shadow-sm border-0">
          <div class="card-body">
            <h6>Total Bookings</h6>
            <p class="fs-3 fw-bold mb-0">
              {{ stats.total_bookings || 0 }}
            </p>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card text-white bg-dark mb-3 shadow-sm border-0">
          <div class="card-body">
            <h6 class="card-title text-white-50">Total Revenue</h6>
            <p class="card-text fs-3 fw-bold mb-0">₹{{ stats.total_revenue || 0 }}</p>
          </div>
        </div>
      </div>

    </div>


    <!-- Create Forms -->
    <div class="row mb-5">

      <!-- Create Trek -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm h-100 border-0">

          <div class="card-header bg-dark text-white fw-bold">
            Create New Trek
          </div>

          <div class="card-body">

            <form @submit.prevent="createTrek">

              <div class="mb-3">
                <label class="form-label fw-bold">
                  Trek Title
                </label>

                <input
                  v-model="newTrek.title"
                  type="text"
                  class="form-control"
                  placeholder="e.g. Kedarkantha Peak"
                  required
                >
              </div>


              <div class="mb-3">
                <label class="form-label fw-bold">
                  Location
                </label>

                <input
                  v-model="newTrek.location"
                  type="text"
                  class="form-control"
                  placeholder="e.g. Uttarkashi"
                  required
                >
              </div>


              <div class="mb-3">
                <label class="form-label fw-bold">
                  Description
                </label>

                <textarea
                  v-model="newTrek.description"
                  class="form-control"
                  rows="3"
                  placeholder="Describe the trek..."
                ></textarea>
              </div>


              <div class="row mb-3">

                <div class="col">
                  <label class="form-label fw-bold">
                    Price (₹)
                  </label>

                  <input
                    v-model="newTrek.price"
                    type="number"
                    class="form-control"
                    required
                  >
                </div>

                <div class="col">
                  <label class="form-label fw-bold">
                    Difficulty
                  </label>

                  <select
                    v-model="newTrek.difficulty"
                    class="form-select"
                  >
                    <option>Easy</option>
                    <option>Moderate</option>
                    <option>Hard</option>
                  </select>
                </div>

              </div>


              <div class="row mb-3">

                <div class="col">
                  <label class="form-label fw-bold">
                    Start Date
                  </label>

                  <input
                    v-model="newTrek.start_date"
                    type="date"
                    class="form-control"
                    required
                  >
                </div>

                <div class="col">
                  <label class="form-label fw-bold">
                    End Date
                  </label>

                  <input
                    v-model="newTrek.end_date"
                    type="date"
                    class="form-control"
                    required
                  >
                </div>

              </div>


              <button
                type="submit"
                class="btn btn-primary w-100"
              >
                Add Trek
              </button>

            </form>

          </div>
        </div>
      </div>


      <!-- Create Staff -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm h-100 border-0">

          <div class="card-header bg-dark text-white fw-bold">
            Register Trek Staff
          </div>

          <div class="card-body">

            <form @submit.prevent="createStaff">

              <div class="mb-3">
                <label class="form-label fw-bold">
                  Full Name
                </label>

                <input
                  v-model="newStaff.full_name"
                  type="text"
                  class="form-control"
                  required
                >
              </div>


              <div class="mb-3">
                <label class="form-label fw-bold">
                  Email
                </label>

                <input
                  v-model="newStaff.email"
                  type="email"
                  class="form-control"
                  required
                >
              </div>


              <div class="mb-3">
                <label class="form-label fw-bold">
                  Contact Number
                </label>

                <input
                  v-model="newStaff.contact_number"
                  type="text"
                  class="form-control"
                  placeholder="Optional"
                >
              </div>


              <div class="mb-3">
                <label class="form-label fw-bold">
                  Password
                </label>

                <input
                  v-model="newStaff.password"
                  type="password"
                  class="form-control"
                  required
                >
              </div>


              <button
                type="submit"
                class="btn btn-success w-100"
              >
                Create Staff Account
              </button>

            </form>

          </div>
        </div>
      </div>

    </div>

<!-- ================= PENDING TREKS ================= -->

<div class="card shadow-sm mb-5 border-0">

  <div class="card-header bg-warning text-dark">
    <h5 class="mb-0 fs-6 fw-bold">
      Pending Trek Approval
    </h5>
  </div>

  <div class="table-responsive">

    <table class="table table-hover align-middle mb-0">

      <thead class="table-light text-center">

      <tr>
          <th>Title</th>
          <th>Location</th>
          <th>Price</th>
          <th>Difficulty</th>
          <th>Status</th>
          <th>Assigned Staff</th>
          <th>Actions</th>
        </tr>

      </thead>

      <tbody>

        <tr
          v-for="trek in pendingTreks"
          :key="trek.id"
          class="text-center"
        >

          <td class="fw-bold">
            {{ trek.title }}
          </td>

          <td>
            {{ trek.location }}
          </td>

          <td>
            {{ trek.price }}
          </td>
          <td>
            <span class="badge bg-info text-dark">
              {{ trek.difficulty }}
            </span>
          </td>
          <td>

            <span
              class="badge"
              :class="{
                'bg-warning text-dark':
                  trek.status === 'Pending',

                'bg-success':
                  trek.status === 'Approved' ||
                  trek.status === 'Open',

                'bg-secondary':
                  trek.status === 'Closed',

                'bg-primary':
                  trek.status === 'Completed',

                'bg-danger':
                  trek.status === 'Blocked'
              }"
            >
              {{ trek.status }}
            </span>

          </td>


         <select
                  v-model="trek.assigned_staff_id"
                  @change="
                    assignStaff(
                      trek.id,
                      trek.assigned_staff_id
                    )
                  "
                  class="form-select form-select-sm"
                >

                  <option :value="null">
                    -- Unassigned --
                  </option>

                  <option
                    v-for="s in staff"
                    :key="s.id"
                    :value="s.id"
                  >
                    {{ s.full_name }}
                  </option>

                </select>

          <td>

            <div
              class="d-flex justify-content-center gap-2"
            >

              <button
                class="btn btn-sm btn-outline-success"
                @click="changeTrekStatus(trek.id, 'Open')"
              >
                Approve
              </button>

              <button
                class="btn btn-sm btn-outline-danger"
                @click="changeTrekStatus(trek.id, 'Blocked')"
              >
                Reject
              </button>

              <button
                class="btn btn-sm btn-outline-primary"
                @click="openEditModal(trek)"
              >
                Edit
              </button>

            </div>

          </td>

        </tr>

        <tr v-if="pendingTreks.length === 0">

          <td
            colspan="6"
            class="text-center py-4 text-muted"
          >
            No pending treks.
          </td>

        </tr>

      </tbody>

    </table>

  </div>

</div>
    <!-- ================= USERS ================= -->

    <div class="card shadow-sm mb-5 border-0">

      <div
        class="card-header bg-secondary text-white
               d-flex justify-content-between align-items-center"
      >

        <h5 class="mb-0 fs-6 fw-bold">
          Manage Registered Trekkers
        </h5>

        <input
          v-model="userSearch"
          @input="fetchUsers"
          type="text"
          class="form-control form-control-sm"
          style="max-width: 250px"
          placeholder="Search by name or email..."
        >

      </div>


      <div class="table-responsive">

        <table class="table table-hover align-middle mb-0">

          <thead class="table-light text-center">

            <tr>
              <th>ID</th>
              <th>Full Name</th>
              <th>Email</th>
              <th>Registered Trek</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>

          </thead>


          <tbody>

            <tr
              v-for="user in users"
              :key="user.id"
              class="text-center"
            >

              <td>
                #{{ user.id }}
              </td>


              <td>

                <button
                  class="btn btn-link p-0 fw-bold
                         text-dark text-decoration-none"
                  @click="viewUser(user.id)"
                >
                  {{ user.full_name }}
                </button>

              </td>


              <td>
                {{ user.email }}
              </td>


              <!-- Registered Trek -->
              <td>

                <span
                  v-if="
                    user.registered_treks &&
                    user.registered_treks.length
                  "
                  class="fw-bold"
                >
                  {{ user.registered_treks.join(', ') }}
                </span>

                <span
                  v-else
                  class="text-muted"
                >
                  None
                </span>

              </td>


              <td>

                <span
                  class="badge"
                  :class="{
                    'bg-success':
                      user.status === 'Active',

                    'bg-warning text-dark':
                      user.status === 'Deactive',

                    'bg-danger':
                      user.status === 'Blacklisted'
                  }"
                >
                  {{ user.status || 'Active' }}
                </span>

              </td>


              <td>

                <div
                  class="d-flex justify-content-center
                         gap-1 flex-wrap"
                >

                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="viewUser(user.id)"
                  >
                    View
                  </button>


                  <button
                    v-if="user.status !== 'Active'"
                    class="btn btn-sm btn-outline-success"
                    @click="
                      updateStatus(user.id, 'Active')
                    "
                  >
                    Activate
                  </button>


                  <button
                    v-if="user.status !== 'Blacklisted'"
                    class="btn btn-sm btn-outline-danger"
                    @click="
                      updateStatus(
                        user.id,
                        'Blacklisted'
                      )
                    "
                  >
                    Blacklist
                  </button>

                </div>

              </td>

            </tr>


            <tr v-if="users.length === 0">

              <td
                colspan="6"
                class="text-center py-3 text-muted"
              >
                No trekkers found.
              </td>

            </tr>

          </tbody>

        </table>

      </div>
    </div>


    <!-- ================= STAFF ================= -->

    <div class="card shadow-sm mb-5 border-0">

      <div
        class="card-header bg-secondary text-white
               d-flex justify-content-between align-items-center"
      >

        <h5 class="mb-0 fs-6 fw-bold">
          Manage Trek Staff
        </h5>

        <input
          v-model="staffSearch"
          @input="fetchStaff"
          type="text"
          class="form-control form-control-sm"
          style="max-width: 250px"
          placeholder="Search staff..."
        >

      </div>


      <div class="table-responsive">

        <table class="table table-hover align-middle mb-0">

          <thead class="table-light text-center">

            <tr>
              <th>ID</th>
              <th>Full Name</th>
              <th>Email</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>

          </thead>


          <tbody>

            <tr
              v-for="member in staff"
              :key="member.id"
              class="text-center"
            >

              <td>
                #{{ member.id }}
              </td>

              <td>

                <button
                  class="btn btn-link p-0 fw-bold
                         text-dark text-decoration-none"
                  @click="viewStaff(member.id)"
                >
                  {{ member.full_name }}
                </button>

              </td>

              <td>
                {{ member.email }}
              </td>

              <td>

                <span
                  class="badge"
                  :class="{
                    'bg-success':
                      member.status === 'Active',

                    'bg-danger':
                      member.status === 'Blacklisted',

                    'bg-warning text-dark':
                      member.status === 'Deactive'
                  }"
                >
                  {{ member.status || 'Active' }}
                </span>

              </td>

              <td>

                <div
                  class="d-flex justify-content-center gap-1"
                >

                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="viewStaff(member.id)"
                  >
                    View
                  </button>

                  <button
                    v-if="member.status !== 'Active'"
                    class="btn btn-sm btn-outline-success"
                    @click="
                      updateStatus(
                        member.id,
                        'Active'
                      )
                    "
                  >
                    Activate
                  </button>

                  <button
                    v-if="member.status !== 'Blacklisted'"
                    class="btn btn-sm btn-outline-danger"
                    @click="
                      updateStatus(
                        member.id,
                        'Blacklisted'
                      )
                    "
                  >
                    Blacklist
                  </button>

                </div>

              </td>

            </tr>


            <tr v-if="staff.length === 0">

              <td
                colspan="5"
                class="text-center py-3 text-muted"
              >
                No staff accounts found.
              </td>

            </tr>

          </tbody>

        </table>

      </div>
    </div>


    <!-- ================= TREKS ================= -->

    <div class="card shadow-sm mb-5 border-0">

      <div
        class="card-header bg-secondary text-white
               d-flex justify-content-between align-items-center"
      >

        <h5 class="mb-0 fs-6 fw-bold">
          Manage Treks & Assign Staff
        </h5>

        <input
          v-model="trekSearch"
          @input="fetchTreks"
          type="text"
          class="form-control form-control-sm"
          style="max-width: 250px"
          placeholder="Search treks..."
        >

      </div>


      <div class="table-responsive">

        <table class="table table-hover align-middle mb-0">

          <thead class="table-light text-center">

            <tr>
              <th>Title</th>
              <th>Location</th>
              <th>Price</th>
              <th>Difficulty</th>
              <th>Assigned Staff</th>
              <th>Actions</th>
            </tr>

          </thead>


          <tbody>

            <tr
              v-for="trek in treks"
              :key="trek.id"
              class="text-center"
            >

              <td>

                <button
                  class="btn btn-link p-0 fw-bold
                         text-dark text-decoration-none"
                  @click="viewTrek(trek)"
                >
                  {{ trek.title }}
                </button>

              </td>

              <td>
                {{ trek.location }}
              </td>

              <td>
                ₹{{ trek.price }}
              </td>

              <td>

                <span class="badge bg-info text-dark">
                  {{ trek.difficulty }}
                </span>

              </td>

              <td>

                <select
                  v-model="trek.assigned_staff_id"
                  @change="
                    assignStaff(
                      trek.id,
                      trek.assigned_staff_id
                    )
                  "
                  class="form-select form-select-sm"
                >

                  <option :value="null">
                    -- Unassigned --
                  </option>

                  <option
                    v-for="s in staff"
                    :key="s.id"
                    :value="s.id"
                  >
                    {{ s.full_name }}
                  </option>

                </select>

              </td>


              <td>

                <div
                  class="d-flex justify-content-center gap-2 flex-wrap"
                >

                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click="openEditModal(trek)"
                  >
                    Edit
                  </button>

                  <button
                    v-if="
                      trek.status !== 'Blocked' &&
                      trek.status !== 'Completed'
                    "
                    class="btn btn-sm btn-outline-danger"
                    @click="
                      changeTrekStatus(trek.id, 'Blocked')
                    "
                  >
                    Block
                  </button>

                  <button
                    v-if="trek.status === 'Blocked'"
                    class="btn btn-sm btn-outline-success"
                    @click="
                      changeTrekStatus(trek.id, 'Open')
                    "
                  >
                    Re-approve
                  </button>

                  <button
                    class="btn btn-sm btn-outline-danger"
                    @click="deleteTrek(trek.id)"
                  >
                    Delete
                  </button>

                </div>

              </td>

            </tr>


            <tr v-if="treks.length === 0">

              <td
                colspan="6"
                class="text-center py-3 text-muted"
              >
                No treks created yet.
              </td>

            </tr>

          </tbody>

        </table>

      </div>
    </div>


    <!-- ================= HISTORICAL BOOKINGS ================= -->

    <div class="card shadow-sm mb-5 border-0">

      <div
        class="card-header bg-dark text-white
               d-flex justify-content-between align-items-center"
      >

        <h5 class="mb-0 fs-6 fw-bold">
          Historical Trekking Bookings
        </h5>

        <button
          class="btn btn-sm btn-light"
          @click="fetchBookings"
        >
          🔄 Refresh
        </button>

      </div>


      <div class="table-responsive">

        <table class="table table-hover align-middle mb-0">

          <thead class="table-light text-center">

            <tr>
              <th>Booking ID</th>
              <th>User</th>
              <th>Trek</th>
              <th>Location</th>
              <th>Seats</th>
              <th>Booking Date</th>
              <th>Status</th>
            </tr>

          </thead>


          <tbody>

            <tr
              v-for="booking in bookings"
              :key="booking.id"
              class="text-center"
            >

              <td>
                #{{ booking.id }}
              </td>

              <td class="fw-bold">
                {{ booking.user_name }}
              </td>

              <td class="fw-bold">
                {{ booking.trek_title }}
              </td>

              <td>
                {{ booking.location }}
              </td>

              <td>
                {{ booking.seats }}
              </td>

              <td>
                {{ booking.booking_date }}
              </td>

              <td>

                <span
                  class="badge"
                  :class="{
                    'bg-success':
                      booking.status === 'Booked',

                    'bg-danger':
                      booking.status === 'Cancelled',

                    'bg-secondary':
                      booking.status === 'Completed'
                  }"
                >
                  {{ booking.status }}
                </span>

              </td>

            </tr>


            <tr v-if="bookings.length === 0">

              <td
                colspan="7"
                class="text-center py-4 text-muted"
              >
                No booking history found.
              </td>

            </tr>

          </tbody>

        </table>

      </div>
    </div>


    <!-- ================= PROFILE MODAL ================= -->

    <div
      v-if="profile"
      class="modal fade show d-block"
      style="background: rgba(0,0,0,.5)"
    >

      <div class="modal-dialog modal-lg modal-dialog-centered">

        <div class="modal-content">

          <div class="modal-header bg-dark text-white">

            <h5 class="modal-title">
              👤 {{ profile.role }} Profile
            </h5>

            <button
              class="btn-close btn-close-white"
              @click="profile = null"
            ></button>

          </div>


          <div class="modal-body">

            <div class="row">

              <div class="col-md-6 mb-3">
                <strong>Name</strong>
                <div>
                  {{ profile.full_name || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Email</strong>
                <div>
                  {{ profile.email || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Contact</strong>
                <div>
                  {{ profile.contact_number || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Age</strong>
                <div>
                  {{ profile.age || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Status</strong>
                <div>
                  {{ profile.status || 'N/A' }}
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <strong>Role</strong>
                <div>
                  {{ profile.role || 'N/A' }}
                </div>
              </div>

              <div class="col-12 mb-3">
                <strong>Address</strong>
                <div>
                  {{ profile.address || 'N/A' }}
                </div>
              </div>

              <div
                v-if="profile.role === 'Staff'"
                class="col-12 mb-3"
              >
                <strong>Specialization</strong>
                <div>
                  {{ profile.specialization || 'N/A' }}
                </div>
              </div>

              <div class="col-12 mb-3">
                <strong>Disability</strong>
                <div>
                  {{ profile.has_disability
                    ? 'Yes'
                    : 'No'
                  }}
                </div>
              </div>

              <div
                v-if="profile.has_disability"
                class="col-12"
              >
                <strong>
                  Disability Description
                </strong>

                <div>
                  {{
                    profile.disability_description ||
                    'N/A'
                  }}
                </div>
              </div>

            </div>

          </div>


          <div class="modal-footer">

            <button
              class="btn btn-secondary"
              @click="profile = null"
            >
              Close
            </button>

          </div>

        </div>

      </div>

    </div>


    <!-- ================= TREK DETAILS MODAL ================= -->

    <div
      v-if="selectedTrek"
      class="modal fade show d-block"
      style="background: rgba(0,0,0,.5)"
    >

      <div class="modal-dialog modal-lg modal-dialog-centered">

        <div class="modal-content">

          <div class="modal-header bg-dark text-white">

            <h5 class="modal-title">
              🏔️ {{ selectedTrek.title }}
            </h5>

            <button
              class="btn-close btn-close-white"
              @click="selectedTrek = null"
            ></button>

          </div>


          <div class="modal-body">

            <p>
              <strong>Location:</strong>
              {{ selectedTrek.location }}
            </p>

            <p>
              <strong>Difficulty:</strong>
              {{ selectedTrek.difficulty }}
            </p>

            <p>
              <strong>Price:</strong>
              ₹{{ selectedTrek.price }}
            </p>

            <p>
              <strong>Capacity:</strong>
              {{ selectedTrek.max_capacity || 'N/A' }}
            </p>

            <p>
              <strong>Available Seats:</strong>
              {{ selectedTrek.available_seats || 0 }}
            </p>

            <p>
              <strong>Dates:</strong>
              {{ selectedTrek.start_date || 'N/A' }}
              to
              {{ selectedTrek.end_date || 'N/A' }}
            </p>

            <hr>

            <h6 class="fw-bold">
              Description
            </h6>

            <p class="text-muted">
              {{
                selectedTrek.description ||
                'No description provided.'
              }}
            </p>

          </div>


          <div class="modal-footer">

            <button
              class="btn btn-secondary"
              @click="selectedTrek = null"
            >
              Close
            </button>

          </div>

        </div>

      </div>

    </div>


    <!-- ================= EDIT TREK MODAL ================= -->

    <div
      v-if="editingTrek"
      class="modal fade show d-block"
      style="background: rgba(0,0,0,.5)"
    >

      <div class="modal-dialog modal-lg">

        <div class="modal-content">

          <div class="modal-header bg-dark text-white">

            <h5 class="modal-title">
              Edit Trek
            </h5>

            <button
              class="btn-close btn-close-white"
              @click="closeEditModal"
            ></button>

          </div>


          <form @submit.prevent="updateTrek">

            <div class="modal-body">

              <div class="mb-3">

                <label class="form-label fw-bold">
                  Trek Title
                </label>

                <input
                  v-model="editingTrek.title"
                  type="text"
                  class="form-control"
                  required
                >

              </div>


              <div class="mb-3">

                <label class="form-label fw-bold">
                  Location
                </label>

                <input
                  v-model="editingTrek.location"
                  type="text"
                  class="form-control"
                  required
                >

              </div>


              <div class="mb-3">

                <label class="form-label fw-bold">
                  Description
                </label>

                <textarea
                  v-model="editingTrek.description"
                  class="form-control"
                  rows="3"
                ></textarea>

              </div>


              <div class="row mb-3">

                <div class="col">

                  <label class="form-label fw-bold">
                    Price
                  </label>

                  <input
                    v-model="editingTrek.price"
                    type="number"
                    class="form-control"
                    required
                  >

                </div>


                <div class="col">

                  <label class="form-label fw-bold">
                    Difficulty
                  </label>

                  <select
                    v-model="editingTrek.difficulty"
                    class="form-select"
                  >
                    <option>Easy</option>
                    <option>Moderate</option>
                    <option>Hard</option>
                  </select>

                </div>

              </div>


              <div class="row">

                <div class="col">

                  <label class="form-label fw-bold">
                    Start Date
                  </label>

                  <input
                    v-model="editingTrek.start_date"
                    type="date"
                    class="form-control"
                  >

                </div>


                <div class="col">

                  <label class="form-label fw-bold">
                    End Date
                  </label>

                  <input
                    v-model="editingTrek.end_date"
                    type="date"
                    class="form-control"
                  >

                </div>

              </div>

            </div>


            <div class="modal-footer">

              <button
                type="button"
                class="btn btn-secondary"
                @click="closeEditModal"
              >
                Cancel
              </button>

              <button
                type="submit"
                class="btn btn-primary"
              >
                Save Changes
              </button>

            </div>

          </form>

        </div>

      </div>

    </div>

  </div>
</template>


<script>
import api from '../api';

export default {
  name: 'AdminDashboard',

  data() {
    return {

      stats: {
        total_users: 0,
        total_staff: 0,
        total_treks: 0,
        total_bookings: 0,
        total_revenue: 0
      },

      message: '',
      error: '',

      userSearch: '',
      staffSearch: '',
      trekSearch: '',

      users: [],
      staff: [],
      treks: [],
      pendingTreks: [],
      bookings: [],

      newTrek: {
        title: '',
        location: '',
        description: '',
        price: '',
        difficulty: 'Moderate',
        start_date: '',
        end_date: ''
      },

      newStaff: {
        full_name: '',
        email: '',
        password: '',
        contact_number: ''
      },

      editingTrek: null,
      selectedTrek: null,
      profile: null
    };
  },


  mounted() {
    this.fetchStats();
    this.fetchUsers();
    this.fetchStaff();
    this.fetchTreks();
    this.fetchPendingTreks();
    this.fetchBookings();
  },


  methods: {

    async fetchStats() {
      try {

        const res =
          await api.get('/api/admin/stats');

        this.stats =
          res.data.stats || {};

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to load system stats.';

      }
    },

    async changeTrekStatus(trekId, status) {

      this.message = '';
      this.error = '';

      try {

        const res = await api.patch(
          `/api/admin/treks/${trekId}/status`,
          { status }
        );

        this.message =
          res.data.message ||
          'Trek status updated.';

        await this.fetchPendingTreks();
        await this.fetchTreks();

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to update trek status.';

      }
    },

    async fetchUsers() {
      try {

        const res = await api.get(
          `/api/admin/users?search=${encodeURIComponent(
            this.userSearch
          )}`
        );

        this.users =
          res.data.users || [];

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to fetch registered trekkers.';

      }
    },


    async fetchStaff() {
      try {

        const res = await api.get(
          `/api/admin/staff?search=${encodeURIComponent(
            this.staffSearch
          )}`
        );

        this.staff =
          res.data.staff || [];

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to fetch staff members.';

      }
    },


    async fetchTreks() {
      try {

        const res = await api.get(
          `/api/admin/treks?search=${encodeURIComponent(
            this.trekSearch
          )}`
        );

        this.treks =
          res.data.treks || [];

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to fetch treks.';

      }
    },

    async fetchPendingTreks() {
      try {

        const res = await api.get(
          '/api/admin/treks/pending'
        );

        this.pendingTreks =
          res.data.treks || [];

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to fetch pending treks.';

      }
    },
    async fetchBookings() {
      try {

        const res =
          await api.get('/api/admin/bookings');

        this.bookings =
          res.data.bookings || [];

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to fetch booking history.';

      }
    },


    async createTrek() {

      this.message = '';
      this.error = '';

      try {

        const res = await api.post(
          '/api/admin/treks',
          this.newTrek
        );

        this.message =
          res.data.message ||
          'Trek created successfully!';

        this.newTrek = {
          title: '',
          location: '',
          description: '',
          price: '',
          difficulty: 'Moderate',
          start_date: '',
          end_date: ''
        };

        await this.fetchStats();
        await this.fetchTreks();
        await this.fetchPendingTreks();
      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to create trek.';

      }
    },


    async createStaff() {

      this.message = '';
      this.error = '';

      try {

        const res = await api.post(
          '/api/admin/staff',
          this.newStaff
        );

        this.message =
          res.data.message ||
          'Staff created successfully!';

        this.newStaff = {
          full_name: '',
          email: '',
          password: '',
          contact_number: ''
        };

        await this.fetchStats();
        await this.fetchStaff();

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to create staff account.';

      }
    },


    async updateStatus(userId, status) {

      this.message = '';
      this.error = '';

      try {

        const res = await api.patch(
          `/api/admin/users/${userId}/status`,
          { status }
        );

        this.message =
          res.data.message;

        await this.fetchUsers();
        await this.fetchStaff();

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to update user status.';

      }
    },


    async assignStaff(trekId, staffId) {

      this.message = '';
      this.error = '';

      try {

        const res = await api.patch(
          `/api/admin/treks/${trekId}/assign-staff`,
          {
            assigned_staff_id: staffId
          }
        );

        this.message =
          res.data.message;

        await this.fetchTreks();

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to assign staff.';

      }
    },


    async deleteTrek(trekId) {

      if (
        !confirm(
          'Are you sure you want to delete this trek?'
        )
      ) {
        return;
      }

      this.message = '';
      this.error = '';

      try {

        const res = await api.delete(
          `/api/admin/treks/${trekId}`
        );

        this.message =
          res.data.message;

        await this.fetchTreks();
        await this.fetchStats();

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to delete trek.';

      }
    },


    viewTrek(trek) {
      this.selectedTrek = trek;
    },


    openEditModal(trek) {
      this.editingTrek = {
        ...trek
      };
    },


    closeEditModal() {
      this.editingTrek = null;
    },


    async updateTrek() {

      this.message = '';
      this.error = '';

      try {

        const res = await api.put(
          `/api/admin/treks/${this.editingTrek.id}`,
          this.editingTrek
        );

        this.message =
          res.data.message ||
          'Trek updated successfully!';

        this.closeEditModal();

        await this.fetchTreks();

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to update trek.';

      }
    },


    async viewUser(userId) {

      this.error = '';

      try {

        const res = await api.get(
          `/api/admin/users/${userId}/profile`
        );

        this.profile =
          res.data.profile;

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to load user profile.';

      }
    },


    async viewStaff(staffId) {

      this.error = '';

      try {

        const res = await api.get(
          `/api/admin/staff/${staffId}/profile`
        );

        this.profile =
          res.data.profile;

      } catch (err) {

        this.error =
          err.response?.data?.error ||
          'Failed to load staff profile.';

      }
    },


    async triggerExport() {
      this.message = '';
      this.error = '';

      try {
        const res = await api.post(
          '/api/admin/export-csv',
          {},
          {
            responseType: 'blob'
          }
        );

        const blob = new Blob([res.data], {
          type: 'text/csv'
        });

        const url = window.URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = 'bookings_export.csv';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        window.URL.revokeObjectURL(url);

        this.message = 'CSV exported, downloaded, and sent to admin email successfully!';
      } catch (err) {
        this.error = 'Failed to export CSV.';
      }
    }

  }

};
</script>