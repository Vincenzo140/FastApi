from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_pessoa(self):
        headers = {"Content-Type": "application/json"}
        data = {
            "apelido": "novapessoa",
            "nome": "Nova Pessoa",
            "nascimento": "2000-01-01",
            "stack": ["Python"]
        }
        response = self.client.post("/pessoas", json=data, headers=headers)
        if response.status_code != 201:
            self.environment.events.request_failure.fire(
                request_type="POST",
                name="/pessoas",
                response_time=0,
                response_length=0,
                exception="Teste de carga interrompido devido a erro HTTP"
            )

    @task
    def get_pessoa_by_id(self):
        response = self.client.get(f"/pessoas/{self.get_random_pessoa_id()}")
        if response.status_code != 200:
            self.environment.events.request_failure.fire(
                request_type="GET",
                name=f"/pessoas/{self.get_random_pessoa_id()}",
                response_time=0,
                response_length=0,
                exception="Teste de carga interrompido devido a erro HTTP"
            )

    @task
    def get_pessoas_by_search_term(self):
        response = self.client.get("/pessoas?t=python")
        if response.status_code != 200:
            self.environment.events.request_failure.fire(
                request_type="GET",
                name="/pessoas?t=python",
                response_time=0,
                response_length=0,
                exception="Teste de carga interrompido devido a erro HTTP"
            )

    def get_random_pessoa_id(self):
        import random
        return random.choice(["id1", "id2", "id3"])
