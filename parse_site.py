import requests
import bs4
import tabulate
import statistics
import pytemperature
import lxml


def get_header_and_data(soup):
    basliklar = []
    satirlar = []

    for sira, satir in enumerate(soup.find("table").find_all("tr")):
        if sira in (0, 2):
            continue

        for sutun in satir.find_all("th"):
            basliklar.append(sutun.text)

        sutunlar = []
        for sutun in satir.find_all("td"):
            sutunlar.append(sutun.text)
        if sutunlar:
            satirlar.append(sutunlar)

    return basliklar, satirlar


def cast_data(row_data):
    yeni_satirlar = []

    for satir in row_data:
        yeni_satir = list(satir)

        for sutun_sirasi in range(1, 5):
            veri = yeni_satir[sutun_sirasi]
            yeni_satir[sutun_sirasi] = int(veri.replace(",", ""))

        yeni_satir[5] = float(yeni_satir[5])
        yeni_satirlar.append(yeni_satir)

    return yeni_satirlar


def get_calculated_rows(row_data):
    total_population = []
    in_migration = []
    out_migration = []

    for satir in row_data:
        total_population.append(satir[1])
        in_migration.append(satir[2])
        out_migration.append(satir[3])

    maksimum_satir = ["Maksimum", max(total_population), max(in_migration), max(out_migration), 0, 0.0]
    ortalama_satir = ["Ortalama", statistics.mean(total_population), statistics.mean(in_migration),
                      statistics.mean(out_migration), 0, 0.0]
    minimum_satir = ["Minimum", min(total_population), min(in_migration), min(out_migration), 0, 0.0]

    return maksimum_satir, ortalama_satir, minimum_satir


def get_formatted_rows(row_data):
    formatli_satirlar = []
    for satir in row_data:
        formatli_satirlar.append([
            satir[0],
            "{:d}".format(int(satir[1])),
            "{:d}".format(int(satir[2])),
            "{:d}".format(int(satir[3])),
            "{:d}".format(int(satir[4])),
            "{:.3f}".format(satir[5]),
        ])
    return formatli_satirlar


def get_goc_data():
    base_url = "http://itu17-a3-asocia.herokuapp.com/"

    anasayfa_response = requests.get(base_url)
    anasayfa_soup = bs4.BeautifulSoup(anasayfa_response.text, "lxml")

    basliklar, ham_satirlar = get_header_and_data(anasayfa_soup)
    cast_satirlar = cast_data(ham_satirlar)
    ortalama_satirlar = get_calculated_rows(cast_satirlar)

    for row in reversed(ortalama_satirlar):
        cast_satirlar.insert(0, row)

    formatli_satirlar = get_formatted_rows(cast_satirlar)

    guzel_tablo = tabulate.tabulate(formatli_satirlar, headers=basliklar, tablefmt="fancy_grid")
    print(anasayfa_soup.find(class_="title").text)
    print(guzel_tablo)


def get_weather_data():
    base_url = "https://www.yahoo.com/news/weather"

    hava_response = requests.get(base_url)
    hava_soup = bs4.BeautifulSoup(hava_response.text, "lxml")

    now_soup = hava_soup.find(class_="temperature").find(class_="now")

    derece = now_soup.find("span").text
    olcek = now_soup.find(class_="unit-control").find("button").text

    if olcek.lower() == "f":
        celcius_derece = int(pytemperature.f2c(int(derece)))
    elif olcek.lower() == "c":
        celcius_derece = int(derece)
    else:
        raise ValueError("Yahoo'nun gösterdiği sıcaklık ölçeği celcius ya da fahreneit değil")

    import sys
    if sys.version_info[:2] >= (3, 6):
        print(f"{celcius_derece:d}C°")
    else:
        print("{:d} C°".format(celcius_derece))


def get_itugnu_data():
    itugnu_response = requests.get("https://itugnu.org/tr/lectures/")
    itugnu_soup = bs4.BeautifulSoup(itugnu_response.text, "lxml")
    for container in itugnu_soup.find_all(class_="portfolio-caption"):
        h4 = container.find("h4")

        if "fa-star" in h4.find("i").attrs["class"]:
            durum = "Açık"
        else:
            durum = "Kapalı"

        print(h4.text.strip(), "|", durum)


get_goc_data()
print("-"*79)
get_weather_data()
print("-"*79)
get_itugnu_data()