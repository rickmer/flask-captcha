from flask.ext.captcha.models import CaptchaStore, CaptchaSequence, CaptchaSequenceCache, get_safe_now
from flask.ext.captcha.helpers import noise_functions, filter_functions
from flask import Blueprint, request, make_response, render_template, url_for
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy
import random
import re
import tempfile
import os
import subprocess

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import Image
    import ImageDraw
    import ImageFont

import json



db = SQLAlchemy()

NON_DIGITS_RX = re.compile('[^\d]')
# Distance of the drawn text from the top of the captcha image
from_top = 4


captcha_blueprint = Blueprint('captcha', __name__)

def getsize(font, text):
    if hasattr(font, 'getoffset'):
        return [x + y for x, y in zip(font.getsize(text), font.getoffset(text))]
    else:
        return font.getsize(text)

@captcha_blueprint.route('/captcha_image/<key>')
def captcha_image(key):

    if not current_app.config['CAPTCHA_PREGEN']:
        store = db.session.query(CaptchaStore).filter(CaptchaStore.hashkey==key)
        if store.count() == 0:
            return make_response("", 404)
        store = store.first()
        text = store.challenge

        image = make_image(text)

        out = StringIO()
        image.save(out, "PNG")
        out.seek(0)
    else:
        image_path = current_app.config['CAPTCHA_PREGEN_PATH']
        path = str(os.path.join(image_path, '%s.png' % key))
        print(path)
        if os.path.isfile(path):
            out = open(path, 'rb')
            out.seek(0)

    response = make_response(out.read())
    response.content_type = 'image/png'
    return response

def make_image(text):
    font_path = current_app.config['CAPTCHA_FONT_PATH']
    font_size = current_app.config['CAPTCHA_FONT_SIZE']
    punctuation = current_app.config['CAPTCHA_PUNCTUATION']
    foreground_color = current_app.config['CAPTCHA_FOREGROUND_COLOR']
    letter_rotation =  current_app.config['CAPTCHA_LETTER_ROTATION']

    if font_path.lower().strip().endswith('ttf'):
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load(font_path)

    size = getsize(font, text)
    size = (size[0] * 2, int(size[1] * 1.4))
    image = Image.new('RGB', size,
                      current_app.config['CAPTCHA_BACKGROUND_COLOR'])

    try:
        PIL_VERSION = int(NON_DIGITS_RX.sub('', current_app.config['VERSION']))
    except:
        PIL_VERSION = 116
    xpos = 2

    charlist = []
    for char in text:
        if char in punctuation and len(charlist) >= 1:
            charlist[-1] += char
        else:
            charlist.append(char)

    for char in charlist:
        fgimage = Image.new('RGB', size, foreground_color)
        charimage = Image.new('L', getsize(font, ' %s ' % char), '#000000')
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), ' %s ' % char, font=font, fill='#ffffff')
        if letter_rotation:
            if PIL_VERSION >= 116:
                charimage = charimage.rotate(random.randrange(*letter_rotation), expand=0, resample=Image.BICUBIC)
            else:
                charimage = charimage.rotate(random.randrange(*letter_rotation), resample=Image.BICUBIC)
        charimage = charimage.crop(charimage.getbbox())
        maskimage = Image.new('L', size)

        maskimage.paste(charimage, (xpos, from_top, xpos + charimage.size[0], from_top + charimage.size[1]))
        size = maskimage.size
        image = Image.composite(fgimage, image, maskimage)
        xpos = xpos + 2 + charimage.size[0]

    image = image.crop((0, 0, xpos + 1, size[1]))
    draw = ImageDraw.Draw(image)

    for f in noise_functions():
        draw = f(draw, image)
    for f in filter_functions():
        image = f(image)

    return image

@captcha_blueprint.route('/captcha_audio/<key>')
def captcha_audio(key):
    flite_path = current_app.config['CAPTCHA_FLITE_PATH']
    challenge_funct = current_app.config['CAPTCHA_CHALLENGE_FUNCT']
    if flite_path:
        store = db.session.query(CaptchaStore).filter(CaptchaStore.hashkey==key)
        if store.count() == 0:
            return make_response("", 404)
        store = store.first()
        text = store.challenge
        if 'captcha.helpers.math_challenge' == challenge_funct:
            text = text.replace('*', 'times').replace('-', 'minus')
        else:
            text = ', '.join(list(text))
        path = str(os.path.join(tempfile.gettempdir(), '%s.wav' % key))
        subprocess.call([flite_path, "-t", text, "-o", path])
        if os.path.isfile(path):
            f = open(path, 'rb')
            response = make_response(f.read())
            response.content_type = 'audio/x-wav'
            f.close()
            os.unlink(path)
            return response
    return make_response("", 404)

@captcha_blueprint.route('/captcha_refresh/')
def captcha_refresh():
    '''
    Return json with new captcha for ajax refresh request
    '''

    if not current_app.config['CAPTCHA_PREGEN']:
        new_key = CaptchaStore.generate_key()
    else:
        next_index = CaptchaSequenceCache.get().next()
        print(next_index)
        store = db.session.query(CaptchaStore).filter(CaptchaStore.index==next_index)
        if store.count() == 0:
            return make_response("", 404)
        else:
            value = store.first()
            value.set_expiration()
            db.session.commit()
            print("preload: using key %s " % value.hashkey)
            new_key = value.hashkey

    to_json_response = {
        'key': new_key,
        'image_url': url_for(".captcha_image", key=new_key),
    }

    resp = make_response(json.dumps(to_json_response))
    resp.content_type = 'application/json'
    return resp

@captcha_blueprint.route('/captcha_validate/<hashkey>/<response>')
def captcha_validate(hashkey, response):
    response = response.strip().lower()
    if not current_app.config['CAPTCHA_PREGEN']:
        CaptchaStore.remove_expired()
    if not CaptchaStore.validate(hashkey, response):
        return make_response("", 400)

    return make_response("", 200)