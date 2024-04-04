FROM grafana/grafana:10.1.2

# Config Datasources
ADD datasource.yml /etc/grafana/provisioning/datasources/

# Config Dashboards
COPY dashboards/ /etc/grafana/dashboards/
ADD dashboards.yaml /etc/grafana/provisioning/dashboards/

ENV GF_AUTH_ANONYMOUS_ENABLED true
ENV GF_AUTH_ANONYMOUS_ORG_ROLE Admin

# ADD grafana.ini /etc/grafana/