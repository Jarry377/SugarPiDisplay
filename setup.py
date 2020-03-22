from setuptools import setup

setup(
    name='sugarpidisplay',
    version='0.10',
    description='Display your CGM data on a tiny LCD or epaper screen',
    url='https://github.com/bassettb/SugarPiDisplay',
    author='Bryan Bassett',
    license='MIT',
    packages=['sugarpidisplay'],
    install_requires=[
        'Flask',
		'Flask-WTF',
		'RPLCD',
        'Pillow',
        'spidev',
        'smbus',
        'RPi.GPIO'
    ],
    zip_safe=False
)
