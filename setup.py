#!/usr/bin/env python

from setuptools import setup

setup(
    name='django-affect',
    version='1.0.0',
    description='Request flagging engine inspired by django-waffle',
    author='Jeremy Sattefield',
    author_email='jsatterfield@consumeraffairs.com',
    url='https://github.com/ConsumerAffairs/django-affect',
    #license='',
    packages=[
        'affect', 'affect.migrations'],
    install_requires=[
        'Django>=1.4',
        'django-extensions'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Site Management'],
)
