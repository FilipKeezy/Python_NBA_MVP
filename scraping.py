import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

ani = list(range(1980, 2025))




#web scraping. ia fisierele html
for an in ani:
    url = f"https://www.basketball-reference.com/awards/awards_{an}.html"
    print(f"Fetch la datele din {an}...")

    try:
        response = requests.get(url)
        response.raise_for_status()  # arunca exceptie daca nu poate accesa

        with open(f"mvp/{an}.html", "w+", encoding="utf-8") as f:
            f.write(response.text)

        print(f"A salvat html {an}.\n")
        time.sleep(30)

    except requests.RequestException as e:
        print(f"Nu a salvat html pt {an}: {e}")



#pt an individual
import requests

url = "https://www.basketball-reference.com/awards/awards_2024.html"
data = requests.get(url)

with open("mvp/2024.html", "w+", encoding="utf-8") as f:
    f.write(data.text)
    page = data.text
soup = BeautifulSoup(page, "html.parser")#creaza parser class ca sa extragem tabeulul din pagina

#citire si prelucrare fișiere HTML
dfs = []
for an in ani:
    with open("mvp/{}.html".format(an), encoding="utf-8") as f:
        page = f.read()
    soup = BeautifulSoup(page, "html.parser")
    soup.find('th', class_=["over_header", "center"]).decompose()
    tabela_mvp = soup.find(id="mvp")
    mvp = pd.read_html(str(tabela_mvp))[0]

    dfs.append(mvp)

for an in ani:
    try:
        with open(f"mvp/{an}.html", encoding="utf-8") as f:
            page = f.read()

        soup = BeautifulSoup(page, "html.parser")

        tabela_mvp = soup.find("table", id="mvp")
        if tabela_mvp is None:
            print(f"Nu exista tabel mvp pt {an}")
            continue

        nou_soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        nou_soup.body.append(tabela_mvp)

        with open(f"doar_mvp/{an}.html", "w+", encoding="utf-8") as f:
            f.write(nou_soup.prettify())

        print(f" Salvat pt {an}")

    except Exception as e:
        print(f" Eroare la anul {an}: {e}")



dfs = []

for an in ani:
    try:
        with open(f"doar_mvp/{an}.html", encoding="utf-8") as f:
            page = f.read()

        soup = BeautifulSoup(page, "html.parser")
        tabela_mvp = soup.find("table", id="mvp")

        if tabela_mvp:
            for a in tabela_mvp.find_all("a"):
                a.replace_with(a.text)

            df = pd.read_html(str(tabela_mvp), header=0)[0]

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [' '.join(col).strip() for col in df.columns]

            df["An"] = an
            cols = ["An"] + [col for col in df.columns if col != "An"]
            df = df[cols]

            dfs.append(df)

    except Exception as e:
        print(f"Eroare la {an}: {e}")

#Concat finala
mvps = pd.concat(dfs, ignore_index=True)

# salvare
mvps.to_csv("mvps.csv")

#intr-un singur dataframe
df_final = pd.concat(dfs, ignore_index=True)
print(df_final.head())
