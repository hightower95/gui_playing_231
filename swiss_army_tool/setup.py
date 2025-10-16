"""
Swiss Army Tool - Setup Configuration
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

setup(
    name="swiss-army-tool",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive engineering toolkit for connector management, EPD operations, and document scanning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/swiss-army-tool",
    packages=find_packages(exclude=["tests", "tests.*", "document_scanner_cache", "e3_caches"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.0.0",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",  # For Excel file support
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "swiss-army-tool=app.main:main",
        ],
    },
    package_data={
        "": ["*.md", "*.json", "*.csv"],
    },
    include_package_data=True,
    zip_safe=False,
)
