from setuptools import setup

setup(
    name="biosemipy",
    version="0.1.0",
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
        "pyopengl",
        "PyQt6",
        "scipy",
    ],
    zip_safe=False,
)
