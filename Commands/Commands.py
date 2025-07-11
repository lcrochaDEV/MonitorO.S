from subprocess import check_output 
import telnetlib
import socket
import time

class Commands:

    @classmethod
    def cli(self, data):
       return check_output(data)
    
    @classmethod
    def telnetCommands(self):
        HOST = "192.168.1.242"
        PORT = 23  # Default Telnet port

        try:
            # Cria uma instância da conexão Telnet
            tn = telnetlib.Telnet(HOST, PORT)

            # Recebe a resposta inicial do servidor (ex: prompt de login)
            print(tn.read_until(b"login: ").decode('ascii'))
            tn.write(b"pi\n") # Substitua pelo nome de usuário
            print(tn.read_until(b"Password: ").decode('ascii'))
            tn.write(b"raspberry\n") # Substitua pela senha
            
            # Aguarda um tempo para o servidor responder
            time.sleep(1)

            # Recebe a resposta do servidor após o login
            print(tn.read_very_eager().decode('ascii'))
            
            # Envia um comando
            tn.write(b"show version\n")
            time.sleep(1)

            # Recebe a resposta do comando
            output = tn.read_very_eager().decode('ascii')
            print(output)

            # Encerra a conexão
            tn.close()

        except socket.error as e:
            print(f"Erro de conexão: {e}")
        except Exception as e:
            print(f"Erro: {e}")