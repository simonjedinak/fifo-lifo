class Lifo:
    top = 0
    stackSize = 0

    def __init__(self, stackSize):
        self.stackSize = stackSize
        self.stack = [] * self.stackSize

    def push(self, item):
        if len(self.stack) >= self.stackSize:
            raise IndexError("full LIFO")
        self.stack.append(item)
        self.top += 1

    def pop(self):
        if self.top > 0:
            self.top -= 1
            return self.stack.pop()
        else:
            raise IndexError("empty LIFO")

    def getLength(self):
        return len(self.stack)

    def __str__(self):
        return str(self.stack)