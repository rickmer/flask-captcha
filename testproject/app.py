#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
import argparse
from flask.ext.captcha import Captcha
from flask.ext.captcha.views import captcha_blueprint

from flask.ext.captcha.models import CaptchaStore, CaptchaSequenceCache
from flask import Blueprint, request, make_response, render_template, url_for

ROOT_PATH = os.path.split(os.path.abspath(__file__))[0]

app_flask = Flask(__name__)
app_captcha = Captcha()

app_flask.register_blueprint(captcha_blueprint, url_prefix='/captcha')

@app_flask.route("/")
def hello():
    return render_template('home.html')

@app_flask.route("/index")
def captcha_inc():
    val = CaptchaSequenceCache.get().current()

    response = make_response(str(val))
    response.content_type = 'text/plain'
    return response

def main():
    # load settings
    app_flask.config.from_object("flask.ext.captcha.settings")
    app_flask.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///%s/db.sqlite' % ROOT_PATH
    db = SQLAlchemy(app_flask)
    app_captcha.init_app(app_flask)

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--createdb", help="create the database", action="store_true")
    parser.add_argument("-l", "--list", help="list captchas", action="store_true")
    parser.add_argument("-d", "--clear", help="clear captchas", action="store_true")
    parser.add_argument("-g", "--gen", help="gen captchas", action="store_true")
    pargs = parser.parse_args()

    with app_flask.app_context():
        if pargs.createdb:
            print("Creating db..")
            db.create_all()
            exit(0)
        elif pargs.list:
            values = CaptchaStore.get_all()
            print(values)
            exit(0)
        elif pargs.clear:
            from flask.ext.captcha.helpers import clear_images
            deleted = CaptchaStore.delete_all()
            clear_images()
            print("cleared %s db records" % deleted)
            exit(0)
        elif pargs.gen:
            from flask.ext.captcha.helpers import init_captcha_dir, generate_images
            init_captcha_dir()
            count = generate_images(app_flask.config['CAPTCHA_PREGEN_MAX'])
            print("created %s captchas" % count)
            exit(0)

    app_flask.run(threaded=True, port=7611, use_reloader=False, host="0.0.0.0")

if __name__ == "__main__":
    main()
