"""
@fileoverview Package setup configuration for the AI governance system
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Package installation and distribution configuration
@responsibility Define package metadata, dependencies, and entry points for governance system
@dependencies setuptools, find_packages
@integration_points pip installation, CLI entry points, dependency management
@testing_strategy Installation tests, dependency resolution tests, CLI invocation tests
@governance Ensures proper dependency versions for governance system stability

Business Logic Summary:
- Define package metadata and version
- Specify runtime dependencies
- Configure CLI entry points
- Enable pip installation
- Manage dependency versions

Architecture Integration:
- Enables pip install governance/
- Creates CLI command 'governance'
- Ensures dependency compatibility
- Supports development installation
- Enables package distribution

Sarah's Framework Check:
- What breaks first: Incompatible dependency versions causing import failures
- How we know: Installation errors or runtime import exceptions
- Plan B: Pin exact versions for critical dependencies
"""

from setuptools import setup, find_packages

setup(
    name="governance",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0",
        "click>=8.0",
        "aiofiles>=0.8",
        "pytest>=7.0",
        "pytest-asyncio>=0.21",
    ],
    entry_points={
        'console_scripts': [
            'governance=governance.cli.main:cli',
        ],
    },
)