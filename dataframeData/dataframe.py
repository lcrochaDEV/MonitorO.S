import pandas as pd
import socket
import json

# Dados de entrada: Saída do comando 'arp -n -v'
arp_output = """
Address              HWtype  HWaddress           Flags Mask          Iface
192.168.1.4          ether   50:8b:b9:6a:a8:9f   C                   br0
192.168.1.5          ether   a0:92:08:81:ff:e6   C                   br0
192.168.1.7          ether   60:fb:00:fc:01:e3   C                   br0
192.168.1.240        ether   d4:f5:47:1a:bf:3a   C                   br0
192.168.1.250        ether   08:60:6e:84:6c:5b   C                   br0
192.168.1.3          ether   b8:06:0d:c8:8a:f9   C                   br0
192.168.1.242        ether   00:e6:99:00:0d:ec   C                   br0
192.168.1.252        ether   50:3e:aa:77:51:88   C                   br0
192.168.1.8          ether   60:fb:00:fc:02:34   C                   br0
192.168.1.6          ether   38:a5:c9:25:b1:c3   C                   br0
Entries: 10     Skipped: 0      Found: 10
"""

# Dados de entrada: Saída do comando 'cat /tmp/hosts'
hostname_data_str = """
192.168.1.240   Google-Nest-Mini.meuintelbras.local Google-Nest-Mini
192.168.1.242   raspberrypi.meuintelbras.local raspberrypi
192.168.1.3     wlan0.meuintelbras.local wlan0
192.168.1.5     wlan0.meuintelbras.local wlan0
192.168.1.4     wlan0.meuintelbras.local wlan0
192.168.1.6     wlan0.meuintelbras.local wlan0
192.168.1.252   Servidor-LNX.meuintelbras.local Servidor-LNX
192.168.1.250   DESKTOP-M8JU6A9.meuintelbras.local DESKTOP-M8JU6A9
192.168.1.1     ONT121W.meuintelbras.local ONT121W
192.168.1.241   S24-FE-de-Lucas.meuintelbras.local S24-FE-de-Lucas
"""

# --- Início do Processamento ---
def convertDataframe():
    # 1. Parsear a saída do ARP para um DataFrame inicial (df_arp)
    lines_arp = arp_output.strip().split('\n')
    # Ignoramos a linha de cabeçalho e a linha de resumo do ARP
    data_lines_arp = lines_arp[1:-1]
    parsed_arp_data = []
    for line in data_lines_arp:
        parts = line.split()
        if len(parts) >= 5: # Garante que temos os campos esperados
            parsed_arp_data.append({
                'Address': parts[0],
                'HWaddress': parts[2] # Extraímos apenas Address e HWaddress daqui
            })
    df_arp = pd.DataFrame(parsed_arp_data)

    # 2. Parsear os dados de hostname para outro DataFrame (df_hostnames)
    lines_hostname = hostname_data_str.strip().split('\n')
    parsed_hostname_data = []
    for line in lines_hostname:
        parts = line.split()
        if len(parts) == 3: # Esperamos 3 partes: IP, FQDN, Short Name
            parsed_hostname_data.append({
                'Address': parts[0], # Renomeamos para 'Address' para facilitar a fusão
                'Short Hostname': parts[2]
            })
    df_hostnames = pd.DataFrame(parsed_hostname_data)

    # 3. Fundir os dois DataFrames baseados no 'Address' (endereço IP)
    # Usamos um 'left merge' para manter todas as entradas do ARP e adicionar o hostname onde houver correspondência
    df_merged = pd.merge(df_arp, df_hostnames, on='Address', how='left')

    # 4. Adicionar a coluna 'id'
    # O id será sequencial, começando de 1
    df_merged['id'] = df_merged.index + 1

    # 5. Adicionar a coluna 'Gateway'
    # Assumimos um gateway padrão; ajuste se o seu for diferente
    df_merged['Gateway'] = '192.168.1.1'

    # 6. Adicionar a coluna 'local'
    # Verifica se o endereço IP está na sub-rede 192.168.1.x
    df_merged['local'] = df_merged['Address'].apply(lambda x: x.startswith('192.168.1.'))

    print("Tentando resolver nomes de host para a coluna 'Hostname'. Isso pode levar alguns segundos, por favor, aguarde...\n")
    df_merged['Full Hostname (FQDN)'] = df_merged['Address'].apply(get_hostname)

    # 7. Selecionar e reordenar as colunas finais para a tabela
    df_final_table = df_merged[['id', 'Address', 'HWaddress', 'Gateway', 'local', 'Short Hostname', 'Full Hostname (FQDN)']].copy()

    print("\n--- New Hosts Table ---")
    print(df_final_table)
    convertJson(df_final_table)
    # --- Fim do Processamento ---

def get_hostname(ip_address):
    """Tenta obter o nome do host para um IP, com tratamento de erros."""
    try:
        socket.setdefaulttimeout(1) # Timeout de 1 segundo por tentativa.
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except socket.herror:
        return "Desconhecido" # Host não pode ser resolvido.
    except socket.timeout:
        return "Timeout" # Tempo limite atingido.
    except Exception as e:
        return f"Erro: {e}" # Captura qualquer outro erro inesperado.

def convertJson(df_final_table):
    # Converte o DataFrame para uma lista de dicionários
    list_of_dicts = df_final_table.to_dict(orient='records')

    # Adiciona a chave 'img' com valor vazio a cada dicionário na lista
    for item in list_of_dicts:
        item['img'] = ""

    # Converte a lista de dicionários para uma string JSON
    json_output = json.dumps(list_of_dicts, indent=2, ensure_ascii=False)

    # Mostrar o JSON gerado
    print("\n--- JSON da Tabela de Dispositivos de Rede (com 'img' na SAÍDA JSON) ---")
    print(json_output)
