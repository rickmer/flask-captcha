# Flask-Captcha

Python Simple Captcha is an extremely simple, yet highly customizable flask extension to use

## Features

* Very simple to setup and deploy, yet very configurable
* Can use custom challenges (e.g. random chars, simple maths, dictionary word, ...)
* Custom generators, noise and filter functions alter the look of the generated image
* Supports text-to-speech audio output of the challenge text, for improved accessibility

## Requirements

* Python 3.3+
* Flask
* A recent version of the Python Imaging Library (Pillow 2.2+) compiled with FreeType support
* Flite is required for text-to-speech (audio) output, but not mandatory

## Troubleshooting

* If the captcha does not render, try opening the img url link directly. If you get this error

"Python: The _imagingft C module is not installed"

You need to recompile Pillow with libfreetype6 support. To do this

$ sudo apt-get install libfreetype6-dev

$ pip uninstall pillow

$ pip install pillow