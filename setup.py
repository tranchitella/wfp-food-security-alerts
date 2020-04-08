import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wfp-food-security-alerts",
    version="1.0.0",
    author="Fabio Tranchitella",
    author_email="fabio@tranchitella.eu",
    description="WFP food security alerts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://wfp.org",
    install_requires=[
        'Click>=7.1',
        'python-dateutil>=2.8.0',
        'requests>=2.23.0',
        'pyyaml>=5.3.0',
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        wfp-food-security-alerts=wfp_food_security_alerts.cli:cli_with_env
    """,
)
