"""
Setup script for the pattern drafting system.
"""
from setuptools import setup, find_packages

setup(
    name="pattern_drafting",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "matplotlib>=3.4.0",
        "pillow>=8.2.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python library for creating, manipulating, and rendering clothing patterns",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pattern_drafting",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.7",
)