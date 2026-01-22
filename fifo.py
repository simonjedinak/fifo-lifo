class Fifo:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("Kapacita musí byť väčšia ako 0")
        self._capacity = capacity
        self.buffer = [None] * capacity
        self.head = 0
        self.tail = 0

    def put(self, data):
        self.buffer[self.tail] = data
        self.tail = (self.tail + 1) % self._capacity

    def get(self):
        if self.length() == 0:
            raise IndexError("FIFO je prázdne")

        data = self.buffer[self.head]
        self.buffer[self.head] = None
        self.head = (self.head + 1) % self._capacity
        return data

    def length(self):
        if self.tail >= self.head:
            return self.tail - self.head
        return self._capacity - (self.head - self.tail)

    def __str__(self):
        return f"FIFO(head={self.head}, tail={self.tail}, buffer={self.buffer})"
