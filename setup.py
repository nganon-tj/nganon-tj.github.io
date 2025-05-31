from setuptools import setup, find_packages
setup(
    name="jannisary",
    version="0.1",
    packages=find_packages(),
    scripts=[],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
        'click',
        'jinja2==3.0.3',
        'pyyaml',
        'tabulate'
    ],
    extras_require={
        'dev': [
            'pytest',
        ]
    },
    package_data={},
    entry_points = {
        'console_scripts': ['janissary=janissary.scripts.janissary:main'],
    },

    # metadata to display on PyPI
    author="Jeff McBride",
    author_email="mcbridejc@gmail.com",
    description="Tool for processing Age of Empires II HD Edition recorded games",
    license="MIT",
    keywords="",
    url="",   # project home page, if any
)
