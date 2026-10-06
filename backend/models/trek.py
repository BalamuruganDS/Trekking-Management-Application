from extensions import db
from datetime import datetime


class Trek(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=False)
    

    difficulty = db.Column(
        db.String(50),
        nullable=False,
        default='Moderate'
    )
    price = db.Column(db.Float, nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False, default=20)
    available_seats = db.Column(
        db.Integer,
        nullable=False,
        default=20
    )
    status = db.Column(
        db.String(20),
        nullable=False,
        default='Pending'
    )

    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)

    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    bookings = db.relationship(
        'Booking',
        backref='trek',
        lazy=True,
        cascade='all, delete-orphan'
    )

    staff = db.relationship(
        'User',
        foreign_keys=[assigned_staff_id]
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'difficulty': self.difficulty,
            'price': self.price,
            'max_capacity': self.max_capacity,
            'available_seats': self.available_seats,
            'status': self.status,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'duration': (
                    (datetime.strptime(str(self.end_date), '%Y-%m-%d').date()
                    - datetime.strptime(str(self.start_date), '%Y-%m-%d').date()).days + 1
                    if self.start_date and self.end_date
                    else None
                    ),
            'assigned_staff_id': self.assigned_staff_id,
            'created_at': (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }


    