import asyncio
import telnetlib3
from frameData.dataframe import TelnetCommands

async def send_telnet_command(host: str = '192.168.1.1', port: int = 23, user: str = 'admin', password: str = 'intelbras', commands: list = None):
    try:
        reader, writer = await telnetlib3.open_connection(host, port)
        print(f"Connected to {host}:{port}")

        if user and password:
            writer.write(f'{user}\n')
            await writer.drain()
            await asyncio.sleep(0.1)
            writer.write(f'{password}\n')
            await writer.drain()
            await asyncio.sleep(0.1)

        # Envia um ou mais comandos de uma lista
        lista: str = []
        if len(commands) == 1:
            writer.write(f'{commands[0]}\r\n')  # Envia o comando e um newline
            await writer.drain()
            await asyncio.sleep(0.1)
            # Read response (adjust buffer size as needed)
            response = await reader.read(2048)
            if response != '':
                print(f"Received response:\n{response}")
                #versionDataframe(dataframe=response)      
                pass    
        else:
            for command in commands:
                writer.write(f'{command}\r\n')  # Envia o comando e um newline
                await writer.drain()
                await asyncio.sleep(0.1)
                # Read response (adjust buffer size as needed)
                response = await reader.read(2048)
                if response != '':
                    #print(f"Received response:\n{response}") 
                    lista.append(response)    
        
        commandsTelnet = TelnetCommands(commadsMult=lista)
        writer.close()
        print("Connection closed.")
        return commandsTelnet.convertDataframe()
    except ConnectionRefusedError:
        print(f"Erro: Conexão recusada pelo host {host}:{port}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

async def asyncFunctin(HOST, PORT, USER, PASSWORD, COMMANDS):
    return 'oi'
    asyncio.run(send_telnet_command(HOST, PORT, USER, PASSWORD, COMMANDS))
'''
if __name__ == "__main__":
    # Replace with your Telnet server's host and port
    HOST = '192.168.1.1'
    PORT = 23 
    USER = 'admin'
    PASSWORD = 'intelbras'
    COMMANDS = [
        "arp -n -v",
        "cat /tmp/hosts",
    ]

    asyncio.run(send_telnet_command(HOST, PORT, USER, PASSWORD, COMMANDS))

'''

# "show system version",
# "cat /tmp/hosts",
# "arp -n -v",