"""
Setup configuration for Spotify Playlist Generator
=================================================
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    requirements = (this_directory / "requirements.txt").read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="spotify-playlist-generator",
    version="2.0.0",
    author="MaxBriliant",
    author_email="mxbit@yahoo.com",
    description="Create Spotify playlists from simple text files with smart search capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maxbriliant/spotify_playlist_generator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "spotify-playlist=main:main",
            "spotify-playlist-cli=cli.cli_interface:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json"],
    },
    project_urls={
        "Bug Reports": "https://github.com/maxbriliant/spotify_playlist_generator/issues",
        "Source": "https://github.com/maxbriliant/spotify_playlist_generator",
        "Documentation": "https://github.com/maxbriliant/spotify_playlist_generator#readme",
    },
    keywords=[
        "spotify",
        "playlist",
        "music",
        "automation",
        "api",
        "gui",
        "cli",
        "chatgpt",
        "ai"
    ],
)