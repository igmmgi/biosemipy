from setuptools import setup

setup(name='biosemipy',
      version='0.0.1',
      description='Code to read BioSemi BDF EEG files',
      author='IGM',
      packages=['biosemipy'],
      license='MIT',
      install_requires=['numba', 'numpy'],
      zip_safe=False
      )
