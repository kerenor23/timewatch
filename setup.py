from os.path import exists
from distutils.core import setup
import timewatch

setup(
  name='timewatch',
  packages=['timewatch'],
  version=timewatch.__version__,
  description='A library automating worktime reports for timewatch.co.il',
  long_description=(open('README.md').read() if exists('README.md') else ''),
  author='Keren-Or & Nir Izraeli',
  author_email='nirizr@gmail.com',
  url ='https://github.com/kerenor23/timewatch',
  keywords=['timewatch', 'timewatch.co.il'], # arbitrary keywords
  classifiers=[]
)
