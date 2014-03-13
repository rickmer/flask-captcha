import re
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.captcha.models import db, CaptchaStore

VERSION = (0, 1, 6)

class Captcha(object):
    ext_db = None

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        with app.app_context():
            self.ext_db = current_app.extensions['sqlalchemy'].db
            active_metadata = self.ext_db.metadata
            CaptchaStore.__table__ = CaptchaStore.__table__.tometadata(active_metadata)

