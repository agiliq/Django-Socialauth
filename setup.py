import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name = "django-socialauth",
    version = "0.1.2c",
    packages = ['socialauth',
                'socialauth/lib',
                'socialauth/templatetags',
                'openid_consumer'],
    package_data = { 'socialauth': [ 'templates/*.html',
                                     'templates/socialauth/*.html',
                                     'templates/socialauth/*.htm',
                                     'templates/openid/*.html'],
                     'openid_consumer': ['locale/*/LC_MESSAGES/*.po']
                     },
    zip_safe = False,
    author = "Agiliq Solutions",
    author_email = "info@uswaretech.com",
    description = "Allows logging via Facebook, Yahoo, Gmail, Twitter and Openid ",
    url = "http://agiliq.com/",
)
