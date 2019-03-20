from setuptools import setup

setup(name='plaza-gitlab-service',
      version='0.0.1',
      description='Plaza service to interact with a Gitlab instance.',
      author='kenkeiras',
      author_email='kenkeiras@codigoparallevar.com',
      license='Apache License 2.0',
      packages=['plaza_gitlab_service'],
      scripts=['bin/plaza-gitlab-service'],
      include_package_data=True,
      install_requires = [
          'python-gitlab',
          'plaza_service',
          'xdg',
      ],
      zip_safe=False)
