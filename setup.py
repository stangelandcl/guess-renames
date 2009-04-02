from setuptools import setup, find_packages

setup(
    name="guessrenames",
    packages=find_packages(),
    version='0.0.1',
    description="Tool to help your version control tool guess renames.",
#    long_description="TODO",
    entry_points={'console_scripts': ['guess-renames=guessrenames.script:main', ],
                  }
)
