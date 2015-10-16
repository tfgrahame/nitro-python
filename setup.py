from setuptools import setup

setup(
    name='nitro-python',
    version='0.0.1',
    author='Tom Grahame',
    author_email='tom.grahame@bbc.co.uk',
    packages=['nitro-python'],
    package_dir={'nitro_py': 'nitro_py'},
    include_package_data=True,
    url='',
    description='Python Library for Nitro.',
    zip_safe = False,
    install_requires=[
        'requests',
        'lxml'
        ]
)
