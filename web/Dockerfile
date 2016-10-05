FROM python:3.5
MAINTAINER datapunt.ois@amsterdam.nl

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

RUN apt-get update \
	&& apt-get install -y \
		gdal-bin \
		libgeos-dev \
		netcat \
 	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
	&& adduser --system datapunt \
	&& mkdir -p /static \
	&& chown datapunt /static \
	&& pip install uwsgi

# -- START Build recipe found on https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux)
RUN apt-get update \
	&& apt-get install -y \
		libopencv-dev \
		libtesseract-dev \
		git \
		cmake \
		build-essential \
		libleptonica-dev

RUN apt-get update \
	&& apt-get install -y \
		liblog4cplus-dev \
		libcurl3-dev

# Clone the latest code from GitHub
WORKDIR /temp
RUN git clone https://github.com/openalpr/openalpr.git

# ADDED STEP: choose latest versioned git-tag
WORKDIR /temp/openalpr
RUN git checkout v2.3.0

# Setup the build directory
WORKDIR /temp/openalpr/src
RUN mkdir build

# setup the compile environment
WORKDIR /temp/openalpr/src/build
RUN cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc ..

# compile the library
WORKDIR /temp/openalpr/src/build
RUN make

# Install the binaries/libraries to your local system (prefix is /usr)
WORKDIR /temp/openalpr/src/build
RUN make install
# -- END Build recipe found on https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux)

WORKDIR /app
RUN mkdir openalpr
RUN cp /temp/openalpr/src/bindings/python/openalpr/* /app/openalpr/

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

USER datapunt
COPY panorama /app/
CMD /app/docker-entrypoint.sh