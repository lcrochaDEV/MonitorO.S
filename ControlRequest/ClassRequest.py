from Async.ClassAsync import AssyncExec
from ont121w.ont121w import Comands_Sends

class Rotas:

    @classmethod
    def methodGet(self, itens: list):
        try:
            return Comands_Sends.asyncFunctin(itens.host, itens.port, itens.user, itens.password, itens.commands)
            #START CLIENT
            return AssyncExec.asyncAction(
              Comands_Sends.send_telnet_command(itens.host, itens.port, itens.user, itens.password, itens.commands),
            )

        except:
            return 'Dado não encontrado.'

'''
    @classmethod
    def methodPostIdCli(self, itens: list):
        try:
            self.clearCache()
            ControlPath.data(itens.cache)
            return 'Dado cadastrado com sucesso.'
        except:
            return 'Erro de cadastro'
'''

'''    
    @classmethod
    def clearCache(self):
        try:
            ControlPath.delete_data()
            return 'Dado deletado com sucesso'
        except:
            return 'Erro ao deletar'
'''