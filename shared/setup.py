from setuptools import setup, find_packages

setup(
    name="project-echo-shared",
    version="1.0.0",
    description="Shared libraries for Project Echo",
    author="Project Echo Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        # Add shared dependencies here
        # These will be installed when shared library is used
    ],
)
