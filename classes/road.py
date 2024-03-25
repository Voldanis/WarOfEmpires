class Road:
    def __init__(self, connected_villages: set):
        self.connected_villages = connected_villages
        self.length = 0

    def __str__(self):
        return self.connected_villages, self.length
