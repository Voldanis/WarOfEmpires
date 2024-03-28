class Road:
    def __init__(self, start_village, finish_village):
        self.start_village = start_village
        self.finish_village = finish_village
        self.length = 0
        self.segments = []

    def init_length(self, length):
        self.length = length
        self.segments = []
        for _ in range(length):
            self.segments.append([])

    def __str__(self):
        return self.start_village, self.length
