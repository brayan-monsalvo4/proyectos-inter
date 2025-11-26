# tunnel_server.py
import socket
import threading
from cryptography.fernet import Fernet, InvalidToken

class TunnelServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        print(f"Servidor iniciado. Clave de cifrado: {self.key.decode()}")
    
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"Servidor escuchando en {self.host}:{self.port}")
            print("Esperando conexiones de clientes...")
            
            while True:
                client_socket, addr = server_socket.accept()
                print(f"\n=== Conexión establecida desde {addr} ===")
                
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, addr)
                )
                client_thread.start()
    
    def handle_client(self, client_socket, addr):
        try:
            while True:
                encrypted_data = client_socket.recv(1024)
                if not encrypted_data:
                    print(f"Conexión cerrada por {addr}")
                    break
                
                print(f"\n[SERVIDOR] Datos recibidos (cifrados): {encrypted_data[:50]}...")
                
                payload = self.remove_esp_header(encrypted_data)
                print(f"[SERVIDOR] Payload después de remover el ESP: {payload[:50]}...")
                
                decrypted_message = self.cipher.decrypt(payload)
                print(f"[SERVIDOR] Mensaje descifrado: {decrypted_message.decode()}")
                
                response = f"[SERVIDOR] *Servidor recibió*: {decrypted_message.decode()}"
                encrypted_response = self.add_esp_header(
                    self.cipher.encrypt(response.encode())
                )
                client_socket.send(encrypted_response)
                print(f"[SERVIDOR] Respuesta enviada al cliente")
        except InvalidToken as token:
            print(f"Error en la clave: las claves no coinciden. {token}")
        except Exception as e:
            print(f"Error en manejo de cliente {addr}: {e}")
        finally:
            client_socket.close()
            print(f"Conexion con {addr} cerrada")
    
    def remove_esp_header(self, data):
        return data[8:]
    
    def add_esp_header(self, data):
        esp_header = b"ESP_HEAD"
        return esp_header + data

    def get_key(self):
        return self.key

if __name__ == "__main__":
    server = TunnelServer()
    print("=== INICIANDO SERVIDOR===")
    print("Clave del servidor:", server.get_key().decode())
    server.start()