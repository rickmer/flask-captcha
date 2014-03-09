# Django Simple Captcha

Python Simple Captcha is an extremely simple, yet highly customizable flask extension to use

## Features

* Very simple to setup and deploy, yet very configurable
* Can use custom challenges (e.g. random chars, simple maths, dictionary word, ...)
* Custom generators, noise and filter functions alter the look of the generated image
* Supports text-to-speech audio output of the challenge text, for improved accessibility
* Ajax refresh

## Requirements

* Python 2.5+
* Flask
* A recent version of the Python Imaging Library (PIL 1.1.7 or Pillow 2.2+) compiled with FreeType support
* Flite is required for text-to-speech (audio) output, but not mandatory

## Python 3 compatibility

The current development version supports Python3 via the `six <https://pypi.python.org/pypi/six>`_ compatibility layer.
You will need to install `Pillow <https://github.com/python-imaging/Pillow>`_ because PIL doesn't support Python3 yet.
