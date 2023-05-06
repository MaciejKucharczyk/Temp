class Wino:
    """ Klasa wino zawierajaca parametry danego wina """
    def __init__(self, id, nazwa, kraj,  slodkosc, gatunek, data, zdjecie, cena):
        self.id = id
        self.nazwa = nazwa
        self.slodkosc = slodkosc
        self.gatunek = gatunek
        self.kraj = kraj
        self.data = data
        self.cena = cena
        self.zdjecie = zdjecie
"""
    wina_list = []
    for wino in wina:
        id = wino[0]
        nazwa = wino[1]
        kraj = wino[2]
        slodkosc = wino[3]
        gatunek = wino[4]
        data = wino[5]
        zdjecie = wino[6]
"""
if __name__ == "__main__":
    wino = Wino()
