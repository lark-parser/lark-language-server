from setuptools import setup

setup(
    name="lark-language-server",
    version="0.1.0",
    packages=['lark_language_server'],
    install_requires=["pygls==0.9.0", "lark-parser"],
    python_requires=">=3.7",
    extras_require={"test": ["pytest"]},
    package_data={},
    description="Language Server for Lark Grammar",
    license="MIT",
    url="https://github.com/lark-parser/lark-language-server",
)
