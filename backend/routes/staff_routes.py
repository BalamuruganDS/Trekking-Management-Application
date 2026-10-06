from flask import Blueprint, jsonify, request
from extensions import db
from models.user import User
from models.booking import Booking
from models.trek import Trek
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity, jwt_required
from utils.cache import clear_trek_cache


staff_bp = Blueprint('staff', __name__, url_prefix='/api/staff')

@staff_bp.route('/my-treks', methods=['GET'])
@role_required('Staff')
def get_my_assigned_treks():

    current_user_id = int(get_jwt_identity())

    assigned_treks = Trek.query.filter(
        Trek.assigned_staff_id == current_user_id,
        Trek.status.notin_(['Pending', 'Blocked'])
    ).all()


    return jsonify({
        'status': 'success',
        'treks': [t.to_dict() for t in assigned_treks]
    }), 200

    

    


@staff_bp.route('/treks/<int:trek_id>/slots', methods=['PATCH'])
@role_required('Staff')
def update_trek_slots(trek_id):
    current_user_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if trek.assigned_staff_id != current_user_id:
        return jsonify({'error': 'Unauthorized: Trek not assigned to you'}), 403

    data = request.get_json() or {}
    new_slots = data.get('available_seats')

    if new_slots is None or not isinstance(new_slots, int) or new_slots < 0:
        return jsonify({'error': 'Available slots must be a valid non-negative integer'}), 400

    trek.available_seats = new_slots
    db.session.commit()
    clear_trek_cache()

    return jsonify({
        'message': f'Available slots updated to {new_slots}.',
        'trek': trek.to_dict()
    }), 200


@staff_bp.route('/treks/<int:trek_id>/status', methods=['PATCH'])
@role_required('Staff')
def update_trek_status(trek_id):
    current_user_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if trek.assigned_staff_id != current_user_id:
        return jsonify({'error': 'Unauthorized: Trek not assigned to you'}), 403

    data = request.get_json() or {}
    new_status = data.get('status')

    valid_statuses = ['Open', 'Closed', 'Completed']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Allowed values: {", ".join(valid_statuses)}'}), 400

    trek.status = new_status
    db.session.commit()
    clear_trek_cache()
    return jsonify({
        'message': f'Trek status updated to {new_status}.',
        'trek': trek.to_dict()
    }), 200


@staff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@role_required('Staff')
def get_trek_participants(trek_id):
    current_user_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({'error': 'Trek not found'}), 404

    if trek.assigned_staff_id != current_user_id:
        return jsonify({'error': 'Unauthorized: Trek not assigned to you'}), 403

    bookings = Booking.query.filter_by(trek_id=trek_id, status='Booked').all()
    
    participants = []
    for b in bookings:
        if b.user:
            user_data = b.user.to_dict()
            user_data['seats_booked'] = getattr(b, 'seats_booked', 1)
            user_data['booking_id'] = b.id
            participants.append(user_data)

    return jsonify({
        'status': 'success',
        'trek_id': trek_id,
        'trek_title': trek.title,
        'total_participants': len(participants),
        'participants': participants
    }), 200




# ==============================================================================
# STAFF PROFILE
# ==============================================================================

@staff_bp.route('/profile', methods=['GET'])
@role_required('Staff')
def get_staff_profile():
    """Get the currently logged-in staff member's profile."""

    staff_id = get_jwt_identity()

    staff = User.query.get(staff_id)

    if not staff:
        return jsonify({
            'error': 'Staff member not found'
        }), 404

    return jsonify({
        'status': 'success',
        'profile': staff.to_dict()
    }), 200


@staff_bp.route('/profile', methods=['PUT'])
@role_required('Staff')
def update_staff_profile():
    """Update the currently logged-in staff member's profile."""

    staff_id = get_jwt_identity()

    staff = User.query.get(staff_id)

    if not staff:
        return jsonify({
            'error': 'Staff member not found'
        }), 404

    data = request.get_json() or {}

    # --------------------------------------------------
    # Get profile data
    # --------------------------------------------------

    full_name = data.get('full_name')
    email = data.get('email')
    contact_number = data.get('contact_number')
    address = data.get('address')
    age = data.get('age')
    has_disability = data.get(
        'has_disability',
        False
    )
    disability_description = data.get(
        'disability_description'
    )
    specialization = data.get(
        'specialization'
    )

    # --------------------------------------------------
    # Validate name
    # --------------------------------------------------

    if not full_name or not full_name.strip():
        return jsonify({
            'error': 'Full name is required.'
        }), 400

    # --------------------------------------------------
    # Validate email
    # --------------------------------------------------

    if not email or not email.strip():
        return jsonify({
            'error': 'Email is required.'
        }), 400

    email = email.strip()

    existing_user = User.query.filter(
        User.email == email,
        User.id != staff.id
    ).first()

    if existing_user:
        return jsonify({
            'error': 'This email is already being used.'
        }), 400

    # --------------------------------------------------
    # Validate age
    # --------------------------------------------------

    if age is not None and age != '':

        try:
            age = int(age)

        except (ValueError, TypeError):
            return jsonify({
                'error': 'Age must be a valid number.'
            }), 400

        if age < 1 or age > 120:
            return jsonify({
                'error': 'Age must be between 1 and 120.'
            }), 400

    else:
        age = None

    # --------------------------------------------------
    # Handle disability correctly
    # --------------------------------------------------

    if isinstance(has_disability, str):

        has_disability = (
            has_disability.lower().strip() == 'true'
        )

    else:

        has_disability = bool(
            has_disability
        )

    # --------------------------------------------------
    # Validate disability description
    # --------------------------------------------------

    if has_disability:

        if (
            not disability_description
            or not disability_description.strip()
        ):
            return jsonify({
                'error': (
                    'Please provide a description '
                    'of the disability.'
                )
            }), 400

        disability_description = (
            disability_description.strip()
        )

    else:

        disability_description = None

    # --------------------------------------------------
    # Update profile
    # --------------------------------------------------

    staff.full_name = full_name.strip()

    staff.email = email

    staff.contact_number = (
        contact_number.strip()
        if contact_number
        else None
    )

    staff.address = (
        address.strip()
        if address
        else None
    )

    staff.age = age

    staff.has_disability = has_disability

    staff.disability_description = (
        disability_description
    )

    staff.specialization = (
        specialization.strip()
        if specialization
        else None
    )

    # --------------------------------------------------
    # Save changes
    # --------------------------------------------------

    try:

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        print(
            f"STAFF PROFILE UPDATE ERROR: {e}"
        )

        return jsonify({
            'error': 'Failed to update profile.'
        }), 500

    # --------------------------------------------------
    # Return updated profile
    # --------------------------------------------------

    return jsonify({
        'status': 'success',
        'message': 'Profile updated successfully.',
        'profile': staff.to_dict()
    }), 200