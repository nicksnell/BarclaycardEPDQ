#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from barclaycard import __version__

setup(
	name='BarclaycardEPDQ',
	version=__version__,
	description='Python interface to the Barclaycard ePDQ interface',
	author='Nick Snell',
	author_email='nick@orpo.co.uk',
	url='http://orpo.co.uk/',
	download_url='http://orpo.co.uk/code/',
	license='License :: OSI Approved :: BSD License',
	classifiers=[
		'Environment :: Web Environment',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
	zip_safe=True,
	packages=find_packages(exclude=['tests',]),
	dependency_links = [],
	install_requires=['requests'],
	extras_require={}
)