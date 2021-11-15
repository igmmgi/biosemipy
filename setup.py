from setuptools import setup

setup(
    name="biosemipy",
    version="0.0.6",
    description="Code to read BioSemi BDF EEG files",
    author="IGM",
    packages=["biosemipy"],
    license="MIT",
    install_requires=[
        "matplotlib",
        "numba",
        "numpy",
        "pandas",
        "pyqtgraph",
        "PyQt5",
        "scipy",
    ],
    zip_safe=False,
)
