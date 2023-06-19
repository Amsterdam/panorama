FROM debian:bookworm-slim
MAINTAINER datapunt@amsterdam.nl
RUN apt-get update \
    && apt-get -y upgrade \
        && apt-get install -y \
                build-essential \
                cmake \
                gdal-bin \
                git \
                libatlas-base-dev \
                libcurl3-dev \
                libeigen3-dev \
                libgeos-dev \
                libjpeg62-turbo-dev \
                libleptonica-dev \
                liblog4cplus-dev \
                libopencv-dev \
                libtesseract-dev \
                python3-dev \
                python3-pip \
                pkg-config

# Install OpenALPR from source. We use our own fork to get a version
# that will compile with OpenCV 4.x. Upstream supports that, but didn't
# tag a release; see https://github.com/openalpr/openalpr/issues/915.
WORKDIR /temp
RUN git config --global advice.detachedHead false \
    && git clone --depth=1 https://github.com/Amsterdam/openalpr.git

# Hack to make OpenALPR find Tesseract. Apparently, these files were removed
# from Tesseract 5.x. OpenALPR doesn't actually need them to build.
RUN touch /usr/include/tesseract/platform.h /usr/include/tesseract/thresholder.h

WORKDIR /temp/openalpr/build
RUN cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc ../src
RUN make -j $(nproc)

RUN make install

WORKDIR /app
RUN mkdir openalpr
RUN cp /temp/openalpr/src/bindings/python/openalpr/* /app/openalpr/
RUN rm -rf /temp/openalpr

WORKDIR /app

RUN adduser --system datapunt \
	&& mkdir -p /static \
	&& chown datapunt /static

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

USER datapunt

COPY panorama /app/
COPY deploy /deploy/

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=panorama.settings
RUN python3 manage.py collectstatic --noinput

CMD uwsgi
