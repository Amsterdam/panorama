FROM amsterdam/panorama_image_processing:latest
MAINTAINER datapunt.ois@amsterdam.nl

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

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

USER datapunt
COPY panorama /app/

ARG OBJECTSTORE_PASSWORD
ENV OBJECTSTORE_PASSWORD=$OBJECTSTORE_PASSWORD

ARG AMPQ_HOST
ENV AMPQ_HOST=$AMPQ_HOST

USER datapunt
ENTRYPOINT ["python3", "manage.py", "work"]
