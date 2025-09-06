"""
Setup configuration for AI Orchestration Platform
Following enterprise monorepo structure with governance compliance
"""

from setuptools import setup, find_packages

setup(
    name="aiorchestration",
    version="2.1.0",
    description="AI Orchestration Platform with Extreme Governance",
    author="AI Orchestration Team",
    author_email="governance@system.local",
    packages=find_packages(include=[
        "libs", "libs.*",
        "libs.shared_types", "libs.shared_types.*",
        "libs.shared_utils", "libs.shared_utils.*",  
        "libs.governance", "libs.governance.*",
        "apps", "apps.*"
    ]),
    package_dir={
        "libs.shared_types": "libs/shared_types",
        "libs.shared_utils": "libs/shared_utils"
    },
    python_requires=">=3.10",
    install_requires=[
        # Core dependencies will be added from requirements files
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "governance": [
            "pyyaml>=6.0",
            "jsonschema>=4.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ai-api=apps.api.main:main",
        ],
    },
)