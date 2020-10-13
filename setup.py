from setuptools import setup

setup(name='programaker-gitlab-service',
      version='0.0.1',
      description='Programaker service to interact with a Gitlab instance.',
      author='kenkeiras',
      author_email='kenkeiras@codigoparallevar.com',
      license='Apache License 2.0',
      packages=['programaker_gitlab_service'],
      scripts=['bin/programaker-gitlab-service'],
      include_package_data=True,
      install_requires = [
          'python-gitlab',
          'programaker-bridge',
          'xdg',
      ],
      zip_safe=False)
