#!/usr/bin/env python3
from setuptools import setup

setup(
	name = 'minecraftd',
	version = '0.0.1',
	packages = ['minecraftd'],
	entry_points = {
		'console_scripts': [
			'minecraftd = minecraftd.__main__:main'
		]
	})
