import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="k-load",
    version="0.2.8",
    author="-T.K.-",
    author_email="tk.fantasy.233@gmail.com",
    description="A downloader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/T-K-233/k-load",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': 'k-load = k_load.__main__:console_entry'
    }
)
