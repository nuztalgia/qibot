from setuptools import setup

setup(
    url="https://github.com/nuztalgia/qibot",
    project_urls={
        "Issue Tracker": "https://github.com/nuztalgia/qibot/issues",
        "Source Code": "https://github.com/nuztalgia/qibot",
    },
    install_requires=[
        "aiohttp >=3.8.0",
        "humanize >=4.2.3",
        "pillow >=9.2.0",
        "py-cord >=2.0.0",
    ],
    extras_require={
        "dev": [
            "black >=22.6.0",
            "isort >=5.10.0",
            "pre-commit >=2.20.0",
        ],
    },
)
