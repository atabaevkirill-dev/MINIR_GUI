from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="minir-gui",
    version="1.0.0",
    author="Thermal Camera Team",
    author_email="thermal-camera@example.com",
    description="GUI application for controlling MINIR thermal camera via RS-232 protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/minir-gui",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyserial>=3.5",
        "PyQt6>=6.4.0",
    ],
    entry_points={
        "console_scripts": [
            "minir-gui=main_pyqt_claude:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
)