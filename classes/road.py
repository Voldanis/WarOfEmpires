class Road:
    def __init__(self, start_town, finish_town):
        self.start_town = start_town
        self.finish_town = finish_town
        self.length = 0
        self.segments = []

    def init_length(self, length):
        self.length = length
        self.segments = []
        for _ in range(length):
            self.segments.append([])


