import os
from flask import Blueprint, request, jsonify, send_from_directory, send_file
from extensions import db
from models.user import User
from models.booking import Booking
from models.trek import Trek
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from utils.cache import clear_trek_cache
from utils.celery_app import celery
from utils.cache import (
    get_cached_treks,
    cache_treks
)   


user_bp = Blueprint('user', __name__, url_prefix='/api/user')





# ==============================================================================
# 1. AUTHENTICATION & REGISTRATION
# ==============================================================================

@user_bp.route('/register', methods=['POST'])
def register_trekker():
    """Public registration endpoint for new Trekkers."""
    data = request.get_json() or {}

    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    contact_number = data.get('contact_number')

    if not full_name or not email or not password:
        return jsonify({'error': 'Full name, email, and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email is already registered'}), 400

    new_user = User(
        full_name=full_name,
        email=email,
        role='Trekker',
        status='Active',
        contact_number=contact_number
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'Registration successful! You can now log in.',
        'user': new_user.to_dict()
    }), 201


@user_bp.route('/login', methods=['POST'])
def login():
    """Unified login endpoint for Admin, Trek Staff, and Trekkers."""
    data = request.get_json() or {}

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if user.status == 'Blacklisted':
        return jsonify({'error': 'Your account has been blacklisted. Please contact Admin.'}), 403
    elif user.status == 'Deactive':
        return jsonify({'error': 'Your account is deactivated.'}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'email': user.email}
    )

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


# ==============================================================================
# 2. TREK EXPLORATION
# ==============================================================================

@user_bp.route('/treks', methods=['GET'])
def list_treks():

    search_query = request.args.get('search', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    duration = request.args.get('duration', '').strip()

    # Create a unique cache key based on filters
    cache_key = (
        f"treks:"
        f"{search_query.lower()}:"
        f"{difficulty.lower()}:"
        f"{duration.lower()}"
    )

    # --------------------------------------------------
    # CHECK REDIS CACHE FIRST
    # --------------------------------------------------

    cached_treks = get_cached_treks(cache_key)

    if cached_treks is not None:
        print("✅ Trek data served from Redis cache")

        return jsonify({
            'status': 'success',
            'source': 'cache',
            'treks': cached_treks
        }), 200

    # --------------------------------------------------
    # CACHE MISS → GET DATA FROM DATABASE
    # --------------------------------------------------

    print("📦 Trek cache miss - fetching from database")

    query = Trek.query.filter(
        Trek.status.in_(['Approved', 'Open'])
    )

    if search_query:
        query = query.filter(
            (Trek.title.ilike(f'%{search_query}%')) |
            (Trek.location.ilike(f'%{search_query}%'))
        )

    if difficulty:
        query = query.filter(
            Trek.difficulty == difficulty
        )

    treks = query.all()

    # --------------------------------------------------
    # DURATION FILTER
    # --------------------------------------------------

    if duration:

        filtered = []

        for trek in treks:

            if not trek.start_date or not trek.end_date:
                continue

            try:

                start_date = datetime.strptime(
                    str(trek.start_date),
                    '%Y-%m-%d'
                ).date()

                end_date = datetime.strptime(
                    str(trek.end_date),
                    '%Y-%m-%d'
                ).date()

                days = (end_date - start_date).days + 1

            except (ValueError, TypeError):

                continue

            if duration == '1-3' and 1 <= days <= 3:
                filtered.append(trek)

            elif duration == '4-7' and 4 <= days <= 7:
                filtered.append(trek)

            elif duration == '8+' and days >= 8:
                filtered.append(trek)

        treks = filtered

    # --------------------------------------------------
    # CONVERT TO DICTIONARY
    # --------------------------------------------------

    trek_data = [
        trek.to_dict()
        for trek in treks
    ]

    # --------------------------------------------------
    # STORE IN REDIS FOR 5 MINUTES
    # --------------------------------------------------

    cache_treks(
        cache_key,
        trek_data
    )

    return jsonify({
        'status': 'success',
        'source': 'database',
        'treks': trek_data
    }), 200


@user_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """Allows an active Trekker to book a trek."""

    from tasks import generate_ticket_pdf

    current_user_id = get_jwt_identity()
    data = request.get_json() or {}

    trek_id = data.get('trek_id')
    seats_requested = int(data.get('seats_booked', 1))

    if not trek_id:
        return jsonify({
            'error': 'Trek ID is required'
        }), 400

    if seats_requested <= 0:
        return jsonify({
            'error': 'Number of seats must be at least 1'
        }), 400

    user = User.query.get(current_user_id)

    if not user:
        return jsonify({
            'error': 'User not found'
        }), 404

    if user.status != 'Active':
        return jsonify({
            'error': f'Booking restricted. Account is {user.status}'
        }), 403

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({
            'error': 'Trek not found'
        }), 404

    if trek.status != 'Open':
        return jsonify({
            'error': 'This trek is not open for booking.'
        }), 400
    
    if trek.available_seats < seats_requested:
        return jsonify({
            'error': 'Not enough seats available for this trek'
        }), 400

    existing_booking = Booking.query.filter_by(
        user_id=current_user_id,
        trek_id=trek_id,
        status='Booked'
    ).first()

    if existing_booking:
        return jsonify({
            'error': 'You have already booked this trek'
        }), 400

    # Create booking
    new_booking = Booking(
        user_id=current_user_id,
        trek_id=trek_id,
        seats_booked=seats_requested,
        status='Booked',
        payment_status='Paid'
    )

    # Reduce available seats
    trek.available_seats -= seats_requested

    db.session.add(new_booking)
    db.session.commit()
    clear_trek_cache()
    # Generate ticket.
    # If ticket generation fails, DON'T mark the booking as failed.
    try:
        total_cost = seats_requested * trek.price

        generate_ticket_pdf.apply(
            args=[
                new_booking.id,
                user.full_name,
                trek.title,
                seats_requested,
                total_cost
            ]
        )

        print(
            f"Ticket generated for booking #{new_booking.id}"
        )

    except Exception as ticket_error:
        print(
            f"WARNING: Booking #{new_booking.id} was created, "
            f"but ticket generation failed: {ticket_error}"
        )

    # Booking was already successfully committed.
    return jsonify({
        'message': 'Trek booked successfully!',
        'booking': new_booking.to_dict()
    }), 201



@user_bp.route('/my-bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    """Fetch all detailed bookings for the currently authenticated user."""
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.id.desc()).all()
    
    results = []
    for b in bookings:
        trek = Trek.query.get(b.trek_id)
        seats = getattr(b, 'seats_booked', 1)
        results.append({
            "id": b.id,
            "trek_id": b.trek_id,
            "trek_title": trek.title if trek else "Unknown Trek",
            "trek_location": trek.location if trek else "N/A",
            "seats_booked": seats,
            "total_price": seats * (trek.price if trek else 0),
            "status": b.status,
            "payment_status": getattr(b, 'payment_status', 'Paid'),
            "created_at": b.booking_date.strftime('%Y-%m-%d') if hasattr(b, 'booking_date') and b.booking_date else None
        })

    return jsonify({'status': 'success', 'history': results}), 200


@user_bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def cancel_booking(booking_id):
    """Allows a trekker to cancel an active booking and release seats."""
    user_id = get_jwt_identity()
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()

    if not booking:
        return jsonify({'error': 'Booking not found or unauthorized'}), 404

    if booking.status == 'Cancelled':
        return jsonify({'error': 'Booking is already cancelled'}), 400

    # Restore trek seats
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_seats += getattr(booking, 'seats_booked', 1)

    booking.status = 'Cancelled'
    db.session.commit()
    clear_trek_cache()
    return jsonify({'message': f'Booking {trek.title} cancelled successfully.'}), 200




@user_bp.route('/download-ticket/<int:booking_id>', methods=['GET'])
@jwt_required()
def download_ticket(booking_id):
    try:
        from flask import send_file
        import os

        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        tickets_dir = os.path.join(base_dir, 'tickets')
        filename = f"ticket_{booking_id}.pdf"
        file_path = os.path.join(tickets_dir, filename)

        if not os.path.exists(file_path):
            return jsonify({
                'error': 'Ticket PDF is currently generating or unavailable. Please try again in a moment.'
            }), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({
            'error': f'Failed to download ticket: {str(e)}'
        }), 500



# ==============================================================================
# USER PROFILE
# ==============================================================================

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get the currently logged-in user's profile."""

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            'error': 'User not found'
        }), 404

    return jsonify({
        'status': 'success',
        'profile': user.to_dict()
    }), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update the currently logged-in user's profile."""

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            'error': 'User not found'
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
    has_disability = data.get('has_disability', False)
    disability_description = data.get(
        'disability_description'
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

    # Check if another account already uses this email
    existing_user = User.query.filter(
        User.email == email,
        User.id != user.id
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
    # Handle disability value correctly
    # --------------------------------------------------

    if isinstance(has_disability, str):
        has_disability = (
            has_disability.lower().strip() == 'true'
        )
    else:
        has_disability = bool(has_disability)

    # --------------------------------------------------
    # Disability description
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
        # If the person does not have a disability,
        # don't keep an old description.
        disability_description = None

    # --------------------------------------------------
    # Update profile
    # --------------------------------------------------

    user.full_name = full_name.strip()

    user.email = email

    user.contact_number = (
        contact_number.strip()
        if contact_number
        else None
    )

    user.address = (
        address.strip()
        if address
        else None
    )

    user.age = age

    user.has_disability = has_disability

    user.disability_description = (
        disability_description
    )

    # --------------------------------------------------
    # Save changes
    # --------------------------------------------------

    try:
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()

        print(
            f"PROFILE UPDATE ERROR: {e}"
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
        'profile': user.to_dict()
    }), 200



@user_bp.route('/export-bookings', methods=['GET'])
@jwt_required()
def export_user_bookings():

    try:
        from tasks import (
            generate_user_csv_export,
            send_user_csv_email
        )

        user_id = get_jwt_identity()

        # Generate CSV immediately
        data = generate_user_csv_export(
            user_id
        )

        file_path = data.get('file')

        if not file_path:
            return jsonify({
                'error': data.get(
                    'error',
                    'Failed to generate CSV.'
                )
            }), 500

        if not os.path.exists(file_path):
            return jsonify({
                'error': 'CSV file was not found.'
            }), 500

        # Send email in background
        if data.get('email'):

            user = User.query.get(user_id)

            send_user_csv_email.delay(
                data['email'],
                data['filename'],
                file_path,
                user.full_name
            )

        # Download immediately
        return send_file(
            file_path,
            as_attachment=True,
            download_name=data['filename'],
            mimetype='text/csv'
        )

    except Exception as e:

        print(
            'USER CSV EXPORT ERROR:',
            e
        )

        return jsonify({
            'error': (
                f'Failed to export booking history: {str(e)}'
            )
        }), 500