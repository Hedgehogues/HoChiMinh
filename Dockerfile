FROM ubuntu:18.04 AS BUILD

RUN apt-get -y update
RUN apt-get install -y gcc python3 python3-pip python3-dev cmake make libsm6 libxext6 libxrender-dev python3.7-dev \
    make python3.7 python3-pip git gcc
RUN python3.7 -m pip install --upgrade pip
RUN pip install --upgrade pip

RUN git clone https://github.com/opencv/opencv.git
WORKDIR /opencv/build
RUN cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local ..
RUN make -j4
RUN make install

COPY . /app
WORKDIR /app

RUN PIP=pip3 PYTHON=python3.7 make deps
CMD PIP=pip3 PYTHON=python3.7 make run
