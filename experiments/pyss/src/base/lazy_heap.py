import heapq
import simple_heap
class Heap(simple_heap.Heap):
    """
    Like the simple heap, but append instead of heappush on push (constant
    time) and lazily heapify on pop
    """
    def _push_breaking_heap(self, item):
        self.pop = self._pop_broken_heap
        self.push = self._push_broken_heap
        self._push_broken_heap(item)

    def _push_broken_heap(self, item):
        self.contents.append(item)

    def _pop_legal_heap(self):
        return heapq.heappop(self.contents)
    def _pop_broken_heap(self):
        heapq.heapify(self.contents)
        self.pop = self._pop_legal_heap
        return self._pop_legal_heap()

    push = _push_broken_heap
    pop = _pop_broken_heap
