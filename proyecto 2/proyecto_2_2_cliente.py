# tunnel_client.py
import socket
import time
from cryptography.fernet import Fernet

class TunnelClient:
    def __init__(self, server_host='localhost', server_port=8080):
        self.server_host = server_host
        self.server_port = server_port
        self.cipher = None
    
    def set_key(self, key):
        self.cipher = Fernet(key)
    
    def send_message(self, message):
        if not self.cipher:
            raise ValueError("Clave de cifrado no establecida. Use set_key() primero.")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_host, self.server_port))
                print(f"Conectado al servidor {self.server_host}:{self.server_port}")
                
                encrypted_payload = self.cipher.encrypt(message.encode())
                print(f"[CLIENTE] Mensaje cifrado: {encrypted_payload[:50]}...")
                
                tunnel_packet = self.add_esp_header(encrypted_payload)
                print(f"[CLIENTE] Paquete con ESP: {tunnel_packet[:50]}...")
                
                client_socket.send(tunnel_packet)
                print(f"[CLIENTE] Mensaje enviado")
                
                response = client_socket.recv(1024)
                decrypted_response = self.cipher.decrypt(
                    self.remove_esp_header(response)
                )
                print(f"[CLIENTE] Respuesta del servidor: {decrypted_response.decode()}")
                
                return decrypted_response.decode()
                
        except ConnectionRefusedError:
            print("Error: No se pudo conectar al servidor")
        except Exception as e:
            print(f"Error en el cliente: {e}")
    
    def add_esp_header(self, data):
        esp_header = b"ESP_HEAD"
        return esp_header + data
    
    def remove_esp_header(self, data):
        return data[8:]

def main():
    client = TunnelClient()
    
    print("=== CLIENTE===")
    print("Por favor, ingrese la clave proporcionada por el servidor:")
    
    while True:
        try:
            # Solicitar clave al usuario
            key_input = input("Clave: ").strip()
            client.set_key(key_input.encode())

            msg = str(input("Ingrese un mensaje: "))

            response = client.send_message(msg)
            time.sleep(2)  # Pausa entre mensajes
             
            print(f"Respuesta del servidor: {response}")

        except KeyboardInterrupt:
            print("\nCliente terminado por el usuario")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()