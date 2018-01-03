FROM nginx:latest
MAINTAINER datapunt@amsterdam.nl

EXPOSE 80

RUN apt-get update \
    && apt-get install -y \
            curl \
            netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/cache/apt

COPY default.conf /etc/nginx/conf.d/
CMD ["nginx", "-g", "daemon off;"]
