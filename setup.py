"""
OMNI V4 Setup Configuration
"""

from setuptools import setup, find_packages

setup(
    name="omni_v4",
    version="4.0.0",
    description="Restaurant Analytics Processing Pipeline",
    author="Jorge Alexander",
    python_requires=">=3.9",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "supabase>=2.3.0",
        "pandas>=2.1.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "mypy>=1.7.1",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "ipython>=8.18.1",
        ]
    },
    entry_points={
        "console_scripts": [
            "omni-run=scripts.run_pipeline:main",
            "omni-backfill=scripts.backfill:main",
        ]
    },
)