import pandas as pd
import socket
import json
import io
import re

class TelnetCommands:
    def __init__(self, lista: list):
        self.lista = lista
    def dataframe_generics(self):
            if len(self.lista) == 1:
                return self.dataframe_version()
            else:
                return self.convertDataframe()
      
    def dataFrame_arp(self):
        # Copie e cole a saída do comando arp aqui
        arp_output = """
            login: admin
            Password: 


            BusyBox v1.12.4 (2020-07-10 11:12:47 CST) built-in shell (ash)
            Enter 'help' for a list of built-in commands.

            # arp -n -v
            Address                 HWtype  HWaddress           Flags Mask            Iface
            192.168.1.4             ether   a0:92:08:81:ff:e6   C                     br0
            192.168.1.240           ether   d4:f5:47:1a:bf:3a   C                     br0
            192.168.1.252           ether   50:3e:aa:77:51:88   C                     br0
            192.168.1.7             ether   60:fb:00:fc:01:e3   C                     br0
            192.168.1.3             ether   b8:06:0d:c8:8a:f9   C                     br0
            192.168.1.241           ether   3e:e7:05:a9:7f:84   C                     br0
            192.168.1.242           ether   00:e6:99:00:0d:ec   C                     br0
            192.168.1.8             ether   60:fb:00:fc:02:34   C                     br0
            192.168.1.5             ether   38:a5:c9:25:b1:c3   C                     br0
            192.168.1.9             ether   80:d2:1d:2c:ce:3a   C                     br0
            192.168.1.6             ether   50:8b:b9:6a:a8:9f   C                     br0
            192.168.1.250           ether   08:60:6e:84:6c:5b   C                     br0
            Entries: 12     Skipped: 0      Found: 12
            #
        """
        # Encontrar o índice da linha que contém os cabeçalhos da tabela ARP
        # Esta linha é identificada por começar com 'Address'
        lines = self.lista[0].strip().split('\n')
        start_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('Address'):
                start_index = i
                break

        if start_index != -1:
            # Coletar as linhas da tabela ARP (cabeçalho + dados)
            # Ignorar a linha de resumo 'Entries: ...'
            arp_table_lines = lines[start_index:-1] # -1 para remover a última linha de resumo

            # Juntar as linhas novamente em uma única string
            arp_table_string = "\n".join(arp_table_lines)

            # Usar io.StringIO para tratar a string como um arquivo e pd.read_csv para parsear
            df = pd.read_csv(io.StringIO(arp_table_string), sep=r'\s+', skipfooter=1, engine='python')    

            # Cria um novo DataFrame apenas com 'Address' e 'HWaddress'
            df_selected = df[['Address', 'HWaddress']]
            #print("✅ DataFrame criado com sucesso:")
            #print(df_selected)
            return df_selected
           
        else:
            print(f"❌ Não foi possível encontrar a tabela ARP na saída fornecida.")

    def dataFrame_hosts(self):
        hosts_data = """
            login: admin
            Password: 


            BusyBox v1.12.4 (2020-07-10 11:12:47 CST) built-in shell (ash)
            Enter 'help' for a list of built-in commands.

            # cat /tmp/hosts
            192.168.1.240   Google-Nest-Mini.meuintelbras.local Google-Nest-Mini
            192.168.1.252   Servidor-LNX.meuintelbras.local Servidor-LNX
            192.168.1.6     wlan0.meuintelbras.local wlan0
            192.168.1.4     wlan0.meuintelbras.local wlan0
            192.168.1.5     wlan0.meuintelbras.local wlan0
            192.168.1.3     wlan0.meuintelbras.local wlan0
            192.168.1.1     ONT121W.meuintelbras.local ONT121W
            192.168.1.242   raspberrypi.meuintelbras.local raspberrypi
            192.168.1.241   S24-FE-de-Lucas.meuintelbras.local S24-FE-de-Lucas
            192.168.1.250   DESKTOP-M8JU6A9.meuintelbras.local DESKTOP-M8JU6A9
            192.168.1.9     Chromecast.meuintelbras.local Chromecast
            # 
        """
        
        # Encontra o ponto de início dos dados desejados
        start_marker = "cat /tmp/hosts"
        start_index = self.lista[1].find(start_marker)

        # Verifica se o marcador foi encontrado
        if start_index != -1:
            # Extrai a parte relevante da string,
            # descartando tudo antes de "cat /tmp/hosts"
            relevant_string = self.lista[1][start_index + len(start_marker):].strip()

            # Usa io.StringIO para tratar a string como um objeto tipo arquivo
            data_io = io.StringIO(relevant_string)

            # Lê os dados em um DataFrame pandas
            # Assumimos que os dados são separados por espaços e não têm cabeçalho
            df = pd.read_csv(data_io, sep=r'\s+', header=None, names=['Address', 'Local', 'Short Hostname'])
            # Adição para remover linhas com NaN 
            # Remove qualquer linha onde pelo menos um valor seja NaN
            df = df.dropna()

            #print("✅ DataFrame criado com sucesso:")
            #print(df)
            return df
        else:
            print(f"❌ O marcador '{start_marker}' não foi encontrado nos dados da string fornecida.")

    # --- Início do Processamento ---
    def convertDataframe(self):
    # 3. Fundir os dois DataFrames baseados no 'Address' (endereço IP)
        # Usamos um 'left merge' para manter todas as entradas do ARP e adicionar o hostname onde houver correspondência
        df_merged = pd.merge(self.dataFrame_arp(), self.dataFrame_hosts(), on='Address', how='left')

        # 4. Adicionar a coluna 'id'
        # O id será sequencial, começando de 1
        df_merged['id'] = df_merged.index + 1

        # 5. Adicionar a coluna 'Gateway'
        # Assumimos um gateway padrão; ajuste se o seu for diferente
        df_merged['Gateway'] = '192.168.1.1'
        ip = '192.168.1.1'
        # 6. Adicionar a coluna 'local'
        # Verifica se o endereço IP está na sub-rede 192.168.1.x
        #df_merged['Local'] = df_merged['Address'].apply(lambda x: x.startswith('192.168.1.'))
        df_merged['Local'] = df_merged['Address'].apply(lambda x: x.startswith(ip[:-1]))

        #print("Tentando resolver nomes de host para a coluna 'Hostname'. Isso pode levar alguns segundos, por favor, aguarde...\n")
        df_merged['Full Hostname (FQDN)'] = df_merged['Address'].apply(self.get_hostname)

        # 7. Selecionar e reordenar as colunas finais para a tabela
        df_final_table = df_merged[['id', 'Address', 'HWaddress', 'Gateway', 'Local', 'Short Hostname', 'Full Hostname (FQDN)']].copy()

        #print("\n--- New Hosts Table ---")
        jsonformomat = self.convertJson(df_final_table)
        return jsonformomat

    def get_hostname(self, ip_address):
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

    def convertJson(self, df_final_table):
        df_final_table['img'] = ""
        df_final_table['parent'] = [[] for _ in range(len(df_final_table))]

        # Assuming df_final_table is your DataFrame
        # 1. Get the current column names
        original_columns = df_final_table.columns

        # 2. Create new column names by removing spaces
        new_columns = [col.replace(' ', '') for col in original_columns]

        # 3. Assign the new column names back to the DataFrame
        df_final_table.columns = new_columns

        json_output = df_final_table.to_json(orient='records')
        #print(json_output)
        return json.loads(json_output)  

    # Convert DataFrame to JSON
    def dataframe_version(self):
        data = """
            login: admin
            Password: 


            BusyBox v1.12.4 (2020-07-10 11:12:47 CST) built-in shell (ash)
            Enter 'help' for a list of built-in commands.

            # show system version


            Model Number: ONT121W
            Build Date: Jul 10 2020 11:12:44
            Firmware Version: 1.0-200710
            MAC Address: D8:77:8B:A6:91:38
            SysUpTime: 0 2:51:54
            HW Serial Number: ITBS8BA69138
            ManufacturerOUI: D8778B
            Manufacturer: Realtek Semiconductor Corp.
            #
        """

        # 1. Isolar os dados relevantes
        # Encontra o índice da linha que contém '# show system version'
        lines = self.lista[0].strip().split('\n')
        start_parsing = False
        data_lines = []

        for line in lines:
            if '# show system version' in line:
                start_parsing = True
                continue # Pula a linha do comando em si
            
            if start_parsing and line.strip() != '': # Começa a coletar linhas não vazias após o comando
                data_lines.append(line.strip())

        # 2. Parsear cada linha em chave-valor
        parsed_data = {}
        for line in data_lines:
            if ':' in line:
                # Divide a linha no primeiro ':' para separar a chave do valor
                # Isso é importante para valores que podem conter ':' (ex: "Build Date: Jul 10 2020 11:12:44")
                key, value = line.split(':', 1) 
                
                # Remove espaços em branco da chave e, em seguida, remove TODOS os espaços
                # dentro da chave para formatar como "CamelCase" ou "NoSpaces"
                cleaned_key = key.strip().replace(" ", "") 
                
                # Armazena a chave limpa e o valor (com espaços em branco removidos) no dicionário
                parsed_data[cleaned_key] = value.strip()

        # 3. Criar o DataFrame
        # Para dados como este, onde há apenas uma "entrada" (um conjunto de características de um dispositivo),
        # o ideal é criar um DataFrame com uma única linha.
        df = pd.DataFrame([parsed_data])
        # Convert the dictionary to a JSON string
        json_output = json.dumps(parsed_data, indent=4)
        return json.loads(json_output)