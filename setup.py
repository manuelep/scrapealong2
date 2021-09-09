import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scrapealong",
    version="0.1.6",
    author="Manuele Pesenti",
    author_email="manuele@inventati.org",
    description="Library for scraping data from web sites with async flavour",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manuelep/scrapealong2",
    project_urls={
        "Bug Tracker": "https://github.com/manuelep/scrapealong2/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'aiohttp',
        'bs4',
        'price-parser',
        'pyppeteer',
        'nest_asyncio',
        'diskcache',
        # 'froxy',
        'mptools>=1.0.7'
    ]
)
