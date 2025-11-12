from setuptools import setup, find_packages

setup(
    name='kappa',
    version='0.1.0',
    description='Compression-based structural analysis for molecular simulations',
    author='Your Name',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'pandas',
        'hilbertcurve',
        'tqdm',
    ],
    python_requires='>=3.8',
)
