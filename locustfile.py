from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task(10)
    def home(self):
        self.client.get("/", name="/home")

    @task(5)
    def io_task(self):
        self.client.get("/uptime", name="/uptime")

    @task(5)
    def cpu_task(self):
        self.client.get("/disk", name="/disk")

    @task(3)
    def random_sleep(self):
        self.client.get("/network", name="/network")    

    @task(3)
    def chain(self):
        self.client.get("/chain", name="/chain")
