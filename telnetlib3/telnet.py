import asyncio
import dataframeData
from dataframeData.dataframe import convertDataframe

async def send_telnet_command(host: str, port: int, user: str, password: str, commands: str):
    try:
        reader, writer = await dataframeData.open_connection(host, port)
        print(f"Connected to {host}:{port}")

        if user and password:
            writer.write(f'{user}\n')
            await writer.drain()
            await asyncio.sleep(0.1)
            writer.write(f'{password}\n')
            await writer.drain()
            await asyncio.sleep(0.1)
        
        # Comando executado no host
        for command in commands:
            writer.write(f'{command}\r\n')  # Envia o comando e um newline
            await writer.drain()
            await asyncio.sleep(0.1)


        # Read response (adjust buffer size as needed)
        response = await reader.read(2048)
        if response != '':
            print(f"Received response:\n{response}")
            convertDataframe(data=response)
            
        writer.close()
        print("Connection closed.")
    except ConnectionRefusedError:
        print(f"Erro: Conexão recusada pelo host {host}:{port}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    # Replace with your Telnet server's host and port
    HOST = '192.168.1.1'
    PORT = 23 
    USER = 'admin'
    PASSWORD = 'intelbras'
    COMMANDS = [
       "cat /tmp/hosts"
    ]

    asyncio.run(send_telnet_command(HOST, PORT, USER, PASSWORD, COMMANDS))


# "show system version"
# "cat /tmp/hosts",
# "arp -n -v",