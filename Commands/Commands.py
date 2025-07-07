from subprocess import check_output 

class Commands:

    @classmethod
    def cli(self, data):
       return check_output(data)