import random
from fifo import Fifo

PORADOVE_CISLO = 11
OTVARACIA_DOBA_MINUT = 8 * 60  # 480 minút
KAPACITA_FIFO = 1500


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
        return (f"Kupujúci #{self.poradove_cislo}: príchod={self.cas_prichodu:.1f}min, "
                f"nakupovanie={self.cas_nakupovania:.1f}min, "
                f"spracovanie={self.cas_spracovania:.2f}min")


def format_cas(minuty):
    # Formátuje minúty na HH:MM:SS.
    sekundy_total = minuty * 60
    h = int(sekundy_total // 3600)
    m = int((sekundy_total % 3600) // 60)
    s = int(sekundy_total % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def get_cas_koniec_nakupovania(kupujuci):
    # Vráti čas konca nakupovania kupujúceho.
    return kupujuci.cas_koniec_nakupovania


def get_second_element(item):
    # Vráti druhý prvok z tuple/listu.
    return item[1]


def generuj_kupujucich():
    # Generuje kupujúcich počas celej otváracej doby.
    kupujuci_list = []
    cas_prichodu = 0
    i = 1

    while cas_prichodu < OTVARACIA_DOBA_MINUT:
        # Ti = Ti-1 + (5 + random(25+P.Č.)) sekúnd
        if i > 1:
            interval_sekund = 5 + random.randint(0, 25 + PORADOVE_CISLO)
            cas_prichodu = kupujuci_list[-1].cas_prichodu + interval_sekund / 60

        if cas_prichodu >= OTVARACIA_DOBA_MINUT:
            break

        cas_nakupovania = 1 + random.randint(0, 10 + PORADOVE_CISLO)

        cas_spracovania = 0.3 + cas_nakupovania / 20

        kupujuci = Kupujuci(i, cas_prichodu, cas_nakupovania, cas_spracovania)
        kupujuci_list.append(kupujuci)
        i += 1

    return kupujuci_list


def spusti_simulaciu():
    # Spustí simuláciu obchodu
    print("=" * 80)
    print(f"SIMULÁCIA RADU PRI POKLADNI")
    print(f"Otváracia doba: 8 hodín ({OTVARACIA_DOBA_MINUT} min)")
    print("=" * 80)

    # init
    fifo = Fifo(KAPACITA_FIFO)
    kupujuci_list = generuj_kupujucich()

    print(f"Celkový počet kupujúcich: {len(kupujuci_list)}\n")

    # Štatistiky
    celkova_necinnost = 0.0
    max_cakanie = 0.0
    max_dlzka_radu = 0
    suma_cakania = 0.0

    # Stav simulácie
    aktualny_cas = 0.0
    cas_konca_obsluhy = 0.0

    # Zoznamy na spracovanie
    nakupujuci = kupujuci_list.copy()
    nakupujuci.sort(key=get_cas_koniec_nakupovania)

    while nakupujuci or fifo.length() > 0 or cas_konca_obsluhy > aktualny_cas:
        # Nájdi najbližšiu udalosť
        udalosti = []

        # Kupujúci dokončí nakupovanie
        if nakupujuci:
            udalosti.append(('nakup_koniec', nakupujuci[0].cas_koniec_nakupovania))

        # Pokladňa dokončí obsluhu
        if cas_konca_obsluhy > aktualny_cas:
            udalosti.append(('obsluha_koniec', cas_konca_obsluhy))
        elif fifo.length() > 0:
            # Pokladňa je voľná a niekto čaká - začni hneď obsluhovať
            udalosti.append(('zacni_obsluhu', aktualny_cas))

        if not udalosti:
            break

        # Vyber najbližšiu udalosť
        udalosti.sort(key=get_second_element)
        typ_udalosti, cas_udalosti = udalosti[0]

        aktualny_cas = cas_udalosti

        if typ_udalosti == 'nakup_koniec':
            kupujuci = nakupujuci.pop(0)
            kupujuci.cas_vstupu_do_radu = aktualny_cas

            # Ak je pokladňa voľná a fronta prázdna, zákazník ide rovno k pokladni
            if fifo.length() == 0 and cas_konca_obsluhy <= aktualny_cas:
                # Počítaj nečinnosť pokladne (ak už niekto bol obslúžený)
                if cas_konca_obsluhy > 0:
                    necinnost = aktualny_cas - cas_konca_obsluhy
                    celkova_necinnost += necinnost

                cas_cakania = 0.0  # nečakal, ide rovno
                suma_cakania += cas_cakania

                print(f"[{format_cas(aktualny_cas)}] PRÍCHOD A OKAMŽITÁ OBSLUHA | "
                      f"Nečinnosť pokladne: {celkova_necinnost:.2f} min")
                print(f"    -> {kupujuci}")

                cas_konca_obsluhy = aktualny_cas + kupujuci.cas_spracovania
            else:
                # Musí čakať v rade
                try:
                    fifo.put(kupujuci)
                except IndexError:
                    print(
                        f"[{format_cas(aktualny_cas)}] CHYBA: Rad je plný, kupujúci #{kupujuci.poradove_cislo} odchádza!")
                    continue

                # Aktualizuj max dĺžku radu
                if fifo.length() > max_dlzka_radu:
                    max_dlzka_radu = fifo.length()
                    print(f"[{format_cas(aktualny_cas)}] >>> NOVÁ MAX. DĹŽKA RADU: {max_dlzka_radu} <<<")

                print(f"[{format_cas(aktualny_cas)}] PRÍCHOD DO RADU | "
                      f"Dĺžka radu: {fifo.length()}")
                print(f"    -> {kupujuci}")

        elif typ_udalosti == 'obsluha_koniec' or typ_udalosti == 'zacni_obsluhu':
            # Pokladňa dokončila obsluhu alebo je voľná, vezmi ďalšieho z radu
            if fifo.length() > 0:
                kupujuci = fifo.get()
                cas_cakania = aktualny_cas - kupujuci.cas_vstupu_do_radu
                suma_cakania += cas_cakania

                # Aktualizuj max čakanie
                if cas_cakania > max_cakanie:
                    max_cakanie = cas_cakania
                    print(
                        f"[{format_cas(aktualny_cas)}] >>> NOVÁ MAX. DOBA ČAKANIA: {cas_cakania:.2f} min <<<")

                print(f"[{format_cas(aktualny_cas)}] OBSLUHA | "
                      f"Dĺžka radu: {fifo.length()}")
                print(
                    f"    -> Kupujúci #{kupujuci.poradove_cislo} začal platiť, čakal v rade: {cas_cakania:.2f} min")

                cas_konca_obsluhy = aktualny_cas + kupujuci.cas_spracovania

    print("\n" + "=" * 80)
    print("KONIEC SIMULÁCIE - SÚHRN")
    print("=" * 80)
    print(f"Celkový počet kupujúcich: {len(kupujuci_list)}")
    print(f"Maximálna doba čakania v rade: {max_cakanie:.2f} min | {max_cakanie * 60:.0f} s")
    print(f"Maximálna dĺžka radu: {max_dlzka_radu}")
    print(f"Celková doba nečinnosti pokladne: {celkova_necinnost:.2f} min | {celkova_necinnost * 60:.0f} s")
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
    print(f"{'Simulácia':<12} | {'Počet ľudí':<12} | {'Max. čakanie (min)':<18} | "
          f"{'Max. dĺžka radu':<16} | {'Nečinnosť (min)':<16}")
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
