from locust import HttpUser, task, between

class PessoaUser(HttpUser):
    wait_time = between(1, 5)

    @task(5)
    def create_pessoa(self):
        pessoa_data = {
            "apelido": "test",
            "nome": "Test User",
            "nascimento": "2000-01-01",
            "stack": ["locust"]
        }
        self.client.post("/pessoas", json=pessoa_data, name="/pessoas")

    @task(3)
    def get_pessoas(self):
        self.client.get("/pessoas", name="/pessoas")

    @task(2)
    def update_pessoa(self):
        pessoa_data = {
            "apelido": "test",
            "nome": "Updated Test User",
            "nascimento": "2000-01-01",
            "stack": ["locust", "update"]
        }
        self.client.put("/pessoas/test", json=pessoa_data, name="/pessoas/{id}")

    @task(1)
    def delete_pessoa(self):
        self.client.delete("/pessoas/test", name="/pessoas/{id}")
