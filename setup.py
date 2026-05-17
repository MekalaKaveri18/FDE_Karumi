from setuptools import setup, find_packages

setup(
    name="karumi-toolkit",
    version="0.1.0",
    description="Karumi Deployment & Reliability Toolkit for AI Agent Onboarding, Testing, and Monitoring",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/karumi-toolkit",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        line.strip() for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "karumi-validate=src.validators.cli:main",
            "karumi-test=src.testing.cli:main",
            "karumi-monitor=src.monitoring.dashboard:main",
        ],
    },
)
