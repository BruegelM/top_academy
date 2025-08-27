class Man:
    def input_data(self, birth: str, country: str, city: str, adress: str) -> None:
        self.__birth = birth
        self.__country = country
        self.__city = city
        self.__adress = adress

    def get_birth(self, birth: str) -> str:
        return self.__birth
    def get_country(self, coutry: str) -> str:
        return self.__country
    def get_city(self, city: str) -> str:
        return self.__city
    def get_adress(self) -> str:
        return self.__adress

    def __repr__(self):
        try:
            return f"Birth: {self.__birth}, Country: {self.__country}, City: {self.__city}, Adress: {self.__adress}"
        except:
            return "Data responce failed"

        
m = Man()
m.input_data("14.03.1986", "Russia", "Moscow", "Kolotushkina 6")

print(m)



from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8080)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.server_forever()
    except KeyboardInterrupt:
        httpd.server_close()