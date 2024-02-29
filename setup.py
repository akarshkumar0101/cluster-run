from setuptools import setup, find_packages

setup(
    name='cluster-run',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cluster_run=cluster_run.main:main',
        ],
    },
)
