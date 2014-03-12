import re
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.captcha.models import db, CaptchaStore

VERSION = (0, 1, 1)

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


def get_version(svn=False):
    "Returns the version as a human-format string."
    return '.'.join([str(i) for i in VERSION])


def pillow_required():
    def pil_version(version):
        try:
            return int(re.compile('[^\d]').sub('', version))
        except:
            return 116

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        try:
            import Image
            import ImageDraw
            import ImageFont
        except ImportError:
            return True

    return pil_version(Image.VERSION) < 116
