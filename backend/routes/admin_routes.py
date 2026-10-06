import os
from flask import Blueprint, request, jsonify, send_file
from extensions import db
from models.user import User
from models.booking import Booking
from models.trek import Trek
from utils.decorators import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.cache import clear_trek_cache



admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
@role_required('Admin')
def get_dashboard_stats():
    total_users = User.query.filter_by(role='Trekker').count()
    total_staff = User.query.filter_by(role='Staff').count()
    total_bookings = Booking.query.count()
    
    completed_bookings = Booking.query.filter_by(status='Booked').all()
    total_revenue = 0
    for b in completed_bookings:
        trek = Trek.query.get(b.trek_id)
        if trek:
            total_revenue += (getattr(b, 'seats_booked', 1) * trek.price)

    return jsonify({
        'status': 'success',
        'stats': {
            'total_users': total_users,
            'total_staff': total_staff,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue
        }
    }), 200


@admin_bp.route('/staff', methods=['POST'])
@role_required('Admin')
def create_staff():
    try:
        data = request.get_json() or {}

        email = data.get('email', '').strip()
        full_name = data.get('full_name', '').strip()
        password = data.get('password', '').strip()
        contact_number = data.get('contact_number', '').strip()
        specialization = data.get('specialization', '').strip()

        if not email or not full_name or not password:
            return jsonify({'error': 'Full name, email, and password are required.'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': f'A user with email "{email}" already exists.'}), 400

        staff_user = User(
            full_name=full_name,
            email=email,
            role='Staff',
            status='Active'
        )
        
        # Set optional attributes if supported by model
        if hasattr(staff_user, 'contact_number'):
            staff_user.contact_number = contact_number
        if hasattr(staff_user, 'specialization'):
            staff_user.specialization = specialization

        staff_user.set_password(password)

        db.session.add(staff_user)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'Trek Staff account for {full_name} created successfully!',
            'staff': staff_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database or server error: {str(e)}'}), 500


@admin_bp.route('/staff', methods=['GET'])
@role_required('Admin')
def list_staff():
    search_query = request.args.get('search', '').strip()
    query = User.query.filter_by(role='Staff')
    
    if search_query:
        query = query.filter(
            (User.full_name.ilike(f'%{search_query}%')) | 
            (User.email.ilike(f'%{search_query}%'))
        )

    staff_members = query.all()
    return jsonify({
        'status': 'success',
        'staff': [s.to_dict() for s in staff_members]
    }), 200


@admin_bp.route('/users', methods=['GET'])
@role_required('Admin')
def list_users():
    search_query = request.args.get('search', '').strip()

    query = User.query.filter_by(role='Trekker')

    if search_query:
        query = query.filter(
            (User.full_name.ilike(f'%{search_query}%')) |
            (User.email.ilike(f'%{search_query}%'))
        )

    users = query.all()

    result = []

    for user in users:
        bookings = Booking.query.filter_by(
            user_id=user.id
        ).all()

        trek_names = []

        for booking in bookings:
            trek = Trek.query.get(booking.trek_id)

            if trek and trek.title not in trek_names:
                trek_names.append(trek.title)

        data = user.to_dict()
        data['registered_treks'] = trek_names

        result.append(data)

    return jsonify({
        'status': 'success',
        'users': result
    }), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PATCH'])
@role_required('Admin')
def update_user_status(user_id):
    try:
        data = request.get_json() or {}
        new_status = data.get('status')

        if new_status not in ['Active', 'Deactive', 'Blacklisted']:
            return jsonify({'error': 'Invalid status option.'}), 400

        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User or staff member not found.'}), 404

        target_user.status = new_status
        db.session.commit()
        clear_trek_cache()
        return jsonify({
            'status': 'success',
            'message': f'Account status for {target_user.full_name} updated to {new_status}.',
            'user': target_user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update status: {str(e)}'}), 500


@admin_bp.route('/treks', methods=['GET'])
@role_required('Admin')
def list_treks():
    search_query = request.args.get('search', '').strip()
    query = Trek.query

    if search_query:
        query = query.filter(
            (Trek.title.ilike(f'%{search_query}%')) |
            (Trek.location.ilike(f'%{search_query}%'))
        )

    treks = query.all()
    return jsonify({
        'status': 'success',
        'treks': [t.to_dict() for t in treks]
    }), 200


@admin_bp.route('/treks', methods=['POST'])
@role_required('Admin')
def create_trek():
    try:
        data = request.get_json() or {}

        title = data.get('title')
        location = data.get('location')
        price = data.get('price')

        if not title or not location or not price:
            return jsonify({'error': 'Title, location, and price are required.'}), 400

        new_trek = Trek(
            title=title,
            description=data.get('description', ''),
            location=location,
            difficulty=data.get('difficulty', 'Moderate'),
            price=float(price),
            max_capacity=int(data.get('max_capacity', 20)),
            available_seats=int(data.get('available_seats', data.get('max_capacity', 20))),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )

        db.session.add(new_trek)
        db.session.commit()
        clear_trek_cache()

        return jsonify({
            'status': 'success',
            'message': 'Trek created successfully!',
            'trek': new_trek.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create trek: {str(e)}'}), 500


# ================= TREK APPROVAL =================

@admin_bp.route('/treks/pending', methods=['GET'])
@role_required('Admin')
def pending_treks():
    treks = Trek.query.filter_by(
        status='Pending'
    ).order_by(Trek.id.desc()).all()

    return jsonify({
        'status': 'success',
        'treks': [trek.to_dict() for trek in treks]
    }), 200


@admin_bp.route('/treks/<int:trek_id>/status', methods=['PATCH'])
@role_required('Admin')
def update_trek_status(trek_id):
    try:
        trek = Trek.query.get(trek_id)

        if not trek:
            return jsonify({
                'error': 'Trek not found.'
            }), 404

        data = request.get_json() or {}
        new_status = data.get('status')

        allowed_statuses = [
            'Pending',
            'Approved',
            'Open',
            'Closed',
            'Completed',
            'Blocked'
        ]

        if new_status not in allowed_statuses:
            return jsonify({
                'error': 'Invalid trek status.'
            }), 400

        trek.status = new_status
        db.session.commit()
        clear_trek_cache()
        return jsonify({
            'status': 'success',
            'message': f'Trek status changed to {new_status}.',
            'trek': trek.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            'error': f'Failed to update trek status: {str(e)}'
        }), 500




@admin_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@role_required('Admin')
def update_trek(trek_id):
    try:
        trek = Trek.query.get(trek_id)
        if not trek:
            return jsonify({'error': 'Trek not found.'}), 404

        data = request.get_json() or {}

        trek.title = data.get('title', trek.title)
        trek.location = data.get('location', trek.location)
        trek.description = data.get('description', trek.description)
        trek.difficulty = data.get('difficulty', trek.difficulty)
        
        if 'price' in data:
            trek.price = float(data['price'])
        if 'max_capacity' in data:
            trek.max_capacity = int(data['max_capacity'])
        if 'available_seats' in data:
            trek.available_seats = int(data['available_seats'])
        if 'start_date' in data:
            trek.start_date = data['start_date']
        if 'end_date' in data:
            trek.end_date = data['end_date']

        db.session.commit()
        clear_trek_cache()

        return jsonify({
            'status': 'success',
            'message': 'Trek details updated successfully!',
            'trek': trek.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update trek: {str(e)}'}), 500


@admin_bp.route('/treks/<int:trek_id>/assign-staff', methods=['PATCH'])
@role_required('Admin')
def assign_staff(trek_id):
    try:
        data = request.get_json() or {}
        staff_id = data.get('assigned_staff_id')

        trek = Trek.query.get(trek_id)
        if not trek:
            return jsonify({'error': 'Trek not found.'}), 404

        if staff_id:
            staff_user = User.query.filter_by(id=staff_id, role='Staff').first()
            if not staff_user:
                return jsonify({'error': 'Staff user not found.'}), 404
            trek.assigned_staff_id = staff_id
        else:
            trek.assigned_staff_id = None

        db.session.commit()
        clear_trek_cache()
        return jsonify({
            'status': 'success',
            'message': 'Staff assigned successfully!', 
            'trek': trek.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to assign staff: {str(e)}'}), 500


@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@role_required('Admin')
def delete_trek(trek_id):
    try:
        trek = Trek.query.get(trek_id)
        if not trek:
            return jsonify({'error': 'Trek not found.'}), 404

        db.session.delete(trek)
        db.session.commit()
        clear_trek_cache()

        return jsonify({
            'status': 'success',
            'message': f'Trek #{trek_id} deleted successfully.'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete trek: {str(e)}'}), 500


@admin_bp.route('/bookings', methods=['GET'])
@role_required('Admin')
def list_bookings():
    bookings = Booking.query.order_by(
        Booking.id.desc()
    ).all()

    result = []

    for booking in bookings:
        user = User.query.get(booking.user_id)
        trek = Trek.query.get(booking.trek_id)

        result.append({
            'id': booking.id,
            'user_id': booking.user_id,
            'user_name': user.full_name if user else 'Unknown',
            'trek_id': booking.trek_id,
            'trek_title': trek.title if trek else 'Unknown Trek',
            'location': trek.location if trek else 'N/A',
            'seats': getattr(booking, 'seats_booked', 1),
            'status': booking.status,
            'payment_status': getattr(
                booking,
                'payment_status',
                'Paid'
            ),
            'booking_date': (
                booking.booking_date.strftime('%Y-%m-%d')
                if getattr(booking, 'booking_date', None)
                else 'N/A'
            ),
            'start_date': (
                trek.start_date
                if trek and trek.start_date
                else 'N/A'
            ),
            'end_date': (
                trek.end_date
                if trek and trek.end_date
                else 'N/A'
            )
        })

    return jsonify({
        'status': 'success',
        'bookings': result
    }), 200





@admin_bp.route('/export-csv', methods=['POST'])
@role_required('Admin')
def trigger_export():
    try:
        from tasks import generate_admin_csv_export

        result = generate_admin_csv_export.apply()
        data = result.get()

        if not isinstance(data, dict):
            return jsonify({
                'error': 'Invalid export result.'
            }), 500

        file_path = data.get('file')
        email_sent = data.get(
            'email_sent',
            False
        )

        if not file_path:
            return jsonify({
                'error': 'CSV file path was not returned.'
            }), 500

        if not os.path.exists(file_path):
            return jsonify({
                'error': 'CSV file was not found.'
            }), 500

        response = send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(
                file_path
            ),
            mimetype='text/csv'
        )

        response.headers['X-Email-Sent'] = (
            'true' if email_sent else 'false'
        )

        return response

    except Exception as e:

        print(
            "CSV DOWNLOAD ERROR:",
            e
        )

        return jsonify({
            'error': (
                f'Failed to export CSV: {str(e)}'
            )
        }), 500


@admin_bp.route('/setup-admin', methods=['GET'])
def setup_admin():
    # Check if an admin already exists
    admin_exists = User.query.filter_by(role='Admin').first()
    if admin_exists:
        return jsonify({'message': 'Admin already exists!', 'email': admin_exists.email}), 200

    # Create the first admin
    admin_user = User(
        full_name='System Admin',
        email='admin@trekapp.com',
        role='Admin',
        status='Active'
    )
    admin_user.set_password('admin123') # The password you will use to log in
    
    db.session.add(admin_user)
    db.session.commit()
    
    return jsonify({'message': 'Admin created successfully! Use admin@trekapp.com / admin123 to login.'}), 201



# ==============================================================================
# VIEW USER / STAFF PROFILE
# ==============================================================================

@admin_bp.route('/users/<int:user_id>/profile', methods=['GET'])
@role_required('Admin')
def view_user_profile(user_id):
    """Admin views a Trekker's complete profile."""

    user = User.query.filter_by(
        id=user_id,
        role='Trekker'
    ).first()

    if not user:
        return jsonify({
            'error': 'Trekker not found.'
        }), 404

    return jsonify({
        'status': 'success',
        'profile': user.to_dict()
    }), 200


@admin_bp.route('/staff/<int:staff_id>/profile', methods=['GET'])
@role_required('Admin')
def view_staff_profile(staff_id):
    """Admin views a Staff member's complete profile."""

    staff = User.query.filter_by(
        id=staff_id,
        role='Staff'
    ).first()

    if not staff:
        return jsonify({
            'error': 'Staff member not found.'
        }), 404

    return jsonify({
        'status': 'success',
        'profile': staff.to_dict()
    }), 200