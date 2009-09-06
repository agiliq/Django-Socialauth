import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "djano-socialauth",
    version = "0.1.1",
    packages = ['socialauth', 'openid_consumer'],
    author = "Usware Technologies",
    author_email = "info@uswaretech.com",
    description = "Allows logging via Facebook, Yahoo, Gmail, Twitter and Openid ",
    url = "http://socialauth.uswaretech.net/",
    include_package_data = True
)
