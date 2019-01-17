from setuptools import setup

setup(name='plaza-gitlab-service',
      version='0.1',
      description='Plaza service to interact with a Gitlab instance.',
      author='kenkeiras',
      author_email='kenkeiras@codigoparallevar.com',
      license='MIT',
      packages=['plaza_gitlab_service'],
      scripts=['bin/plaza-gitlab-service'],
      include_package_data=True,
      install_requires = [
          'python-gitlab',
          'plaza-service',
      ],
      zip_safe=False)
