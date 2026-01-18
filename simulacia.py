from fifo import Fifo

'''
Naprogramujte v jednom z jazykov Python alebo Java aplikáciu simulujúcu pomocou FIFO rad kupujúcich, čakajúcich pri pokladni na zaplatenie.
• Váš program využíva pre evidenciu kupujúcich v rade štruktúru FIFO.
• model simulácie pohybu ľudí v obchode bude používať nasledujúce pravidlá
• Kupujúci s poradovým číslom i prichádza do obchodu v čase Ti = Ti-1 + 5 + random(25+P.Č.) sekúnd, kde
Ti-1 je čas príchodu predošlého kupujúceho, na začiatku 0 sekúnd
P.Č. je Vaše poradové číslo v triednej knihe
• Kupujúci i sa v obchode zdrží nakupovaním Tn = 1 + random(10+P.Č.) minút
• Jeho nákup sa pri pokladni spracuje za Tp = 0.3 + Tn/20 minút
• Evidujte ľudí v zoradenom zozname s časovými údajmi
• kedy má skončiť nakupovanie a postaviť sa do radu pri pokladni
• ako dlho sa bude jeho nákup spracovávať pri pokladni
• V správnom čase zaraďte kupujúceho do radu pri pokladni (FIFO)
• Pri každej zmene vo FIFO vypíšte
• Vždy aktuálny čas, aktuálna dĺžka radu, súhrnná doba nečinnosti pokladne
• Pri príchode do radu, ktorý kupujúci prišiel do radu (jeho poradové číslo i, čas príchodu do obchodu, čas nakupovania, čas spracovania nákupu),
• Po zaplatení poradové číslo kupujúceho, ktorý odišiel a ako dlho stál v rade
• Maximálnu dobu čakania v rade pri pokladni, keď sa zmení, maximálnu dĺžku radu, keď sa zmení
• Simuláciu spúšťajte zrýchlene (každý časový údaj /100)
• Po prvom zaplnení obrazovky výpismi a na konci simulácie 8 hodinovej otváracej doby urobte screenshot obrazovky a pripojte ich do riešiteľskej dokumentácie
• Simuláciu spustite 5x a výsledky zapíšte do tabuľky do stĺpcov (celkový počet ľudí v obchode, max. dĺžka čakania v rade pri pokladni, max. dĺžka radu pri pokladni,
max. doba nečinnosti pokladne)
'''

import random

class Customer:
    def __init__(self, id, arrival_time, shopping_time, processing_time):
        self.id = id
        self.arrival_time = arrival_time
        self.shopping_time = shopping_time
        self.processing_time = processing_time
        self.queue_entry_time = None
        self.queue_exit_time = None
    def wait_time(self):
        if self.queue_entry_time is not None and self.queue_exit_time is not None:
            return self.queue_exit_time - self.queue_entry_time
        return 0
    def __str__(self):
        return f"Customer {self.id} (Arrival: {self.arrival_time}, Shopping: {self.shopping_time}, Processing: {self.processing_time})"
class Simulation:
    def __init__(self):
        self.p_cislo = 11
        self.customers = []
        self.queue = Fifo(5000)
        self.current_time = 0
        self.next_arrival_time = 0
        self.next_processing_end_time = float('inf')
        self.total_idle_time = 0
        self.max_wait_time = 0
        self.max_queue_length = 0
        self.last_event_time = 0

    def run(self, duration=28800):
        customer_id = 1
        while self.current_time < duration:
            if self.current_time >= self.next_arrival_time:
                shopping_time = 60 * (1 + random.randint(0, 10 + self.p_cislo))
                processing_time = 0.3 * 60 + shopping_time / 20
                customer = Customer(customer_id, self.current_time, shopping_time, processing_time)
                self.customers.append(customer)
                customer_id += 1
                self.next_arrival_time += 5 + random.randint(0, 25 + self.p_cislo)

            if (not self.queue.getLength()) and (self.current_time >= self.next_processing_end_time):
                if self.queue.getLength() > 0:
                    next_customer = self.queue.get()
                    next_customer.queue_exit_time = self.current_time
                    wait_time = next_customer.wait_time()
                    self.max_wait_time = max(self.max_wait_time, wait_time)
                    print(f"Time {self.current_time/100:.2f}s: Customer {next_customer.id} finished checkout after waiting {wait_time/100:.2f}s")
                    self.next_processing_end_time = self.current_time + next_customer.processing_time

            for customer in self.customers:
                if customer.queue_entry_time is None and self.current_time >= customer.arrival_time + customer.shopping_time:
                    customer.queue_entry_time = self.current_time
                    self.queue.put(customer)
                    print(f"Time {self.current_time/100:.2f}s: Customer {customer.id} entered queue")
                    if self.queue.getLength() > self.max_queue_length:
                        self.max_queue_length = self.queue.getLength()

            if self.queue.getLength() == 0:
                idle_duration = self.current_time - self.last_event_time
                if idle_duration > 0:
                    self.total_idle_time += idle_duration
            self.last_event_time = self.current_time
            self.current_time += 1

        print(f"Simulation ended. Total customers: {len(self.customers)}, Max wait time: {self.max_wait_time/100:.2f}s, Max queue length: {self.max_queue_length}, Total idle time: {self.total_idle_time/100:.2f}s")
if __name__ == "__main__":
    sim = Simulation()
    sim.run()