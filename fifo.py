from typing import override


class Fifo:
    head = 0
    tail = 0

    def __init__(self, bufferSize):
        self.bufferSize = bufferSize
        self.buffer = [] * self.bufferSize


    def put(self, item):
        if len(self.buffer) < self.bufferSize:
            self.buffer.append(item)
            self.tail += 1
        else:
            raise IndexError("full FIFO")

    def get(self):
        if self.head < len(self.buffer):
            item = self.buffer[self.head]
            self.head += 1
            return item
        else:
            raise IndexError("empty FIFO")

    def getLength(self):
        return len(self.buffer) - self.head

    @override
    def __str__(self):
        return str(self.buffer[self.head:])
    def raw(self):
        return self.buffer


if __name__ == "__main__":
    fifo = Fifo(4)
    fifo.put(1)
    fifo.put(2)
    fifo.put(3)
    print(fifo.get())  # Output: 1
    print(fifo.get())  # Output: 2
    fifo.put(4)
    print(fifo)
    print(fifo.get())  # Output: 3
    print(fifo.get())  # Output: 4
    print(fifo)        # Output: []