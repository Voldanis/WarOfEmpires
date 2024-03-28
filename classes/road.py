class Road:
    def __init__(self, start_village, finish_village):
        self.start_village = start_village
        self.finish_village = finish_village
        self.length = 0
        self.segments = []

    def __str__(self):
        return self.start_village, self.length

    def init_length(self, length):
        self.length = length
        self.segments = []
        for _ in range(length):
            self.segments.append([])

    def copy_segments(self):
        copy_segments = []
        for segment in self.segments:
            copy_segments.append(segment.copy())
        return copy_segments

