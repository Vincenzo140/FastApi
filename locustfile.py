from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task(10)
    def home(self):
        self.client.get("/", name="/home")

    @task(5)
    def io_task(self):
        self.client.get("/io_task", name="/io_task")

    @task(5)
    def cpu_task(self):
        self.client.get("/cpu_task", name="/cpu_task")

    @task(3)
    def random_sleep(self):
        self.client.get("/data", name="/data")    

    @task(10)
    def random_status(self):
        self.client.get("/cpu", name="/cpu")

    @task(3)
    def chain(self):
        self.client.get("/chain", name="/chain")

    @task()
    def random_sleep(self):
      self.client.get("/ram", name="/ram")