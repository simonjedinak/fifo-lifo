class Lifo:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("Kapacita musí byť väčšia ako 0")
        self._capacity = capacity
        # Inicializácia poľa s fixnou veľkosťou (v Pythone zoznam, ale simulujeme pole)
        self._LIFO = [None] * capacity
        self.clear()

    # Gettery
    @property
    def top(self):
        return self._top

    @property
    def capacity(self):
        return self._capacity

    def push(self, data):
        """Pridáva nové dáta do LIFO."""
        if self._top >= self._capacity:
            raise IndexError("LIFO je plné (Stack overflow)")
        
        self._LIFO[self._top] = data
        self._top += 1

    def pop(self):
        """Vyberie z LIFO dáta, ktoré sú na rade."""
        if self._top == 0:
            raise IndexError("LIFO je prázdne (Stack underflow)")
        
        self._top -= 1
        data = self._LIFO[self._top]
        self._LIFO[self._top] = None # Vyčistenie referencie (voliteľné)
        return data

    def freeCap(self):
        """Vráti voľnú kapacitu LIFO."""
        return self._capacity - self._top

    def clear(self):
        """Nastaví top na nulu."""
        self._top = 0
        # V reálnom poli by sme nemuseli nulovať hodnoty, ale pre čistotu:
        # self._LIFO = [None] * self._capacity 

    def getLength(self):
        """Pomocná metóda pre kompatibilitu (nie je v zadaní, ale hodí sa)."""
        return self._top

    def __str__(self):
        """Vráti kompletnú štruktúru všetkých dát LIFO ako reťazec."""
        return f"LIFO(top={self._top}, capacity={self._capacity}, items={self._LIFO})"

    def see(self):
        """Vráti všetky aktuálne hodnoty LIFO počnúc hodnotou, ktorá je na rade."""
        # Od vrchu dole (LIFO poradie)
        items = []
        for i in range(self._top - 1, -1, -1):
            items.append(str(self._LIFO[i]))
        return ", ".join(items)
