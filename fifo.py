class Fifo:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("Kapacita musí byť väčšia ako 0")
        self._capacity = capacity
        # Inicializácia poľa
        self._FIFO = [None] * capacity
        self.clear()

    # Gettery
    @property
    def head(self):
        return self._head

    @property
    def tail(self):
        return self._tail

    @property
    def capacity(self):
        return self._capacity
    
    @property
    def fullHouse(self):
        return self._fullHouse

    def append(self, data): # v zadaní je append namiesto put
        """Pridáva nové dáta do FIFO."""
        if self._fullHouse:
            raise IndexError("FIFO je plné")
        
        self._FIFO[self._tail] = data
        self._tail = (self._tail + 1) % self._capacity
        
        if self._tail == self._head:
            self._fullHouse = True

    # Alias pre kompatibilitu ak by niekto volal put
    def put(self, data):
        self.append(data)

    def get(self):
        """Vyberie z FIFO dáta, ktoré sú na rade."""
        if self.getLength() == 0:
             raise IndexError("FIFO je prázdne")
        
        data = self._FIFO[self._head]
        self._FIFO[self._head] = None # Voliteľné čistenie
        self._head = (self._head + 1) % self._capacity
        self._fullHouse = False
        return data

    def freeCap(self):
        """Vráti voľnú kapacitu FIFO."""
        if self._fullHouse:
            return 0
        if self._tail >= self._head:
            return self._capacity - (self._tail - self._head)
        else:
            return self._head - self._tail

    def clear(self):
        """Nastaví head a tail na nulu."""
        self._head = 0
        self._tail = 0
        self._fullHouse = False
        # self._FIFO = [None] * self._capacity

    def getLength(self):
        if self._fullHouse:
            return self._capacity
        if self._tail >= self._head:
            return self._tail - self._head
        return self._capacity - (self._head - self._tail)

    def __str__(self):
        """Vráti kompletnú štruktúru všetkých dát FIFO ako reťazec."""
        return f"FIFO(head={self._head}, tail={self._tail}, full={self._fullHouse}, items={self._FIFO})"
    
    def see(self):
        """Vráti všetky aktuálne hodnoty FIFO počnúc hodnotou, ktorá je na rade."""
        items = []
        count = self.getLength()
        curr = self._head
        for _ in range(count):
            items.append(str(self._FIFO[curr]))
            curr = (curr + 1) % self._capacity
        return ", ".join(items)

if __name__ == "__main__":
    # Rýchly test funkčnosti
    fifo = Fifo(4)
    fifo.append(1)
    fifo.append(2)
    fifo.append(3)
    print(f"See: {fifo.see()}")
    print(f"Get: {fifo.get()}") # 1
    fifo.append(4)
    fifo.append(5) # Full
    try:
        fifo.append(6)
    except IndexError as e:
        print(f"Chyba: {e}")
    print(f"FullHouse: {fifo.fullHouse}")
    print(f"Get: {fifo.get()}") # 2
    print(f"See: {fifo.see()}") # 3, 4, 5
