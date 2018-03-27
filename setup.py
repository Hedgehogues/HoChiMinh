from setuptools import setup

PACKAGE = "HoChiMinh"
NAME = "HoChiMinh"
DESCRIPTION = "Ho Chi Minh is designed to extract textual information from tables presented in PDF, pictures or " \
              "other format. Хошимин предназначен для извлечения текстовой информации из таблиц, представленных в " \
              "PDF, картинках или ином формате."
AUTHOR = "Egor Urvanov"
AUTHOR_EMAIL = "hedgehogues@bk.ru"
URL = "https://github.com/Hedgehogues/HoChiMinh"
req = open('requirements.txt').readlines()

setup(
    name=NAME,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    install_requiers=req,
)
