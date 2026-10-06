# from celery import Celery, Task
# from celery.schedules import crontab

# celery = Celery(
#     __name__,
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/0",
#     include=['tasks']
# )

# celery.conf.timezone = 'Asia/Kolkata'
# celery.conf.enable_utc = False

# celery.conf.beat_schedule = {
#     'daily-reminders': {
#         'task': 'tasks.send_daily_reminders',
#         'schedule': crontab(
#             hour=8,
#             minute=0
#         ),
#     },

#     'monthly-report': {
#         'task': 'tasks.generate_monthly_report',
#         'schedule': crontab(
#             day_of_month=1,
#             hour=8,
#             minute=0
#         ),
#     }
# }


# class FlaskTask(Task):
#     def __call__(self, *args, **kwargs):
#         from app import create_app

#         app = create_app()

#         with app.app_context():
#             return self.run(*args, **kwargs)


# celery.Task = FlaskTask


# def celery_init_app(app):
#     celery.conf.update(
#         broker_url=app.config.get(
#             "CELERY_BROKER_URL",
#             "redis://localhost:6379/0"
#         ),
#         result_backend=app.config.get(
#             "CELERY_RESULT_BACKEND",
#             "redis://localhost:6379/0"
#         )
#     )

#     app.extensions["celery"] = celery

#     return celery
import os

from dotenv import load_dotenv
from celery import Celery, Task
from celery.schedules import crontab


# Load .env from the backend folder
load_dotenv(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        '.env'
    )
)


celery = Celery(
    __name__,
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=['tasks']
)


# Timezone
celery.conf.timezone = 'Asia/Kolkata'
celery.conf.enable_utc = False


# Scheduled tasks
celery.conf.beat_schedule = {

    # Daily reminder at 8:00 AM
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(
            hour=8,
            minute=0
        ),
    },

    # Monthly report on the 1st at 8:00 AM
    'monthly-report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(
            day_of_month=1,
            hour=8,
            minute=0
        ),
    }
}


# Give Celery access to Flask application context
class FlaskTask(Task):

    def __call__(self, *args, **kwargs):

        from app import create_app

        app = create_app()

        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = FlaskTask


def celery_init_app(app):

    celery.conf.update(
        broker_url=app.config.get(
            "CELERY_BROKER_URL",
            "redis://localhost:6379/0"
        ),

        result_backend=app.config.get(
            "CELERY_RESULT_BACKEND",
            "redis://localhost:6379/0"
        )
    )

    app.extensions["celery"] = celery

    return celery