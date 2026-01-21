import random
from fifo import Fifo

PORADOVE_CISLO = 11
OTVARACIA_DOBA_SEKUND = 8 * 60 * 60
ZRYCHLENIE = 100
KAPACITA_FIFO = 10000


class Kupujuci:
    # Trieda reprezentujúca kupujúceho.

    def __init__(self, poradove_cislo, cas_prichodu, cas_nakupovania, cas_spracovania):
        self.poradove_cislo = poradove_cislo
        self.cas_prichodu = cas_prichodu
        self.cas_nakupovania = cas_nakupovania
        self.cas_spracovania = cas_spracovania
        self.cas_koniec_nakupovania = cas_prichodu + self.cas_nakupovania
        self.cas_vstupu_do_radu = None

    def __str__(self):
        return (f"Kupujúci #{self.poradove_cislo}: príchod={self.cas_prichodu}s, "
                f"nakupovanie={self.cas_nakupovania:.1f}s, "
                f"spracovanie={self.cas_spracovania:.2f}s")


def format_cas(sekundy):
    # Formátuje sekundy na HH:MM:SS.
    h = int(sekundy // 3600)
    m = int((sekundy % 3600) // 60)
    s = int(sekundy % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def generuj_kupujucich():
    # Generuje kupujúcich počas celej otváracej doby.
    kupujuci_list = []
    cas_prichodu = 0
    i = 1

    while cas_prichodu < OTVARACIA_DOBA_SEKUND:
        # Ti = Ti-1 + 5 + random(25+P.Č.) sekúnd
        if i > 1:
            cas_prichodu = kupujuci_list[-1].cas_prichodu + 5 + random.randint(0, 25 + PORADOVE_CISLO)

        if cas_prichodu >= OTVARACIA_DOBA_SEKUND:
            break

        # Tn = 1 + random(10+P.Č.) minút
        cas_nakupovania = 1 + random.randint(0, 10 + PORADOVE_CISLO) * 60

        # Tp = 0.3 + Tn/20 minút
        cas_spracovania = 0.3 + cas_nakupovania / 20 * 60

        kupujuci = Kupujuci(i, cas_prichodu, cas_nakupovania, cas_spracovania)
        kupujuci_list.append(kupujuci)
        i += 1

    # Zoradenie podľa času konca nakupovania
    kupujuci_list.sort(key=lambda k: k.cas_koniec_nakupovania)

    return kupujuci_list


def spusti_simulaciu():
    # Spustí simuláciu obchodu
    print("=" * 80)
    print(f"SIMULÁCIA RADU PRI POKLADNI")
    print(f"Otváracia doba: 8 hodín ({OTVARACIA_DOBA_SEKUND}s), Zrýchlenie: {ZRYCHLENIE}x")
    print("=" * 80)

    # init
    fifo = Fifo(KAPACITA_FIFO)
    kupujuci_list = generuj_kupujucich()

    print(f"Celkový počet kupujúcich: {len(kupujuci_list)}\n")

    # Štatistiky
    celkova_necinnost = 0.0
    max_cakanie = 0.0
    max_dlzka_radu = 0

    # Stav simulácie
    aktualny_cas = 0.0
    cas_konca_obsluhy = 0.0

    # Zoznamy na spracovanie
    nakupujuci = kupujuci_list.copy()  # zakaznici ktory este nakupuju
    nakupujuci.sort(key=lambda k: k.cas_koniec_nakupovania)

    while aktualny_cas < OTVARACIA_DOBA_SEKUND or fifo.length() > 0:
        # Nájdi najbližšiu udalosť
        udalosti = []

        # Kupujúci dokončí nakupovanie
        if nakupujuci:
            udalosti.append(('nakup_koniec', nakupujuci[0].cas_koniec_nakupovania))

        # Pokladňa dokončí obsluhu
        if cas_konca_obsluhy > aktualny_cas:
            udalosti.append(('obsluha_koniec', cas_konca_obsluhy))
        elif fifo.length() > 0:
            # Môžeme hneď obslúžiť ďalšieho
            udalosti.append(('obsluha_koniec', aktualny_cas))

        if not udalosti:
            if aktualny_cas >= OTVARACIA_DOBA_SEKUND:
                break
            # Posunieme čas
            aktualny_cas += 1
            continue

        # Vyber najbližšiu udalosť
        udalosti.sort(key=lambda x: x[1])
        typ_udalosti, cas_udalosti = udalosti[0]

        aktualny_cas = cas_udalosti

        if typ_udalosti == 'nakup_koniec':
            # Kupujúci dokončil nakupovanie - postaví sa do radu
            kupujuci = nakupujuci.pop(0)
            kupujuci.cas_vstupu_do_radu = aktualny_cas

            try:
                fifo.put(kupujuci)
            except IndexError:
                print(f"[{format_cas(aktualny_cas)}] CHYBA: Rad je plný, kupujúci #{kupujuci.poradove_cislo} odchádza!")
                continue

            # Aktualizuj max dĺžku radu
            if fifo.length() > max_dlzka_radu:
                max_dlzka_radu = fifo.length()
                print(f"[{format_cas(aktualny_cas)}] >>> NOVÁ MAX. DĹŽKA RADU: {max_dlzka_radu} <<<")

            print(f"[{format_cas(aktualny_cas)}] PRÍCHOD DO RADU | "
                  f"Dĺžka radu: {fifo.length()} | Nečinnosť: {celkova_necinnost:.2f}s")
            print(f"    -> {kupujuci}")

            # Ak pokladňa čaká, spočítaj nečinnosť
            if cas_konca_obsluhy <= aktualny_cas and fifo.length() == 1:
                necinnost = aktualny_cas - max(cas_konca_obsluhy, 0)
                if necinnost > 0 and cas_konca_obsluhy > 0:
                    celkova_necinnost += necinnost

        elif typ_udalosti == 'obsluha_koniec':
            if fifo.length() > 0:
                kupujuci = fifo.get()
                cas_cakania = aktualny_cas - kupujuci.cas_vstupu_do_radu

                # Aktualizuj max čakanie
                if cas_cakania > max_cakanie:
                    max_cakanie = cas_cakania
                    print(f"[{format_cas(aktualny_cas)}] >>> NOVÁ MAX. DOBA ČAKANIA: {max_cakanie:.2f}s <<<")

                print(f"[{format_cas(aktualny_cas)}] ODCHOD Z RADU | "
                      f"Dĺžka radu: {fifo.length()} | Nečinnosť: {celkova_necinnost:.2f}s")
                print(f"    -> Kupujúci #{kupujuci.poradove_cislo} zaplatil, čakal v rade: {cas_cakania:.2f}s")

                cas_konca_obsluhy = aktualny_cas + kupujuci.cas_spracovania
            else:
                # Pokladňa je voľná, ale nikto nečaká
                if aktualny_cas >= OTVARACIA_DOBA_SEKUND:
                    break

    # Záverečné štatistiky
    print("\n" + "=" * 80)
    print("KONIEC SIMULÁCIE - SÚHRN")
    print("=" * 80)
    print(f"Celkový počet kupujúcich: {len(kupujuci_list)}")
    print(f"Maximálna doba čakania v rade: {max_cakanie / 60:.2f} min = {max_cakanie:.2f} sekúnd")
    print(f"Maximálna dĺžka radu: {max_dlzka_radu}")
    print(f"Celková doba nečinnosti pokladne: {celkova_necinnost / 60:.2f} min = {celkova_necinnost:.2f} sekúnd")
    print("=" * 80)

    return {
        'pocet_ludi': len(kupujuci_list),
        'max_cakanie': max_cakanie,
        'max_dlzka_radu': max_dlzka_radu,
        'necinnost': celkova_necinnost
    }


def spusti_5_simulacii():
    # Spustí 5 simulácií a zobrazí výsledky v tabuľke.
    vysledky = []

    for i in range(5):
        print(f"\n{'#' * 80}")
        print(f"SIMULÁCIA č. {i + 1}")
        print(f"{'#' * 80}\n")

        vysledok = spusti_simulaciu()
        vysledky.append(vysledok)

        input("\nStlačte ENTER pre pokračovanie na ďalšiu simuláciu...")

    # Výpis tabuľky
    print("\n" + "=" * 100)
    print("SÚHRNNÁ TABUĽKA VÝSLEDKOV (5 simulácií)")
    print("=" * 100)
    print(f"{'Simulácia':<12} | {'Počet ľudí':<12} | {'Max. čakanie (s)':<18} | "
          f"{'Max. dĺžka radu':<16} | {'Nečinnosť (s)':<16}")
    print("-" * 100)

    for i, v in enumerate(vysledky, 1):
        print(f"{i:<12} | {v['pocet_ludi']:<12} | {v['max_cakanie']:<18.2f} | "
              f"{v['max_dlzka_radu']:<16} | {v['necinnost']:<16.2f}")

    print("=" * 100)


if __name__ == "__main__":
    print("Vyberte režim:")
    print("1 - Jedna simulácia")
    print("2 - 5 simulácií s tabuľkou")

    volba = input("Vaša voľba (1/2): ").strip()

    if volba == "2":
        spusti_5_simulacii()
    else:
        spusti_simulaciu()
