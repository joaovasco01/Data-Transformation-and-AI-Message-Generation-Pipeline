from setuptools import find_packages, setup

packages = [
    "duckdb==0.10.0",
    "jupyter_client==8.6.0",
    "jupyter_core==5.7.1",
    "numpy==1.24.2",
    "openai==0.28.0",
    "pandas==1.5.3",
    "pydantic==2.5.3",
    "pydantic-settings==2.1.0",
    "pyarrow==14.0.2",
    "SQLAlchemy==1.4.46",
    "typer==0.9.0",
]

setup(
    name="message",
    version="0.1.0",
    author="Sword Health",
    author_email="ai@swordhealth.com",
    python_requires=">=3.8",
    packages=find_packages(exclude=("tests", "resources")),
    install_requires=packages,
    entry_points={
        "console_scripts": [
            "message = message.main:app",
        ],
    },
)
