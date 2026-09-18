from setuptools import setup, find_packages

setup(
    name="HRSploit",
    version="1.0.0",
    description="HRSploit - Advanced Security Research Framework",
    author="Altay HR",
    author_email="altay@turkhackteam.org",
    url="https://github.com/ThT0AltayHR/HRSploit",
    packages=find_packages(),
    py_modules=["HRSploit"],
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "urllib3>=1.26.0",
        "colorama>=0.4.6",
        "rich>=13.0.0",
    ],
    entry_points={"console_scripts": ["hrsploit=HRSploit:main"]},
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
