FROM grafana/loki:2.8.5

ADD local-config.yaml /etc/loki/
# Health Check -> /distributor/ring

CMD [ "-config.file=/etc/loki/local-config.yaml" ]