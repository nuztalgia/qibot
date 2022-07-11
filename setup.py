from setuptools import setup

setup(
    install_requires=[
        "aiohttp == 3.8.1",
        "humanize == 4.2.3",
        "pillow == 9.2.0",
        "py-cord == 2.0.0",
    ],
    extras_require={
        "dev": [
            "black == 22.6.0",
            "isort == 5.10.1",
            "pre-commit ==2.20.0",
        ],
    },
)
