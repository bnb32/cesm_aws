from distutils.core import setup

setup(
    name='ecrlcesm',
    version='0.1.0',
    url='https://github.com/bnb32/cesm_aws',
    author='Brandon N. Benton',
    description='for running cesm on aws',
    packages=['ecrlcesm'],
    package_dir={'ecrlcesm':'./ecrlcesm'},
    install_requires=['ecrlgcm']
)
