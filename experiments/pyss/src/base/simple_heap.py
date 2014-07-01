import heapq
class Heap(object):
    def __init__(self):
        self.contents = []

    def push(self, item):
        heapq.heappush(self.contents, item)

    def pop(self):
        return heapq.heappop(self.contents)

    def remove(self, item):
        # warning: inefficient, O(n)
        self.contents.remove(item)
        heapq.heapify(self.contents)

    def __len__(self):
        return len(self.contents)

    def __contains__(self, item):
        return item in self.contents

    def __iter__(self):
        return iter(self.contents)
