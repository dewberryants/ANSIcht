from setuptools import setup, find_packages

with open('./README.md') as f:
    readme = f.read()

with open('./LICENSE') as f:
    lic = f.read()

packages = find_packages()

setup(
    name='ANSIcht',
    version='0.0.5',
    description='A simple ANSI art editor.',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Dominik Behrens',
    author_email='dewberryants@gmail.com',
    url='https://github.com/dewberryants/ANSIcht',
    license=lic,
    packages=find_packages(exclude="docs"),
    package_data={"ansicht.resources": ["*.bin"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Art :: Pixel Art"
    ],
    install_requires=[
        'pygame',
        'numpy'
    ],
    entry_points={"console_scripts": ["ansicht = ansicht:run_ansicht"]}
)