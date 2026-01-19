from fifo import Fifo
import random
import time

'''
Zadanie:
• Simultánie 8 hodinovej otváracej doby.
• 5 opakovaní simulácie -> výstup do tabuľky.
• Zrýchlenie času / 100.
• Pravidlá časov:
    P.Č. = 11
    Príchod Ti = Ti-1 + 5 + random(25 + P.Č.) [sekúnd]
    Nakupovanie Tn = 1 + random(10 + P.Č.) [minút]
    Spracovanie Tp = 0.3 + Tn / 20 [minút]
'''

P_CISLO = 11

def format_time(seconds):
    """Pomocná funkcia na formátovanie času (HH:MM:SS) od začiatku (0s = 08:00:00)."""
    # Predpokladáme, že 0s je otvorenie obchodu
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

class Customer:
    def __init__(self, id, arrival_time):
        self.id = id
        self.arrival_time = arrival_time
        # Doba nakupovania v sekundách
        # Tn = 1 + random(10 + P.Č.) minút
        self.shopping_duration_min = 1 + random.randint(0, 10 + P_CISLO)
        self.shopping_duration_sec = self.shopping_duration_min * 60
        
        # Čas kedy sa postaví do radu
        self.queue_entry_time = self.arrival_time + self.shopping_duration_sec
        
        # Doba spracovania v sekundách
        # Tp = 0.3 + Tn / 20 minút
        self.processing_duration_min = 0.3 + (self.shopping_duration_min / 20.0)
        self.processing_duration_sec = self.processing_duration_min * 60
        
        self.start_service_time = None
        self.end_service_time = None

    def __str__(self):
        return (f"Zákazník {self.id}: Príchod={format_time(self.arrival_time)}, "
                f"Nakupovanie={self.shopping_duration_min} min, "
                f"Spracovanie={self.processing_duration_min:.2f} min")

class StoreSimulation:
    def __init__(self, simulation_id, run_duration_hours=8, time_scale=100.0):
        self.simulation_id = simulation_id
        self.run_duration_sec = run_duration_hours * 3600
        self.time_scale = time_scale
        
        # FIFO buffer - kapacita dostatočne veľká aby sa nezaplnila počas simulácie bežne
        self.queue = Fifo(1000)
        
        self.customers = []
        self.current_time = 0.0
        
        # Štatistiky
        self.total_customers = 0
        self.max_wait_time = 0.0
        self.max_queue_length = 0
        self.total_idle_time = 0.0
        
        # Stav pokladne
        self.cashier_busy_until = 0.0
        self.last_idle_start = 0.0

    def run(self, verbose=True):
        if verbose:
            print(f"\n=== SPUSTENIE SIMULÁCIE č. {self.simulation_id} ===")
        
        # Generovanie zákazníkov vopred alebo za behu? 
        # Keďže je to event-based simulation (diskrétna simulácia), budeme skákať po eventoch alebo po sekundách?
        # Zadanie hovorí "V správnom čase zaraďte kupujúceho...".
        # Najjednoduchšie je generovať príchody postupne.
        
        next_arrival_time = 0.0 # Prvý zákazník príde v čase 0 + 5 + ... alebo hneď? 
        # Zadanie: Ti = Ti-1 + 5 + random(...) -> T0 predošlý = 0.
        # Prvý Ti = 0 + 5 + random(...)
        next_arrival_time = 5 + random.randint(0, 25 + P_CISLO)
        
        customer_counter = 1
        
        # Zoradené udalosti: (čas, typ, objekt)
        # Typy: 'ARRIVAL' (príchod do obchodu - len info), 'QUEUE_ENTRY' (príchod k pokladni), 'CHECKOUT_DONE' (odchod od pokladne)
        # Avšak CHECKOUT_DONE závisí od toho kedy sa dostane na rad.
        
        # Budeme simulovať po 1 virtuálnej sekunde (rýchle a jednoduché implementovať)
        # alebo event-based. Event based je presnejší pre desatinné časy.
        
        # Zoznam aktívnych zákazníkov v obchode (nakupujúcich)
        shoppers = [] 
        
        # Zoznam ukončených zákazníkov
        finished_customers = []

        is_idle = True
        self.last_idle_start = 0.0

        step = 1.0 # krok simulácie v sekundách
        while self.current_time < self.run_duration_sec or self.queue.getLength() > 0 or shoppers:
            # 1. Kontrola príchodu nového zákazníka do obchodu
            # Generujeme ich len ak ešte neuplynul otvárací čas
            if self.current_time < self.run_duration_sec and self.current_time >= next_arrival_time:
                c = Customer(customer_counter, next_arrival_time)
                shoppers.append(c)
                self.customers.append(c)
                if verbose:
                    # Toto nie je vyžadované vo výpise "Pri každej zmene vo FIFO", ale užitočné pre debug
                    # print(f"[{format_time(self.current_time)}] Príchod do obchodu: {c}")
                    pass
                    
                customer_counter += 1
                # Plánovanie ďalšieho príchodu
                next_arrival_time += 5 + random.randint(0, 25 + P_CISLO)

            # 2. Kontrola či niekto dopodnakupoval a ide do radu
            # Shoppers zoznam prejdeme a presunieme do queue
            items_to_queue = []
            for s in shoppers:
                if self.current_time >= s.queue_entry_time:
                    items_to_queue.append(s)
            
            for s in items_to_queue:
                shoppers.remove(s)
                try:
                    self.queue.append(s)
                    if verbose:
                        print(f"[{format_time(self.current_time)}] DO RADU: Zákazník {s.id} (Príchod: {format_time(s.arrival_time)}, Nákup: {s.shopping_duration_min}m, Sprac: {s.processing_duration_min:.2f}m)")
                        print(f"    -> Dĺžka radu: {self.queue.getLength()}, Idle pokladne: {format_time(self.total_idle_time)}")
                except IndexError:
                    print("!!! CHYBA: Plný rad, zákazník odchádza !!!")

                # Update max queue length
                if self.queue.getLength() > self.max_queue_length:
                    self.max_queue_length = self.queue.getLength()

            # 3. Obsluha pokladne
            if self.current_time >= self.cashier_busy_until:
                # Pokladňa je voľná
                if not is_idle:
                     # Práve sa uvoľnila
                     is_idle = True
                     self.last_idle_start = self.current_time

                if self.queue.getLength() > 0:
                    # Berieme zákazníka
                    customer = self.queue.get()
                    
                    # Koniec idle time
                    if is_idle:
                        idle_duration = self.current_time - self.last_idle_start
                        self.total_idle_time += idle_duration
                        is_idle = False
                    
                    customer.start_service_time = self.current_time
                    customer.end_service_time = self.current_time + customer.processing_duration_sec
                    self.cashier_busy_until = customer.end_service_time
                    
                    # Výpočet čakania
                    wait_time = customer.start_service_time - customer.queue_entry_time
                    if wait_time > self.max_wait_time:
                        self.max_wait_time = wait_time
                        
                    finished_customers.append(customer)

            # 4. Kontrola či niekto práve zaplatil (len pre výpis)
            # Ak sa cashier_busy_until == current_time (približne), tak práve skončil
            if not is_idle and abs(self.current_time - self.cashier_busy_until) < step/2:
                 # Nájdeme posledného finished (pozor na race condition v logike, ale tu sme single thread)
                 if finished_customers:
                     last = finished_customers[-1]
                     if abs(last.end_service_time - self.current_time) < step/2:
                         wait = last.start_service_time - last.queue_entry_time
                         if verbose:
                             print(f"[{format_time(self.current_time)}] ODCHOD: Zákazník {last.id}, čakal v rade: {format_time(wait)}")
                             print(f"    -> Dĺžka radu: {self.queue.getLength()}, Idle pokladne: {format_time(self.total_idle_time)}")


            # Posun času
            # Ak bežíme zrýchlene, sleepujeme
            # Zadanie: "Simuláciu spúšťajte zrýchlene (každý časový údaj /100)"
            # To znamená, že 1 sekunda v simulácii trvá 0.01 sekundy reálne.
            # Ale keďže chceme zbehnúť 8 hodín (28800 sekúnd), trvalo by to 288 sekúnd (cca 5 minút).
            # To je akceptovateľné pre "view".
            
            self.current_time += step
            # if verbose: time.sleep(step / self.time_scale) 
            # Pre účely generovania outputu pre užívateľa teraz sleep vypnem, aby sme to mali hneď.

            # Stop condition ak sme za otváracou dobou a všetci sú vybavení
            if self.current_time >= self.run_duration_sec and self.queue.getLength() == 0 and not shoppers and is_idle:
                break
        
        # Prirátame posledný idle time ak skončilo skôr
        if is_idle and self.current_time < self.run_duration_sec:
             self.total_idle_time += (self.run_duration_sec - self.current_time)
        elif is_idle:
             # ak sme skončili po záverečnej, idle time rátame len do poslednej akcie alebo do konca otvaracej doby?
             # Rátame idle time počas otváracej doby.
             pass

        self.total_customers = len(finished_customers)
        return {
            "Run": self.simulation_id,
            "Total Customers": self.total_customers,
            "Max Wait (s)": self.max_wait_time,
            "Max Queue": self.max_queue_length,
            "Total Idle (s)": self.total_idle_time
        }

def main():
    results = []
    print("=== ZAČIATOK SÉRIE 5 SIMULÁCIÍ ===\n")
    
    for i in range(1, 6):
        sim = StoreSimulation(i)
        res = sim.run(verbose=True) # Verbose pre prvú, alebo všetky? "Simuláciu spúšťajte 5x ... po prvom zaplnení obrazovky..."
        # Dám verbose pre všetky, user si scrolne.
        results.append(res)
        print("-" * 50)

    print("\n=== VÝSLEDNÁ TABUĽKA ===")
    print(f"{'Beh':<5} | {'Zákazníci':<10} | {'Max Čakanie':<15} | {'Max Rad':<10} | {'Idle Pokladne':<15}")
    print("-" * 65)
    for r in results:
        print(f"{r['Run']:<5} | {r['Total Customers']:<10} | {format_time(r['Max Wait (s)']):<15} | {r['Max Queue']:<10} | {format_time(r['Total Idle (s)']):<15}")

if __name__ == "__main__":
    main()