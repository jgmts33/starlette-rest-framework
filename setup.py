from distutils.core import setup

setup(
    name = 'starlette-rest-framework',
    packages = ['srf'],
    version = '0.0.4',
    license='MIT',
    description = 'A REST framework for Starlette inspired by Django REST framework.',
    author = 'Luke Sapan',
    url = 'https://github.com/lsapan/starlette-rest-framework',
    download_url = 'https://github.com/lsapan/starlette-rest-framework/archive/refs/tags/0.0.4.tar.gz',
    keywords = ['starlette', 'rest', 'framework'],
    install_requires=[
        'starlette',
        'pydantic',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)
