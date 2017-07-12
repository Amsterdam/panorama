FROM build.datapunt.amsterdam.nl:5000/atlas/postgres
MAINTAINER datapunt.ois@amsterdam.nl

ARG OBJECTSTORE_PASSWORD
ENV OBJECTSTORE_PASSWORD=$OBJECTSTORE_PASSWORD

COPY z_import_panorama.sh /docker-entrypoint-initdb.d/z_import_panorama.sh
