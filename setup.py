from setuptools import setup

setup(
    name="biosemipy",
    version="0.0.4",
    description="Code to read BioSemi BDF EEG files",
    author="IGM",
    packages=["biosemipy"],
    license="MIT",
    install_requires=[
        "numba",
        "numpy",
        "pyqtgraph",
        "PyQt5",
        "matplotlib",
        "scipy",
    ],
    zip_safe=False,
)
