from setuptools import setup

setup(
    name='tsmtool',
    version='0.1',
    py_modules=['tsmtool'],
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
        'bs4',
        'pprint',
        'json',
        'datetime',
    ],
    entry_points='''
        [console_scripts]
        tsmtool=tsmtool:cli
    ''',
)
