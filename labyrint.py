from lifo import Lifo
import time

with open("labyrint.txt", 'r') as file:
    labirynt = [list(map(int, line.strip().split(" "))) for line in file.readlines()]


def print_labirynt(labirynt):
    for row in labirynt:
        print(' '.join(map(str, row)))


# Mapovanie smerov: názov -> (bitová hodnota, posun x, posun y)
SMERY = {
    'SEVER': (1, 0, -1),
    'VYCHOD': (2, 1, 0),
    'JUH': (4, 0, 1),
    'ZAPAD': (8, -1, 0)
}

OPACNE_SMERY = {
    'SEVER': 'JUH',
    'JUH': 'SEVER',
    'VYCHOD': 'ZAPAD',
    'ZAPAD': 'VYCHOD'
}


def getMoznosti(poz):
    moznosti = []
    hodnota = labirynt[poz[1]][poz[0]]
    if hodnota & 1:
        moznosti.append("SEVER")
    if hodnota & 2:
        moznosti.append("VYCHOD")
    if hodnota & 4:
        moznosti.append("JUH")
    if hodnota & 8:
        moznosti.append("ZAPAD")
    return moznosti


def najdiStart():
    for y in range(len(labirynt)):
        for x in range(len(labirynt[y])):
            if labirynt[y][x] & 16:
                return x, y
    return None


def pohyb(poz, smer):
    x, y = poz
    _, dx, dy = SMERY[smer]
    return x + dx, y + dy


def vypisMiestnost(poradie, poz, ma_kluc):
    hodnota = labirynt[poz[1]][poz[0]]
    moznosti = getMoznosti(poz)

    typ_miestnosti = ""
    if hodnota & 16:
        typ_miestnosti = " [ŠTART]"
    if hodnota & 32:
        typ_miestnosti = " [KĽÚČ]"

    print(f"\nMiestnosť č. {poradie}{typ_miestnosti}")
    print(f"Dostupné dvere: {', '.join(moznosti) if moznosti else 'žiadne'}")
    if ma_kluc:
        print(">>> Máte kľúč! Vráťte sa na štart! <<<")


def main():
    print("=== LABYRINT - Escape Room ===\n")

    velkost_zasobnika = len(labirynt) * len(labirynt[0])
    zasobnik = Lifo(velkost_zasobnika)  # zásobník pre históriu pohybov (smery)

    poz = najdiStart()
    start_poz = poz

    if poz is None:
        print("Chyba: Nenašla sa štartovacia miestnosť!")
        return

    ma_kluc = False
    kroky = 0
    poradie = 1

    start_time = time.time()

    vypisMiestnost(poradie, poz, ma_kluc)

    while True:
        prikaz = input("\nZadajte príkaz (SEVER/VYCHOD/JUH/ZAPAD/NAVRAT): ").strip().upper()

        if prikaz in SMERY:
            moznosti = getMoznosti(poz)

            if prikaz not in moznosti:
                print(f"CHYBA: V smere {prikaz} nie sú dvere!")
                continue

            # Ulož smer do zásobníka
            zasobnik.push(prikaz)

            # Pohyb
            poz = pohyb(poz, prikaz)
            kroky += 1
            poradie += 1

            # Skontroluj či je tu kľúč
            hodnota = labirynt[poz[1]][poz[0]]
            if hodnota & 32 and not ma_kluc:
                ma_kluc = True
                print("\n*** NAŠLI STE KĽÚČ! ***")

            vypisMiestnost(poradie, poz, ma_kluc)

            # Skontroluj víťazstvo
            if ma_kluc and poz == start_poz:
                elapsed = time.time() - start_time
                print("\n*** GRATULUJEME! UNIKLI STE Z LABYRINTU! ***")
                print(f"Čas: {elapsed:.2f} sekúnd")
                print(f"Počet krokov: {kroky}")
                break

        elif prikaz == 'NAVRAT':
            if zasobnik.getLength() == 0:
                print("CHYBA: Nie je možné sa vrátiť - ste na štarte!")
                continue

            # Vyber posledný smer zo zásobníka
            posledny_smer = zasobnik.pop()
            opacny_smer = OPACNE_SMERY[posledny_smer]

            print(f"Návrat: vykonávam pohyb {opacny_smer}")

            # Pohyb v opačnom smere
            poz = pohyb(poz, opacny_smer)
            kroky += 1
            poradie -= 1

            vypisMiestnost(poradie, poz, ma_kluc)

            # Skontroluj víťazstvo
            if ma_kluc and poz == start_poz:
                elapsed = time.time() - start_time
                print("\n*** GRATULUJEME! UNIKLI STE Z LABYRINTU! ***")
                print(f"Čas: {elapsed:.2f} sekúnd")
                print(f"Počet krokov: {kroky}")
                break

        elif prikaz == 'KONIEC':
            print("Hra ukončená.")
            break

        else:
            print(f"CHYBA: Neznámy príkaz '{prikaz}'")


if __name__ == "__main__":
    main()
