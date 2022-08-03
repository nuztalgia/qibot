from setuptools import setup

setup(
    url="https://github.com/nuztalgia/qibot",
    project_urls={
        "Issue Tracker": "https://github.com/nuztalgia/qibot/issues",
        "Source Code": "https://github.com/nuztalgia/qibot",
    },
    install_requires=[
        "aiohttp >=3.8.0",
        "botstrap >=0.1.0",
        "humanize >=4.2.3",
        "json5 >=0.9.8",
        "pillow >=9.2.0",
        "py-cord >=2.0.0",
    ],
    extras_require={
        "dev": [
            "pre-commit >=2.20.0",
            "setuptools >=61.0.0",
        ],
    },
)
