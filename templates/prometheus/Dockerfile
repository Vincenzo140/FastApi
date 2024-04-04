FROM prom/prometheus:v2.47.0

# Health Check -> http://localhost:<port>/-/healthy

CMD ["--web.listen-address=:8002", "--config.file=/etc/prometheus/prometheus.yml"]
