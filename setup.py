from setuptools import setup, find_packages, Extension

setup(
    name = "ekmmeters",
    version = "0.2.4",
    license='MIT',
    description='Python API for V3 and V4 EKM Omnimeters',
    author = 'EKM Metering',
    author_email = "info@ekmmetering.com",
    url = 'https://github.com/ekmmetering/ekmmeters',
    download_url = 'https://github.com/ekmmetering/ekmmeters/tarball/0.2.4',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    py_modules=['ekmmeters'],
    install_requires=[
          'OrderedDict==1.1',
          'pyserial==3.0.1',
      ]
)
