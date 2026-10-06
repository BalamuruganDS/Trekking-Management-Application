from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(256),
        nullable=False
    )

    # Roles:
    # Admin, Staff, Trekker
    role = db.Column(
        db.String(20),
        nullable=False,
        default='Trekker'
    )

    # Account status:
    # Active, Deactive, Blacklisted
    status = db.Column(
        db.String(20),
        nullable=False,
        default='Active'
    )

    # Basic contact information
    contact_number = db.Column(
        db.String(20),
        nullable=True
    )

    address = db.Column(
        db.String(250),
        nullable=True
    )

    # Personal information
    age = db.Column(
        db.Integer,
        nullable=True
    )

    # Disability information
    has_disability = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    disability_description = db.Column(
        db.String(500),
        nullable=True
    )

    # Staff-specific information
    specialization = db.Column(
        db.String(100),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Relationships
    bookings = db.relationship(
        'Booking',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'status': self.status,

            'contact_number': self.contact_number,
            'address': self.address,

            'age': self.age,

            'has_disability': self.has_disability,
            'disability_description': self.disability_description,

            'specialization': self.specialization,

            'created_at': (
                self.created_at.strftime('%Y-%m-%d %H:%M:%S')
                if self.created_at
                else None
            )
        }





