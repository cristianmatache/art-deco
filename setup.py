from pathlib import Path

from setuptools import find_packages, setup

LIB_ROOT = Path(__file__).parent
REQS_FILE = LIB_ROOT / '3rdparty/requirements.txt'
README_FILE = LIB_ROOT / 'README.md'


def main() -> None:
    setup(
        name='art_deco',
        version='0.0.1',
        packages=find_packages(exclude=['tests*', 'art_deco_test_examples*']),
        python_requires='>=3.7',
        install_requires=REQS_FILE.read_text(encoding='utf-8'),
        zip_safe=False,  # for mypy
        package_data={'{self.lib_name}': ['py.typed']},  # expose types to users
        author='Cristian Matache',
        author_email='Your email',
        description='',
        long_description=README_FILE.read_text(encoding='utf-8'),
    )


if __name__ == '__main__':
    main()
