Datapunt panorama API
======================

Project om beelden gemaakt in equirectangulaire projectie te importeren, en te ontsluiten via een API.

De API-laag bestaat uit twee componenten:

* Een OGC (WMS/WFS)-server die de opnamelocatieas en de metadata serveert,
* Een REST-API die aanvullende functionaliteiten biedt.


Requirements
------------

* Docker-Compose (required)


Developing
----------

Use `docker-compose` to start a local set of dockers.

	(sudo) docker-compose start

or

	docker-compose up
	
You can also start the web project locally on port 8000 for live development, it will connect to the containerized database. 

Unit tests run locally
----------------------

name the django app explicitly.

    web/panorama/manage.py test datapunt_api

Running panorama demo
---------------------

Use http://localhost:8088/demo in a browser to see a demo of normalized panoramas in Marzipano viewer.

Running job docker from root of the project:
-----------------------------

make sure you have the OBJECTSTORE_PASSWORD in an environment file (for instance ~/.docker/env/objectstore.env)

	docker build . -f JobDockerfile -t job
	docker run --env-file ~/.docker/env/objectstore.env job 2016/03/17/TMX7315120208-000020/pano_0000_000000.jpg 359.75457352539 -0.467467454247501 -0.446629825528845
