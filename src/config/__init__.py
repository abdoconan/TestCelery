from flask import Flask
from celery import Celery
from dotenv import load_dotenv
import os
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery.contrib.abortable import AbortableTask


celery: Optional[Celery] = None 
db: Optional[SQLAlchemy] = None
migrate: Optional[Migrate] = None

def make_celery(app: Flask) -> Celery:
    celery: Celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    # Tie Flask application context to Celery tasks
    # class ContextTask(celery.Task):
    class ContextTask(AbortableTask):
        def __call__(self, *args: tuple, **kwargs: dict) -> any:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.conf.update(app.config)
    return celery

def init_models(app: Flask):
    global db
    db= SQLAlchemy(app)
    global migrate
    migrate = Migrate(app, db)
    from ..models.testModel import TestModel
    # Import Celery's database-related classes
    from celery.backends.database.models import Task

def init_apis(app:Flask):
    from ..apis.task_api import task_bp
    app.register_blueprint(task_bp)


def init_app() -> Flask:
    load_dotenv()
    app: Flask = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = os.getenv("CELERY_BROKER_URL")
    app.config['CELERY_RESULT_BACKEND'] = os.getenv("CELERY_RESULT_BACKEND")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRES_URL")

    
    
    init_models(app)
    
    global celery 
    celery = make_celery(app)
    setattr(app, "celery", celery)

    init_apis(app)
   

    return app


