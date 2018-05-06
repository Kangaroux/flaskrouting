from setuptools import setup

with open("README.md") as f:
  readme = f.read()

setup(name="flaskrouting",
  description="Create simple, nestable routes in flask.",
  long_description=readme,
  long_description_content_type="text/markdown",
  version="1.0",
  author="kangaroux",
  author_email="roux.jesse@gmail.com",
  packages=["flaskrouting"],
  url="https://github.com/Kangaroux/flaskrouting",
  license="MIT",
)