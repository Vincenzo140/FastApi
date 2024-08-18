## 🚀 Recursos Principais

```mermaid
graph TD
    %% Definindo cores e estilos
    classDef fastapi fill:#1abc9c,stroke:#000,stroke-width:2px;
    classDef otel fill:#3498db,stroke:#000,stroke-width:2px;
    classDef prometheus fill:#e74c3c,stroke:#000,stroke-width:2px;
    classDef grafana fill:#f39c12,stroke:#000,stroke-width:2px;
    classDef loki fill:#2ecc71,stroke:#000,stroke-width:2px;
    classDef tempo fill:#9b59b6,stroke:#000,stroke-width:2px;
    classDef analysis fill:#34495e,stroke:#000,stroke-width:2px,color:#fff;

    subgraph FastAPI
        A[APP - A] --> |metrics/logs/traces\n127.0.0.1:8000| OTEL[OpenTelemetry Collector]
        B[APP - B] --> |metrics/logs/traces\n127.0.0.1:8001| OTEL
        C[APP - C] --> |metrics/logs/traces\n127.0.0.1:8007| OTEL
        class A,B,C fastapi
    end
    
    subgraph OpenTelemetry Collector
        OTEL --> |push Metrics| Prometheus[Prometheus\nMetrics:127.0.0.1:8002]
        OTEL --> |push Logs| Loki[Grafana Loki\nLogs:127.0.0.1:8006\nLogs:127.0.0.1:8009]
        OTEL --> |push Traces| Tempo[Grafana Tempo\nTempo:127.0.0.1:8003\nTempo:127.0.0.1:8004\nTempo:127.0.0.1:8008]
        class OTEL otel
    end
    
    Prometheus --> |Metrics| Grafana[Grafana\n127.0.0.1:8005]
    Loki --> |Logs| Grafana
    Tempo --> |Traces| Grafana
    
    Grafana --> |Alerts| Analysis[Analysis]
    Grafana --> |Analysis| Analysis
    
    %% Aplicando estilos
    class OTEL otel
    class Prometheus prometheus
    class Grafana grafana
    class Loki loki
    class Tempo tempo
    class Analysis analysis
```

- **Loki:** Análise de Logs.
- **Tempo:** Análise de Traces.
- **Prometheus:** Análise de Métricas.
- **Grafana:** Dashboard para visualização.
- **API:** Armazena requisições ao ser acessada.
- **Docker:** Gerencia toda a aplicação na rede das plataformas.

## 🛠 Tecnologias Utilizadas
- Python
- FastAPI
- OpenTelemetry
- Grafana
- Prometheus
- Loki
- Tempo

## 🔧 Configuração do Ambiente

### 1. Clone o Repositório

```bash
git clone https://github.com/Vincenzo140/FastApi.git
```

### 2. Instalação e Configuração

#### Usando Docker:

1. Inicie o Docker manualmente:
   ```bash
   cd package_obs
   docker-compose up -d
   docker-compose up
   ```

### 3. Executando Testes de Carga com Locust

1. Instale o **Locust**:
   ```bash
   pip install locust
   ```

2. Rode o Locust:
   ```bash
   locust -f locustfile.py --headless --users 100 --spawn-rate 10 -H http://localhost:8000
   ```

### 4. Acessando as Ferramentas de Monitoramento

- **Grafana:** [http://localhost:8005](http://localhost:8005)
- **Prometheus:** [http://localhost:8002](http://localhost:8002)
- Outras portas dependentes podem ser verificadas nos containers Docker.