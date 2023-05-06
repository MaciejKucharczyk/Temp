from flask import Flask, render_template, request, redirect
from src.store_data import Data
from src.models.wino import Wino
from src.config import USER, PASS, HOST, PORT, DB_NAME
from src.database import Database
import logging
from src.static import *
import src.user

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sprzedawany_towar = []

all_wina_size = 0

target_database = Database(USER, PASS, HOST, PORT, DB_NAME)
app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    global all_wina_size
    all_wina_list = []
    
    # Selecting data from database
    ceny = Data.get_cena_wina(target_database)
    #zdjecia = Data.get_zdjecie_wina(target_database)
    wina = Data.get_wina(target_database, ceny)
    kraje = Data.get_kraje(target_database)
    gatunki = Data.get_gatunki(target_database)
    slodkosc = Data.get_slodkosc(target_database)
    wina_bez_ceny = Data.get_wina_bez_ceny(target_database)

    winko = wina[0]
    for wine in winko:
        wino = Wino(wine[0], wine[1], wine[2], wine[3], wine[4], wine[5], wine[6], wine[7])
        all_wina_list.append(wino)

    all_wina_size = len(all_wina_list)

    # INSERT
    if request.method == "POST":

        if request.form["btn"] == "Dodaj cenę":
            id_wina = request.form["id_wina"]
            cena = float(request.form["cena"])

            target_database.insert_into_database("INSERT INTO sklep (id_wina, cena) VALUES (%s, %s);", [id_wina, cena])

        if request.form["btn"] == "details":
            pass
            # TODO akcja po kliknięciu w produkt, np: wyświetlenie ceny, stanu na magazynie itp.

        return redirect("/")
    else:
        return render_template(
            "index.html",
            wina=wina,
            kraje=kraje,
            gatunki=gatunki,
            slodkosc=slodkosc,
            wina_bez_ceny=wina_bez_ceny,
            all_wina_list=all_wina_list,
            all_wina_size=all_wina_size,
        )


@app.route("/magazyn", methods=["POST", "GET"])
def magazyn():

    # Selecting data from database
    ceny = Data.get_cena_wina(target_database)
    wina = Data.get_wina(target_database, ceny)
    kraje = Data.get_kraje(target_database)
    gatunki = Data.get_gatunki(target_database)
    slodkosc = Data.get_slodkosc(target_database)
    magazyn = Data.get_magazyn(target_database, wina)
    straty = Data.get_straty(target_database, wina)

    # inserting a new type of wine into the database
    if request.method == "POST":
        # inserting a new type of wine into the database
        if request.form["btn"] == "Dodaj wino":
            nazwa_wina = request.form["nazwa_wina"]
            kraj = request.form["kraj"]
            slodkosc = request.form["slodkosc"]
            gatunek = request.form["gatunek"]
            target_database.insert_into_database(
                "INSERT INTO jstasik_bazy_danych_2.rodzaje_wina (`nazwa`, `kraj`, `gatunek`, `slodkosc`) VALUES (%s, %s, %s, %s);",
                [nazwa_wina, kraj, slodkosc, gatunek],
            )

        # deleting a wine type from the database
        if request.form["btn"] == "Usuń wino":
            id_wina = request.form["id_wina"] 

            logger.info(f"deleting a wine. wine_id: {id_wina}")
            target_database.delete_from_database("DELETE FROM jstasik_bazy_danych_2.rodzaje_wina WHERE `id_wina`=%s", [id_wina])

        # adding a wine delivery to the warehouse
        if request.form["btn"] == "Dodaj dostawę":
            id_wina = request.form["id_wina"]
            regal = request.form["regal"]
            ilosc = request.form["ilosc"]
            partia = request.form["partia"]
            target_database.insert_into_database(
                "INSERT INTO jstasik_bazy_danych_2.magazyn (`nr_regalu`, `id_wina`, `ilosc`, `nr_partii`) VALUES (%s, %s, %s, %s);",
                [regal, id_wina, ilosc, partia],
            )

        # removal of the entire batch from the warehouse
        if request.form["btn"] == "Wycofaj":
            nr_partii = request.form["nr_partii"]
            logger.info(f"deleting a batch of wine. batch_id: {nr_partii}")
            target_database.delete_from_database("DELETE FROM jstasik_bazy_danych_2.magazyn WHERE `nr_partii`=%s", [nr_partii])

        if request.form["btn"] == "Zgłoś straty":
            id_wina = request.form["id_wina"]
            ilosc = int(request.form["ilosc"])
            partia = request.form["nr_partii"]
            delikwent = request.form["delikwent"]

            # zmniejszenie stanu magazynowego
            result = target_database.select_from_database(
                f"SELECT `ilosc` FROM jstasik_bazy_danych_2.magazyn WHERE `nr_partii`={partia};"
            )
            magazyn_list = []
            for r in result:
                magazyn_list.append(int(r[0]))
            stara_ilosc = magazyn_list[0]
            nowa_ilosc = stara_ilosc - ilosc

            if nowa_ilosc < 0:
                # TODO komunikat o błędzie
                return redirect("/magazyn")

            target_database.insert_into_database("UPDATE jstasik_bazy_danych_2.magazyn SET `ilosc`=%s WHERE `nr_partii`=%s", [nowa_ilosc, partia])

            # dodanie do tabeli strat
            target_database.insert_into_database(
                "INSERT INTO jstasik_bazy_danych_2.straty (`id_wina`, `nr_partii`, `ilosc`, `delikwent`) VALUES (%s, %s, %s, %s);",
                [id_wina, partia, ilosc, delikwent],
            )

        # czyszczenie całej tabeli straty
        if request.form["btn"] == "Wyczyść tabelę strat":
            target_database.delete_from_database("DELETE FROM jstasik_bazy_danych_2.straty;")

        return redirect("/magazyn")
        
    else:
        return render_template(
            "magazyn.html",
            wina=wina,
            kraje=kraje,
            gatunki=gatunki,
            slodkosc=slodkosc,
            magazyn=magazyn,
            straty=straty
        )

# zarządzanie transakcjami
@app.route("/transakcje", methods=["POST", "GET"])
def transakcje():
    global sprzedawany_towar

    # Selecting data from database
    transakcje = Data.get_transakcje(target_database)
    sprzedaz = Data.get_sprzedaz(target_database)
    ceny = Data.get_cena_wina(target_database)
    wina = Data.get_wina(target_database, ceny)


    if request.method == "POST":

        if request.form["btn"] == "Anuluj zamówienie":
            target_database.delete_from_database("DELETE FROM `sprzedaz` WHERE `nr_transakcji` NOT IN (SELECT `nr_transakcji` FROM `transakcje`);")

        if request.form["btn"] == "Potwierdź zamówienie":
            forma_platnosci = request.form["platnosc"]
            nr_konta = request.form["nr_konta"]

            target_database.insert_into_database(
            """
            INSERT INTO `transakcje` (`nr_transakcji`, `cena`, `nr_konta`, `forma_platnosci`, `data`)
            SELECT `s`.`nr_transakcji`, SUM(`s`.`ilosc` * `sk`.`cena`) as `cena`, %s, %s, CURRENT_TIMESTAMP
            FROM `sprzedaz` `s`
            JOIN `sklep` `sk` ON `s`.`id_wina` = `sk`.`id_wina`
            WHERE `s`.`nr_transakcji` NOT IN (SELECT `nr_transakcji` FROM `transakcje`)
            GROUP BY `s`.`nr_transakcji`;
            """,
                [nr_konta, forma_platnosci]
            )

            logger.critical(sprzedawany_towar)

            for towar in sprzedawany_towar:
                target_database.insert_into_database("UPDATE magazyn SET ilosc = ilosc - %s WHERE nr_partii = %s;", [towar[0], towar[1]])

            sprzedawany_towar = []


        if request.form["btn"] == "Dodaj do zamówienia":

            id_wina = request.form["id_wina"]
            zamawiana_ilosc = int(request.form["ilosc"])
            
            result = target_database.select_from_database(
                f"SELECT `nr_partii`, `ilosc` FROM `magazyn` WHERE `id_wina` = {id_wina};"
            )
            magazyn_list = []
            for r in result:
                magazyn_list.append((int(r[0]), int(r[1])))

            dostepna_ilosc = 0
            for partia in magazyn_list:
                dostepna_ilosc += partia[1]

            if dostepna_ilosc < zamawiana_ilosc:
                return redirect("/transakcje")
            
            left = zamawiana_ilosc
            for partia in magazyn_list:
                if left == 0:
                    break
                elif partia[1] >= left:
                    sprzedawany_towar.append([left, partia[0]])
                    target_database.insert_into_database(
                        "INSERT INTO `sprzedaz` (`nr_transakcji`, `id_wina`, `ilosc`, `nr_partii`) VALUES ((SELECT MAX(`nr_transakcji`) FROM `transakcje`) + 1, %s, %s, %s);", 
                        [id_wina, left, partia[0]]
                    )
                    break
                else:
                    sprzedawany_towar.append([partia[1], partia[0]])
                    target_database.insert_into_database(
                        "INSERT INTO `sprzedaz` (`nr_transakcji`, `id_wina`, `ilosc`, `nr_partii`) VALUES ((SELECT MAX(`nr_transakcji`) FROM `transakcje`) + 1, %s, %s, %s);", 
                        [id_wina, partia[1], partia[0]]
                    )
                    left = left - partia[1]


        return redirect("/transakcje")

    else:
        return render_template(
            "transakcje.html",
            transakcje=transakcje,
            sprzedaz=sprzedaz,
            wina=wina,
        )

# logowanie jako pracownik
@app.route("/admin")
def admin():
    return render_template(
        "admin.html",
    )

@app.route("/admin", methods=["POST", "GET"])
def login():
    global all_wina_size
    all_wina_list = []
    
    # Selecting data from database
    ceny = Data.get_cena_wina(target_database)
    #zdjecia = Data.get_zdjecie_wina(target_database)
    wina = Data.get_wina(target_database, ceny)
    kraje = Data.get_kraje(target_database)
    gatunki = Data.get_gatunki(target_database)
    slodkosc = Data.get_slodkosc(target_database)
    wina_bez_ceny = Data.get_wina_bez_ceny(target_database)

    winko = wina[0]
    for wine in winko:
        wino = Wino(wine[0], wine[1], wine[2], wine[3], wine[4], wine[5], wine[6], wine[7])
        all_wina_list.append(wino)

    all_wina_size = len(all_wina_list)

    # user = request.form['uname']
    # password = request.form['psw']
    LOGIN = str(src.user.LOGIN)
    PASSWORD = str(src.user.PASSWORD)
    if str(request.form["guzik"]) == "Login":
        user = str(request.form['uname'])
        logger.info(user +" = "+ LOGIN)
        if user != LOGIN:
            return redirect("/index")

        password = str(request.form['psw'])
        if password != PASSWORD:
            return redirect("/index")

        return render_template(
            "employee.html",
            wina=wina,
            kraje=kraje,
            gatunki=gatunki,
            slodkosc=slodkosc,
            wina_bez_ceny=wina_bez_ceny,
            all_wina_list=all_wina_list,
            all_wina_size=all_wina_size,
        )
    else:
        return redirect("/admin")


@app.route("/employee", methods=["POST", "GET"])
def employee():
    global all_wina_size
    all_wina_list = []
    
    # Selecting data from database
    ceny = Data.get_cena_wina(target_database)
    #zdjecia = Data.get_zdjecie_wina(target_database)
    wina = Data.get_wina(target_database, ceny)
    kraje = Data.get_kraje(target_database)
    gatunki = Data.get_gatunki(target_database)
    slodkosc = Data.get_slodkosc(target_database)
    wina_bez_ceny = Data.get_wina_bez_ceny(target_database)

    winko = wina[0]
    for wine in winko:
        wino = Wino(wine[0], wine[1], wine[2], wine[3], wine[4], wine[5], wine[6], wine[7])
        all_wina_list.append(wino)
        logger.info("winko")
        logger.info(wino.nazwa)
        logger.info(wino.cena)
        logger.info(wino.zdjecie)

    all_wina_size = len(all_wina_list)

    # INSERT
    if request.method == "POST":

        if request.form["btn"] == "Dodaj cenę":
            id_wina = request.form["id_wina"]
            cena = float(request.form["cena"])

            target_database.insert_into_database("INSERT INTO sklep (id_wina, cena) VALUES (%s, %s);", [id_wina, cena])

        if request.form["btn"] == "details":
            pass
            # TODO akcja po kliknięciu w produkt, np: wyświetlenie ceny, stanu na magazynie itp.

        return redirect("/")
    else:
        return render_template(
            "employee.html",
            wina=wina,
            kraje=kraje,
            gatunki=gatunki,
            slodkosc=slodkosc,
            wina_bez_ceny=wina_bez_ceny,
            all_wina_list=all_wina_list,
            all_wina_size=all_wina_size,
        )

if __name__ == "__main__":
    # python -m src.sklep_winny
    app.run(debug=False)
