from setuptools import setup, find_packages

setup(
    name='aws_cost_summary',
    version='0.1.0',
    packages=find_packages(),  
    install_requires=[
        'boto3',
        'numpy',
        'tabulate',
    ],
)
