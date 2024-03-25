from bots.example import Example


class Bot(Example):
    def move(self, response: dict):
        if response['status_kode'] == 104 or response['status_kode'] == 105:
            return 'end'
        else:
            return 'equip', 'v3'
