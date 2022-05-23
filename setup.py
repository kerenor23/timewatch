from setuptools import setup
import timewatch

with open("requirements.txt", "r") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name='timewatch',
    packages=['timewatch'],
    version=timewatch.__version__,
    description='A library automating worktime reports for timewatch.co.il',
    author='Keren-Or & Nir Izraeli',
    author_email='nirizr@gmail.com',
    url='https://github.com/kerenor23/timewatch',
    keywords=['timewatch', 'timewatch.co.il'],  # arbitrary keywords
    classifiers=[],
    install_requires=REQUIREMENTS
)
