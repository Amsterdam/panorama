FROM python:3.11-slim
MAINTAINER datapunt@amsterdam.nl
RUN apt-get update \
    && apt-get -y upgrade \
        && apt-get install -y \
                build-essential \
                gfortran \
                git \
                cmake \
                gdal-bin \
                libatlas-base-dev \
                libboost-python-dev \
                libcurl3-dev \
                libeigen3-dev \
                libgeos-dev \
                libjpeg62-turbo-dev \
                libleptonica-dev \
                liblog4cplus-dev \
                libtesseract-dev \
                netcat \
                pkg-config \
                python3-dev

# OpenALPR won't build against OpenCV 3.* or newer, so install the latest/last
# OpenCV 2.x. https://github.com/openalpr/openalpr/issues/739
WORKDIR /temp
RUN git config --global advice.detachedHead false \
    && git clone -b 2.4.13.6 --depth=1 https://github.com/opencv/opencv.git
WORKDIR /temp/opencv/build
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr \
    -D CMAKE_INSTALL_SYSCONFDIR:PATH=/etc \
    -D INSTALL_C_EXAMPLES=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..
RUN make -j $(nproc) && make install

# Install OpenALPR from source.
WORKDIR /temp
RUN git config --global advice.detachedHead false \
    && git clone -b v2.3.0 --depth=1 https://github.com/openalpr/openalpr.git

WORKDIR /temp/openalpr/src/build
RUN cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc ..
RUN make -j $(nproc)

WORKDIR /temp/openalpr/src/build
RUN make install

WORKDIR /app
RUN mkdir openalpr
RUN cp /temp/openalpr/src/bindings/python/openalpr/* /app/openalpr/
RUN rm -rf /temp/openalpr

RUN pip install --no-cache-dir dlib

WORKDIR /app

RUN adduser --system datapunt \
	&& mkdir -p /static \
	&& chown datapunt /static \
	&& pip install uwsgi

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

USER datapunt

COPY panorama /app/
COPY deploy /deploy/

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=panorama.settings
RUN python manage.py collectstatic --noinput

CMD uwsgi
