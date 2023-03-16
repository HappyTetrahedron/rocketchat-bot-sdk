import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='rocketchat_bot_sdk',
    version='0.0.3',
    scripts=[],
    author="Aline Abler",
    author_email="alinea@riseup.net",
    description="SDK for creating chat bots with the Rocketchat API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HappyTetrahedron/rocketchat-bot-sdk",
    install_requires=['rocketchat_API', 'websockets==10.4'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
