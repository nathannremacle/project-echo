from setuptools import setup, find_packages

# Find all packages under src/ (returns ['common', 'download', 'scraping', 'transformation', 'publication'])
src_packages = find_packages(where="src")
# Build package list: shared, shared.src, and all shared.src.* subpackages
all_packages = ["shared", "shared.src"] + [f"shared.src.{pkg}" for pkg in src_packages]

setup(
    name="project-echo-shared",
    version="1.0.0",
    description="Shared libraries for Project Echo",
    author="Project Echo Team",
    packages=all_packages,
    package_dir={
        "shared": ".",
        "shared.src": "src",
    },
    python_requires=">=3.11",
    install_requires=[
        # Add shared dependencies here
        # These will be installed when shared library is used
    ],
)
