from venv import logger
from src.database import Database


class Data:
    @classmethod
    def get_zdjecie_wina(cls, db: Database) -> dict:
        """tuple[int, int] -> id, nazwa pliku ze zdjeciem"""

        dane = db.select_from_database(
            "SELECT `rodzaje_wina`.`zdjecie`, `zdjecia`.`zdjecie` FROM `zdjecia` INNER JOIN `rodzaje_wina` WHERE `zdjecia`.`id_zdjecia` = `rodzaje_wina`.`zdjecie`;"
        )

        zdjecia_list = {}
        for d in dane:
            id = d[0]
            zdjecie = d[1]
            zdjecia_list[id] = zdjecie
            logger.info(zdjecie)
        logger.info(zdjecia_list)
        return zdjecia_list

    @classmethod
    def get_cena_wina(cls, db: Database) -> dict:
        """tuple[int, int] -> id, cena"""

        dane = db.select_from_database(
            "SELECT * FROM `sklep`;"
        )

        ceny_list = {}
        for d in dane:
            id = d[0]
            cena = d[1]
            ceny_list[id] = cena

        return ceny_list

    @classmethod
    def get_wina(cls, db: Database, ceny) -> tuple[list, int]:
        """Wyciąga dane z tabeli 'wina'

        Args:
            db (Database): baza danych z której mają być wyciągnięte informacje

        Returns:
            tuple[list, int]: list(id, nazwa, kraj, slodkosc, gatunek, data, zdjecie), długość listy
        """

        wina = db.select_from_database(
            "SELECT * FROM jstasik_bazy_danych_2.rodzaje_wina;"
        )
        wina_list = []
        i = 0
        for wino in wina:
            id = wino[0]
            nazwa = wino[1]
            kraj = wino[2]
            slodkosc = wino[3]
            gatunek = wino[4]
            data = wino[5]
            zdjecie = wino[6]
            try:
                cena = ceny[id]
            except:
                cena = 0

           # try:
            #    zdjecie = zdjecia[id]
           # except:
            #    zdjecie = "brak.png"

            wina_list.append((id, nazwa, kraj, slodkosc, gatunek, data, zdjecie, cena))
        return (wina_list, len(wina_list))

    @classmethod
    def get_kraje(cls, db: Database) -> tuple[list, int]:
        """Wyciąga dane z tabeli 'kraje'

        Args:
            db (Database): baza danych z której mają być wyciągnięte informacje

        Returns:
            tuple[list, int]: list(id, nazwa kraju), długość listy
        """

        kraje = db.select_from_database(
            "SELECT * FROM jstasik_bazy_danych_2.kraje;"
        )
        kraje_list = []
        for k in kraje:
            kraje_list.append([k[0], k[1]]) # id, nazwa kraju

        return (kraje_list, len(kraje_list))

    @classmethod
    def get_gatunki(cls, db: Database) -> tuple[list, int]:
        """Wyciąga dane z tabeli 'gatunki'

        Args:
            db (Database): baza danych z której mają być wyciągnięte informacje

        Returns:
            tuple[list, int]: list(id, gatunek), długość listy
        """

        gatunki = db.select_from_database(
            "SELECT * FROM jstasik_bazy_danych_2.gatunki;"
        )
        gatunki_list = []
        for g in gatunki:
            gatunki_list.append([g[0], g[1]])
        return (gatunki_list, len(gatunki_list))

    @classmethod
    def get_slodkosc(cls, db: Database) -> tuple[list, int]:
        """Wyciąga dane z tabeli 'slodkosc'

        Args:
            db (Database): baza danych z której mają być wyciągnięte informacje

        Returns:
            tuple[list, int]: list(id, słodkość), długość listy
        """

        slodkosci = db.select_from_database(
            "SELECT * FROM jstasik_bazy_danych_2.slodkosc;"
        )
        slodkosc_list = []
        for s in slodkosci:
            slodkosc_list.append([s[0], s[1]])
        return (slodkosc_list, len(slodkosc_list))

    @classmethod
    def get_slodkosc(cls, db: Database) -> tuple[list, int]:
        """Wyciąga dane z tabeli 'slodkosc'

        Args:
            db (Database): baza danych z której mają być wyciągnięte informacje

        Returns:
            tuple[list, int]: list(id, słodkość), długość listy
        """

        slodkosci = db.select_from_database(
            "SELECT * FROM jstasik_bazy_danych_2.slodkosc;"
        )
        slodkosc_list = []
        for s in slodkosci:
            slodkosc_list.append([s[0], s[1]])
        return (slodkosc_list, len(slodkosc_list))

    @classmethod
    def get_name_from_id(cls, id: int, wina: tuple[list, int]) -> str:
        """Funkcja zwracająca nazwę wina o podanym id

        Args:
            id (int): id wina
            wina (tuple[list, int]): dane wyciągnięte z tabeli 'rodzaje_wina'

        Returns:
            str: nazwa wina
        """

        for wino in wina[0]:
            if id == wino[0]:
                return wino[1]
        return ""

    @classmethod
    def get_magazyn(cls, db: Database, wina: tuple[list, int]) -> tuple[list, int]:
        """Wyciąga dane z tabeli 'magazyn'

        Args:
            db (Database): baza danych z której mają być wyciągnięte informacje

        Returns:
            tuple[list, int]: list(id_wina, nazwa, ilosc, nr_regalu, nr_partii), długość listy
        """

        magazyn = db.select_from_database(
            "SELECT * FROM jstasik_bazy_danych_2.magazyn ORDER BY id_wina;"
        )
        magazyn_list = []
        for s in magazyn:
            id_wina = s[1]
            nazwa = Data.get_name_from_id(id_wina, wina)
            ilosc = s[2]
            nr_regalu = s[0]
            nr_partii = s[3]
            magazyn_list.append((id_wina, nazwa, ilosc, nr_regalu, nr_partii))

        return (magazyn_list, len(magazyn_list))

    @classmethod
    def get_straty(cls, db: Database, wina: tuple[list, int]) -> tuple[list, int]:
        """Wyciąga dane z tabeli 'straty'

        Args:
            db (Database): baza danych z której mają być wyciągnięte informacje

        Returns:
            tuple[list, int]: list(id_wina, nazwa, ilosc, nr_partii, delikwent), długość listy
        """

        straty = db.select_from_database(
            "SELECT * FROM jstasik_bazy_danych_2.straty ORDER BY id_wina;"
        )
        straty_list = []
        for s in straty:
            id_wina = s[0]
            nazwa = Data.get_name_from_id(id_wina, wina)
            ilosc = s[2]
            nr_partii = s[1]
            delikwent = s[3]
            straty_list.append((id_wina, nazwa, ilosc, nr_partii, delikwent))

        return (straty_list, len(straty_list))

    @classmethod
    def get_transakcje(cls, db: Database):
        
        result = db.select_from_database(
            """
            SELECT `sprzedaz`.`nr_transakcji` , `rodzaje_wina`.`nazwa`, `sprzedaz`.`ilosc`, `sprzedaz`.`nr_partii`, `transakcje`.`cena`, `formy_platnosci`.`forma_platnosci`, `transakcje`.`nr_konta`, `transakcje`.`data`
            FROM `sprzedaz`
            RIGHT JOIN `transakcje` ON `sprzedaz`.`nr_transakcji` = `transakcje`.`nr_transakcji`
            RIGHT JOIN `rodzaje_wina` ON `sprzedaz`.`id_wina` = `rodzaje_wina`.`id_wina`
            RIGHT JOIN `formy_platnosci` ON `transakcje`.`forma_platnosci` = `formy_platnosci`.`id_formy_platnosci`
            ORDER BY `sprzedaz`.`nr_transakcji` DESC;"""
        )

        result_list = []
        for r in result:
            nr_transakcji = int(r[0])
            nazwa = r[1]
            ilosc = int(r[2])
            nr_partii = int(r[3])
            cena = float(r[4])
            forma_platnosci = r[5]
            nr_konta = r[6]
            data = r[7]
            result_list.append((nr_transakcji, nazwa, ilosc, nr_partii, cena, forma_platnosci, nr_konta, data))

        return (result_list, len(result_list))

    @classmethod
    def get_sprzedaz(cls, db: Database):
        
        result = db.select_from_database(
            """
            SELECT `sprzedaz`.`nr_transakcji`, `rodzaje_wina`.`nazwa`, `sprzedaz`.`ilosc`, `sprzedaz`.`nr_partii`
            FROM `sprzedaz`
            LEFT JOIN `transakcje` ON `sprzedaz`.`nr_transakcji` = `transakcje`.`nr_transakcji`
            INNER JOIN `rodzaje_wina` ON `sprzedaz`.`id_wina` = `rodzaje_wina`.`id_wina`
            WHERE `transakcje`.`nr_transakcji` IS NULL;"""
        )

        result_list = []
        for r in result:
            nr_transakcji = int(r[0])
            nazwa = r[1]
            ilosc = int(r[2])
            nr_partii = int(r[3])
            result_list.append((nr_transakcji, nazwa, ilosc, nr_partii))

        return (result_list, len(result_list))

    @classmethod
    def get_wina_bez_ceny(cls, db: Database):
        
        result = db.select_from_database(
            """
            SELECT `rodzaje_wina`.`id_wina`, `rodzaje_wina`.`nazwa`
            FROM `rodzaje_wina`
            LEFT JOIN `sklep` ON `rodzaje_wina`.`id_wina` = `sklep`.`id_wina`
            WHERE `sklep`.`cena` IS NULL;"""
        )

        result_list = []
        for r in result:
            id_wina = int(r[0])
            nazwa = r[1]
            result_list.append((id_wina, nazwa))

        return (result_list, len(result_list))
