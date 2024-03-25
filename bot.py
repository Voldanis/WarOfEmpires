from example import Example


class Bot(Example):
    def move(self, response: dict):
        if response['status_kode'] == 1:
            return 'upgrade', 'v3'
        else:
            return 'end'
