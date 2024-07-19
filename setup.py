from setuptools import setup, find_packages

setup(
    name='DupliPicFinder',
    version='0.1.0',
    description='A tool to find and manage duplicate images using perceptual hashing.',
    author='Timo Schneider',
    url='https://github.com/timoschneider249/DupliPicFinder',
    packages=find_packages(),
    install_requires=[
        'imagehash==4.3.1',
        'Pillow==10.4.0',
    ],
    extras_require={
        'dev': [
            'pip==24.1.2',
            'wheel==0.43.0',
            'setuptools==71.0.3',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    keywords='image comparison duplicate detection',
)
