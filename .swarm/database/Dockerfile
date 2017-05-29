FROM build.datapunt.amsterdam.nl:5000/atlas/postgres
MAINTAINER datapunt.ois@amsterdam.nl

COPY update-db.sh /bin/update-db.sh
COPY z_import_panorama.sh /docker-entrypoint-initdb.d/z_import_panorama.sh
