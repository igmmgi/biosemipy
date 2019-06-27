from setuptools import setup

setup(
    name="biosemipy",
    version="0.0.3",
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
        "mne",
    ],
    zip_safe=False,
)
