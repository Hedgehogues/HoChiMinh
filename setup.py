import setuptools
try:
    from pip._internal import main as pipmain
except:
    print('your version of pip is deprecated')
    from pip import main as pipmain


class InternalRequirements:
    pass


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


with open("README.md", "r") as fh:
    long_description = fh.read()

install_reqs = parse_requirements('./requirements')
print(f'public requirements: {install_reqs}')

kwargs = {
    'name': "HoChiMinh",
    'version': "1.0.1",
    'author': 'Egor Urvanov',
    'author_email': 'hedgehogues@bk.ru',
    'description': 'Ho Chi Minh is designed to extract textual information from tables presented in PDF, pictures or other format. Хошимин предназначен для извлечения текстовой информации из таблиц, представленных в PDF, картинках или ином формате.',
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',
    'url': 'https://github.com/Hedgehogues/HoChiMinh',
    'packages': setuptools.find_packages(),
    'classifiers': [
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    'install_requires': install_reqs,
}

setuptools.setup(**kwargs)
