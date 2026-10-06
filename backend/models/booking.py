from extensions import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), default='Booked')  # 'Booked', 'Cancelled'
    payment_status = db.Column(db.String(20), default='Paid')  # 'Paid', 'Refunded', 'Pending'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def booking_date(self):
        """Property alias for created_at to maintain backward compatibility with routes."""
        return self.created_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trek_id': self.trek_id,
            'seats_booked': self.seats_booked,
            'status': self.status,
            'payment_status': self.payment_status,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }