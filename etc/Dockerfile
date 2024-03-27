FROM grafana/grafana:latest

# Config Datasources
ADD datasource.yml /etc/grafana/datasources/

# Config Dashboards
COPY dashboards/ /etc/grafana/dashboards/
ADD dashboards.yaml etc/grafana/
ENV GF_AUTH_ANONYMOUS_ENABLED true
ENV GF_AUTH_ANONYMOUS_ORG_ROLE Admin

# /etc/Dockerfile