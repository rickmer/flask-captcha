from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.captcha.helpers import get_challenge
from flask import current_app
import datetime
import random
import time
import unicodedata
import six

db = SQLAlchemy()

# Heavily based on session key generation in Django
# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_RANDOM_KEY = 18446744073709551616     # 2 << 63


import hashlib  # sha for Python 2.5+

def get_safe_now():
    return datetime.datetime.utcnow()


class CaptchaStore(db.Model):
    __tablename__ = 'captcha_store'

    challenge = db.Column(db.String(32))
    response = db.Column(db.String(32))
    hashkey = db.Column(db.String(40), primary_key=True)
    expiration = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        self.response = six.text_type(self.response).lower()
        if not self.expiration:
            timeout = current_app.config['CAPTCHA_TIMEOUT']
            self.expiration = (get_safe_now() +
                               datetime.timedelta(minutes=int(timeout)))
        if not self.hashkey:
            key_ = unicodedata.normalize(
                    'NFKD',
                    str(randrange(0, MAX_RANDOM_KEY)) +
                    str(time.time()) + six.text_type(self.challenge)
                ).encode('ascii', 'ignore') +\
                unicodedata.normalize('NFKD', six.text_type(self.response)).\
                    encode('ascii', 'ignore')
            if hashlib:
                self.hashkey = hashlib.sha1(key_).hexdigest()
            else:
                self.hashkey = sha.new(key_).hexdigest()
            del(key_)
        db.session.add(self)
        db.session.commit()

    @classmethod
    def validate(cls, hashkey, response):
        '''
        Returns true or false if key validates or not
        '''
        find = db.session.query(CaptchaStore).filter(
            CaptchaStore.hashkey==hashkey,
            CaptchaStore.expiration > get_safe_now())

        if find.count() == 0:
            return False

        ret = (find.first().response == response)
        db.session.delete(find.first())
        db.session.commit()
        return ret

    def __unicode__(self):
        return self.challenge

    @classmethod
    def remove_expired(cls):
        items = db.session.query(CaptchaStore).\
            filter(CaptchaStore.expiration <= get_safe_now())

        for i in items:
            db.session.delete(i)
        db.session.commit()

    @classmethod
    def generate_key(cls):
        challenge, response = get_challenge()()
        c = CaptchaStore()
        c.challenge = challenge
        c.response = response
        c.save()

        return c.hashkey
