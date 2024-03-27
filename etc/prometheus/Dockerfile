FROM prom/prometheus:v2.47.0

# Health Check -> http://localhost:<port>/-/healthy

CMD ["--web.listen-address=:9090", "--config.file=/etc/prometheus/prometheus.yml"]