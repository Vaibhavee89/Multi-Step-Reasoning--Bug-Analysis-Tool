"""Setup script for Code Analysis Agent."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="bug-analysis-tool",
    version="0.1.0",
    description="Multi-step reasoning agent for code analysis using LangChain and Claude",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/bug-analysis-tool",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.3.1",
        "langchain-anthropic>=0.3.0",
        "anthropic>=0.39.0",
        "python-dotenv>=1.0.1",
        "astroid>=3.3.5",
        "pylint>=3.3.1",
        "mypy>=1.13.0",
        "flake8>=7.1.1",
        "GitPython>=3.1.43",
        "rich>=13.9.4",
        "pydantic>=2.10.3",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.4",
            "black>=24.10.0",
            "isort>=5.13.2",
        ],
        "ui": [
            "streamlit>=1.41.1",
            "gradio>=5.9.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "bug-analyzer=src.ui.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
)
