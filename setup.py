from setuptools import setup

def read_requirements():
    with open('requirements.txt', 'r') as f:
        return f.read().splitlines()

setup(
    name='WebAppVersion',
    version='1.0',
    packages=['WebAppVersion', 'WebAppVersion.utils', 'WebAppVersion.services', 'WebAppVersion.exceptions'],
    package_data={'WebAppVersion': ['./utils/remove_folder.bat']},
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'WebAppVersion=WebAppVersion.main:EntryPoint',
        ],
    },
)