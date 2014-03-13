#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
import argparse
from flask.ext.captcha import Captcha
from flask.ext.captcha.views import captcha_blueprint

ROOT_PATH = os.path.split(os.path.abspath(__file__))[0]

app_flask = Flask(__name__)
app_captcha = Captcha()

app_flask.register_blueprint(captcha_blueprint, url_prefix='/captcha')

@app_flask.route("/")
def hello():
    return render_template('home.html')

def main():
    # load settings
    app_flask.config.from_object("flask.ext.captcha.settings")
    app_flask.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///%s/db.sqlite' % ROOT_PATH
    db = SQLAlchemy(app_flask)
    app_captcha.init_app(app_flask)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--createdb", help="create the database",
                        action="store_true")
    pargs = parser.parse_args()
    if pargs.createdb:
        print("creating db")
        db.create_all()
        exit(0)
    app_flask.run(threaded=True, port=7611, use_reloader=False, host="0.0.0.0")

if __name__ == "__main__":
    main()
