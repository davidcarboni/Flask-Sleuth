from setuptools import setup, find_packages
import unittest


def readme():
    with open('README.md') as f:
        return f.read()


def test_suite():
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    return suite


setup(name='flask_logging',
      version='0.0.1',
      description='Spring Cloud Sleuth logging implementation for Python 2/3.',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Topic :: System :: Logging',
          'Topic :: Internet :: Log Analysis',
          'Intended Audience :: Developers',
          'Framework :: Flask',
          'License :: OSI Approved :: MIT License',
      ],
      keywords='logging b3 distributed tracing spring boot cloud sleuth',
      url='https://gitlab.ros.gov.uk/CarbonD/flask_logging',
      author='David Carboni',
      author_email='david@carboni.io',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'flask',
      ],
      test_suite='setup.test_suite',
      include_package_data=True,
      zip_safe=True,
      )
