import os
from setuptools import setup, find_packages
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
if os.path.exists("requirements.txt"):
    install_reqs = parse_requirements("requirements.txt")
else:
    install_reqs = parse_requirements("Flask_Captcha.egg-info/requires.txt")

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='Flask-Captcha',
    version="0.1.8",
    description='A very simple, yet powerful, Flask captcha extension',
    author='Eduardo Robles Elvira',
    author_email='edulix@wadobo.com',
    url='https://github.com/agoraciudadana/flask-captcha',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Security',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=reqs
)
