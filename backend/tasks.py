import csv
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from extensions import db
from utils.celery_app import celery

from models.user import User
from models.booking import Booking
from models.trek import Trek
@celery.task
def generate_admin_csv_export():
    import csv
    import os
    import smtplib

    from datetime import datetime
    from email.message import EmailMessage

    from models.booking import Booking
    from models.user import User
    from models.trek import Trek

    export_dir = os.path.join(
        os.path.dirname(__file__),
        'exports'
    )

    os.makedirs(export_dir, exist_ok=True)

    filename = (
        f"bookings_export_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    file_path = os.path.join(export_dir, filename)

    bookings = Booking.query.order_by(
        Booking.id.desc()
    ).all()

    # Create CSV
    with open(
        file_path,
        'w',
        newline='',
        encoding='utf-8'
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            'User Name',
            'Trek Name',
            'Trekker Staff',
            'Location',
            'Booking Status',
            'Start Date',
            'End Date'
        ])

        for booking in bookings:

            user = User.query.get(booking.user_id)
            trek = Trek.query.get(booking.trek_id)

            staff_name = (
                trek.staff.full_name
                if trek and trek.staff
                else 'Not Assigned'
            )

            writer.writerow([
                user.full_name if user else 'Unknown User',
                trek.title if trek else 'Unknown Trek',
                staff_name,
                trek.location if trek else 'N/A',
                booking.status,
                trek.start_date if trek else 'N/A',
                trek.end_date if trek else 'N/A'
            ])

    # Find admin email
    admin = User.query.filter_by(
        role='Admin'
    ).first()

    if not admin:
        return {
            'file': file_path,
            'status': 'Completed',
            'email_sent': False
        }

    # SMTP configuration
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_host = os.getenv(
        'SMTP_HOST',
        'smtp.gmail.com'
    )
    smtp_port = int(
        os.getenv('SMTP_PORT', '587')
    )

    if not smtp_email or not smtp_password:
        return {
            'file': file_path,
            'status': 'Completed',
            'email_sent': False
        }

    try:
        # Create email
        message = EmailMessage()

        message['Subject'] = 'Trekking Bookings CSV Export'
        message['From'] = smtp_email
        message['To'] = admin.email

        message.set_content(
            f"""
Hello {admin.full_name},

The trekking bookings CSV report has been generated successfully.

The report is attached to this email.

Thank you,
Trekking Management Application
"""
        )

        # Attach CSV
        with open(file_path, 'rb') as file:
            csv_data = file.read()

        message.add_attachment(
            csv_data,
            maintype='text',
            subtype='csv',
            filename=filename
        )

        # Send email
        with smtplib.SMTP(
            smtp_host,
            smtp_port
        ) as server:

            server.starttls()
            server.login(
                smtp_email,
                smtp_password
            )

            server.send_message(message)

        print(
            f"CSV report sent to {admin.email}"
        )

        return {
            'file': file_path,
            'status': 'Completed',
            'email_sent': True
        }

    except Exception as e:

        print(
            f"CSV email error: {e}"
        )

        return {
            'file': file_path,
            'status': 'Completed',
            'email_sent': False
        }

@celery.task
def send_daily_reminders():
    import os
    import smtplib
    from email.mime.text import MIMEText
    from datetime import datetime, timedelta

    print("🔔 [Celery Beat] Checking upcoming trek bookings...")

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    bookings = Booking.query.filter_by(
        status='Booked'
    ).all()

    sent = 0

    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if not smtp_email or not smtp_password:
        print("⚠️ SMTP settings are missing.")
        return "Reminder skipped: SMTP settings missing."

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)

        for booking in bookings:

            user = User.query.get(booking.user_id)
            trek = Trek.query.get(booking.trek_id)

            if not user or not trek:
                continue

            try:
                start_date = datetime.strptime(
                    str(trek.start_date),
                    '%Y-%m-%d'
                ).date()
            except ValueError:
                continue

            if start_date not in [today, tomorrow]:
                continue

            if start_date == today:
                day_text = "today"
            else:
                day_text = "tomorrow"

            subject = f"Trek Reminder - {trek.title}"

            message = f"""
Hello {user.full_name},

This is a reminder about your upcoming trek.

Trek: {trek.title}
Location: {trek.location}
Start Date: {trek.start_date}
End Date: {trek.end_date}

Your trek starts {day_text}.

Please make sure you are prepared and arrive on time.

Thank you,
Trekking Management Application
"""

            email = MIMEText(message)
            email['Subject'] = subject
            email['From'] = smtp_email
            email['To'] = user.email

            server.sendmail(
                smtp_email,
                user.email,
                email.as_string()
            )

            sent += 1

        server.quit()

        print(f"✅ Daily reminders sent: {sent}")

        return f"Daily reminders sent successfully: {sent}"

    except Exception as e:
        print(f"❌ Reminder error: {e}")
        return f"Reminder failed: {e}"

@celery.task
def generate_ticket_pdf(booking_id, user_name, trek_title, seats, total_price):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tickets_dir = os.path.join(base_dir, 'tickets')

    os.makedirs(tickets_dir, exist_ok=True)

    file_path = os.path.join(
        tickets_dir,
        f"ticket_{booking_id}.pdf"
    )

    c = canvas.Canvas(file_path, pagesize=letter)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 750, "--- Trekking Application Pass ---")

    c.setFont("Helvetica", 12)
    c.drawString(100, 710, f"Booking ID: #{booking_id}")
    c.drawString(100, 690, f"Trekker Name: {user_name}")
    c.drawString(100, 670, f"Trek: {trek_title}")
    c.drawString(100, 650, f"Seats Booked: {seats}")
    c.drawString(100, 630, f"Total Paid: Rs.{total_price}")
    c.drawString(100, 590, "Thank you for booking with us!")

    c.save()

    print(f"TICKET CREATED: {file_path}")

    return file_path





@celery.task
def generate_monthly_report():
    from datetime import datetime
    import os
    import smtplib
    from email.mime.text import MIMEText

    admin = User.query.filter_by(role='Admin').first()

    if not admin:
        return "No admin found."

    completed_treks = Trek.query.filter_by(status='Completed').all()

    total_treks = len(completed_treks)

    participants = set()

    trek_counts = []

    for trek in completed_treks:
        bookings = Booking.query.filter_by(
            trek_id=trek.id,
            status='Booked'
        ).all()

        count = len(bookings)

        for booking in bookings:
            participants.add(booking.user_id)

        trek_counts.append((trek.title, count))

    trek_counts.sort(key=lambda x: x[1], reverse=True)

    popular_treks = trek_counts[:5]

    report = f"""
    <html>
    <body>
        <h2>Monthly Trekking Activity Report</h2>

        <p><b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d')}</p>

        <h3>Summary</h3>
        <p>Treks Conducted: {total_treks}</p>
        <p>Users Participated: {len(participants)}</p>

        <h3>Popular Treks</h3>
        <table border="1" cellpadding="6">
            <tr>
                <th>Trek</th>
                <th>Participants</th>
            </tr>
    """

    for trek_name, count in popular_treks:
        report += f"""
            <tr>
                <td>{trek_name}</td>
                <td>{count}</td>
            </tr>
        """

    report += """
        </table>

        <p>Generated by Trekking Management Application.</p>
    </body>
    </html>
    """

    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))

    if not smtp_email or not smtp_password:
        print("SMTP settings are missing.")
        return "Report created but email was not sent."

    message = MIMEText(report, 'html')
    message['Subject'] = 'Monthly Trekking Activity Report'
    message['From'] = smtp_email
    message['To'] = admin.email

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)

        server.sendmail(
            smtp_email,
            admin.email,
            message.as_string()
        )

        server.quit()

        print(f"Monthly report sent to {admin.email}")
        return "Monthly report sent successfully."

    except Exception as e:
        print(f"Monthly report error: {e}")
        return f"Report failed: {e}"



def generate_user_csv_export(user_id):
    import csv
    import os
    from datetime import datetime

    user = User.query.get(user_id)

    if not user:
        return {
            'file': None,
            'email': None,
            'filename': None,
            'error': 'User not found.'
        }

    export_dir = os.path.join(
        os.path.dirname(__file__),
        'exports'
    )

    os.makedirs(export_dir, exist_ok=True)

    filename = (
        f"user_booking_history_"
        f"{user.id}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    file_path = os.path.join(
        export_dir,
        filename
    )

    bookings = Booking.query.filter_by(
        user_id=user.id
    ).order_by(
        Booking.id.desc()
    ).all()

    with open(
        file_path,
        'w',
        newline='',
        encoding='utf-8'
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            'Booking ID',
            'Trek Name',
            'Location',
            'Seats Booked',
            'Total Price',
            'Booking Status',
            'Payment Status',
            'Booking Date',
            'Start Date',
            'End Date'
        ])

        for booking in bookings:

            trek = Trek.query.get(
                booking.trek_id
            )

            seats = getattr(
                booking,
                'seats_booked',
                1
            )

            total_price = (
                seats * trek.price
                if trek
                else 0
            )

            booking_date = (
                booking.booking_date.strftime(
                    '%Y-%m-%d'
                )
                if getattr(
                    booking,
                    'booking_date',
                    None
                )
                else 'N/A'
            )

            writer.writerow([
                booking.id,
                trek.title if trek else 'Unknown Trek',
                trek.location if trek else 'N/A',
                seats,
                total_price,
                booking.status,
                getattr(
                    booking,
                    'payment_status',
                    'Paid'
                ),
                booking_date,
                trek.start_date if trek else 'N/A',
                trek.end_date if trek else 'N/A'
            ])

    return {
        'file': file_path,
        'email': user.email,
        'filename': filename,
        'error': None
    }


@celery.task
def send_user_csv_email(
    email,
    filename,
    file_path,
    full_name
):
    import os
    import smtplib

    from email.message import EmailMessage

    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_host = os.getenv(
        'SMTP_HOST',
        'smtp.gmail.com'
    )
    smtp_port = int(
        os.getenv('SMTP_PORT', '587')
    )

    if not smtp_email or not smtp_password:
        print('SMTP settings are missing.')
        return False

    if not email:
        print('User email is missing.')
        return False

    try:
        message = EmailMessage()

        message['Subject'] = (
            'Your Trekking Booking History'
        )

        message['From'] = smtp_email
        message['To'] = email

        message.set_content(
            f"""
Hello {full_name},

Your trekking booking history has
been generated successfully.

The CSV file is attached to this email.

Thank you,
Trekking Management Application
"""
        )

        with open(
            file_path,
            'rb'
        ) as file:

            csv_data = file.read()

        message.add_attachment(
            csv_data,
            maintype='text',
            subtype='csv',
            filename=filename
        )

        with smtplib.SMTP(
            smtp_host,
            smtp_port
        ) as server:

            server.starttls()

            server.login(
                smtp_email,
                smtp_password
            )

            server.send_message(
                message
            )

        print(
            f"Booking history sent to {email}"
        )

        return True

    except Exception as e:

        print(
            f"User CSV email error: {e}"
        )

        return False