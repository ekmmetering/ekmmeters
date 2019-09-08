from setuptools import setup, find_packages, Extension

setup(
    name = "ekmmeters",
    version = "0.2.5",
    license='MIT',
    description='Python API for V3 and V4 EKM Omnimeters',
    author = 'EKM Metering',
    author_email = "info@ekmmetering.com",
    url = 'https://github.com/ekmmetering/ekmmeters',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
    ],
    py_modules=['ekmmeters'],
    install_requires=[
          'OrderedDict>=1.1',
          'pyserial>=3.0.1',
      ]
)
