# Klasyczny Algorytm Genetyczny (Projekt OE)

## Cel projektu
Implementacja klasycznego algorytmu genetycznego (AG) do optymalizacji (minimalizacji i maksymalizacji) funkcji wielu zmiennych. Projekt realizowany jako API (FastAPI) z kodem napisanym obiektowo w Pythonie (bez użycia dedykowanych bibliotek ewolucyjnych).

## Słowniczek pojęć (Skondensowana Wiedza)
Zrozumienie tych pojęć jest niezbędne do pracy z kodem:

* **Optymalizacja** – poszukiwanie minimum (lub maksimum) funkcji celu.
* **Funkcja celu (Fitness Function)** – matematyczny wzór (np. z `FunkcjeTestowe.pdf`), który ocenia, jak dobre jest dane rozwiązanie.
* **Populacja** – zbiór potencjalnych rozwiązań problemu (osobników) w danej iteracji.
* **Osobnik / Chromosom** – pojedyncze rozwiązanie. W naszym projekcie ma reprezentację binarną (ciąg zer i jedynek).
* **Gen / Allel** – pojedynczy bit w chromosomie (wartość `0` lub `1`).
* **Epoka (Generacja)** – jedna pełna pętla działania algorytmu (ocena -> selekcja -> krzyżowanie -> mutacja).
* **Dekodowanie** – zamiana ciągu binarnego (chromosomu) na wartość rzeczywistą, aby móc podstawić ją pod funkcję celu.
* **Selekcja** – wybór najlepszych osobników, którzy przekażą swoje geny dalej (metody: najlepszych, ruletka, turniej).
* **Krzyżowanie** – łączenie genów dwóch rodziców w celu stworzenia potomstwa (np. wymiana części bitów).
* **Mutacja** – celowa, losowa zmiana pojedynczych bitów (genów) u potomstwa, aby zapobiec utknięciu algorytmu w lokalnym minimum.
* **Elitaryzm** – przeniesienie najlepszego osobnika (lub kilku) z poprzedniej epoki do nowej bez żadnych zmian, aby nie stracić najlepszego znalezionego rozwiązania.

## Wymagane funkcjonalności
1. **Selekcja**: Najlepszych, Koło Ruletki, Turniejowa.
2. **Krzyżowanie**: Jednopunktowe, Dwupunktowe, Jednorodne, Ziarniste.
3. **Mutacja**: Brzegowa, Jednopunktowa, Dwupunktowa.
4. **Inne operatory**: Operator inwersji, Strategia elitarna.
