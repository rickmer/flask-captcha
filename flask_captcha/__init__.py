import re
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.captcha.models import db, CaptchaStore, CaptchaSequence

VERSION = (0, 1, 7)

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
            CaptchaSequence.__table__ = CaptchaSequence.__table__.tometadata(active_metadata)

