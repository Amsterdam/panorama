FROM build.datapunt.amsterdam.nl:5000/atlas/postgres
MAINTAINER datapunt.ois@amsterdam.nl

RUN echo 'max_connections = 200' >> "/usr/share/postgresql/$PG_MAJOR/postgresql.conf.sample"

