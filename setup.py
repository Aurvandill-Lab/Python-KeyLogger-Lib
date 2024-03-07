from setuptools import setup, find_packages

setup(
    name='PyKeyLogger',
    version='0.1.0-alpha',
    author="Aurvandill Lab",
    author_email='aurvandillresearch@gmail.com',
    description='A multithreaded keylogger template based on low-level keyboard hooks for python',
    # long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Aurvandill-Lab/Python-KeyLogger-Lib',
    packages=find_packages(exclude=('tests*', 'testing*')),
    install_requires=[
        # List your project's dependencies here.
    ],
    classifiers=[
        'Development Status :: 0.1.0 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
