import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  vus: 100, 
  duration: '30s', 
};

export default function () {
  var server_list = ["localhost:8000", "localhost:8001", "localhost:8007"]
  var endpoint_list = ["/", "/cpu", "/desculpas", "/dados_invalidos"]
  server_list.forEach(function(server) {
    endpoint_list.forEach(function(endpoint) {
      http.get("http://" + server + endpoint);
    });
  });
  sleep(0.5);
}