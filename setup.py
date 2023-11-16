from setuptools import setup

version = '0.0.1-alpha'
URL = 'https://github.com/Garulf/PyFlowLauncher'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='pyflowlauncher',
      version=version,
      description='Python library to help build Flow Launcher plugins.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url=URL,
      project_urls={
          "Bug Tracker": f"{URL}/issues"
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: Microsoft :: Windows",
      ],
      author='William McAllister',
      author_email='dev.garulf@gmail.com',
      license='MIT',
      packages=['pyflowlauncher'],
      zip_safe=True,
      package_data={
            'pyflowlauncher': ['py.typed'],
      },
      install_requires=[
          'importlib-metadata; python_version < "3.8"',
      ]
      )
