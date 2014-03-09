# -*- coding: utf-8 -*-
import random
from flask import current_app, url_for
from six import u

def math_challenge():
    operators = ('+', '*', '-',)
    operands = (random.randint(1, 10), random.randint(1, 10))
    operator = random.choice(operators)
    if operands[0] < operands[1] and '-' == operator:
        operands = (operands[1], operands[0])
    challenge = '%d%s%d' % (operands[0], operator, operands[1])
    return '%s=' % (challenge), eval(challenge)


def random_char_challenge():
    chars, ret = u('abcdefghijklmnopqrstuvwxyz'), u('')
    for i in range(current_app.config['CAPTCHA_LENGTH']):
        ret += random.choice(chars)
    return ret.upper(), ret


def unicode_challenge():
    chars, ret = u('äàáëéèïíîöóòüúù'), u('')
    for i in range(current_app.config['CAPTCHA_LENGTH']):
        ret += random.choice(chars)
    return ret.upper(), ret


def word_challenge():
    words_dict = current_app.config['CAPTCHA_WORDS_DICTIONARY']
    min_len = current_app.config['CAPTCHA_DICTIONARY_MIN_LENGTH']
    max_len = current_app.config['CAPTCHA_DICTIONARY_MAX_LENGTH ']
    fd = open(words_dict, 'rb')
    l = fd.readlines()
    fd.close()
    while True:
        word = random.choice(l).strip()
        if len(word) >= min_len and len(word) <= max_len:
            break
    return word.upper(), word.lower()


def huge_words_and_punctuation_challenge():
    "Yay, undocumneted. Mostly used to test Issue 39 - http://code.google.com/p/django-simple-captcha/issues/detail?id=39"
    words_dict = current_app.config['CAPTCHA_WORDS_DICTIONARY']
    min_len = current_app.config['CAPTCHA_DICTIONARY_MIN_LENGTH']
    max_len = current_app.config['CAPTCHA_DICTIONARY_MAX_LENGTH ']
    fd = open(words_dict, 'rb')
    l = fd.readlines()
    fd.close()
    word = ''
    while True:
        word1 = random.choice(l).strip()
        word2 = random.choice(l).strip()
        punct = random.choice(current_app.config['CAPTCHA_PUNCTUATION'])
        word = '%s%s%s' % (word1, punct, word2)
        if len(word) >= min_len and len(word) <= max_len:
            break
    return word.upper(), word.lower()


def noise_arcs(draw, image):
    fg_color = current_app.config['CAPTCHA_FOREGROUND_COLOR']
    size = image.size
    draw.arc([-20, -20, size[0], 20], 0, 295, fill=fg_color)
    draw.line([-20, 20, size[0] + 20, size[1] - 20], fill=fg_color)
    draw.line([-20, 0, size[0] + 20, size[1]], fill=fg_color)
    return draw


def noise_dots(draw, image):
    fg_color = current_app.config['CAPTCHA_FOREGROUND_COLOR']
    size = image.size
    for p in range(int(size[0] * size[1] * 0.1)):
        draw.point((random.randint(0, size[0]), random.randint(0, size[1])),
                   fill=fg_color)
    return draw


def post_smooth(image):
    try:
        import ImageFilter
    except ImportError:
        from PIL import ImageFilter
    return image.filter(ImageFilter.SMOOTH)


def captcha_image_url(key):
    """ Return url to image. Need for ajax refresh and, etc"""
    return url_for('.captcha-image', args=[key])

def _callable_from_string(string_or_callable):
    if callable(string_or_callable):
        return string_or_callable
    else:
        return getattr(__import__('.'.join(string_or_callable.split('.')[:-1]),
            {}, {}, ['']), string_or_callable.split('.')[-1])

def get_challenge():
    return _callable_from_string(current_app.config['CAPTCHA_CHALLENGE_FUNCT'])

def noise_functions():
    noise_fs = current_app.config['CAPTCHA_NOISE_FUNCTIONS']
    if noise_fs:
        return map(_callable_from_string, noise_fs)
    return []

def filter_functions():
    filter_fs = current_app.config['CAPTCHA_FILTER_FUNCTIONS']
    if filter_fs:
        return map(_callable_from_string, filter_fs)
    return []
