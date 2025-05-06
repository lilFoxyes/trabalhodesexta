import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
import matplotlib.pyplot as plt

...
#criando o dataframe com os dados de votação para o meu candidato
#importando os dados de votação
df = pd.read_csv('votacao_secao_2022_DF.csv', sep=';', encoding='latin1')
df = df[df["DS_CARGO"] == "DEPUTADO DISTRITAL"]
...
df = df[df["NM_VOTAVEL"] == "DANIEL DE CASTRO SOUSA"]
df = df[["NM_VOTAVEL", "QT_VOTOS", "NR_ZONA"]]
df = df.groupby(["NM_VOTAVEL", "NR_ZONA"]).sum().reset_index()
df = df.rename(columns={"QT_VOTOS": "Quantidade de votos", "NR_ZONA": "Número das zonas", "NM_VOTAVEL": "Candidato"})


#criando o dataframe com os dados de regiões
regioes = pd.read_csv("zonas_eleitorais.csv", sep=";")
regioes["Número das zonas"] = regioes["Número das zonas"].str.extract(r'(\d+)').astype(int)

#realizando o merge entre os dataframes de votação e regiões
df = df.merge(regioes, on= "Número das zonas" , how="left")
df = df.drop(columns=["Número das zonas"])


#criando o dataframe com os dados de violência
url = "https://www.ssp.df.gov.br/dados-por-regiao-administrativa/"
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
html = soup(response.content, "html.parser")
divs = html.find_all("div", class_="panel-body assessoria")[2]
links = []
for strong_tag in divs.find_all("strong"):
    if "2022" in strong_tag.text:
        xlsx_link = strong_tag.find_next("a", href=True, string=lambda t: "XLS" in t)
        if xlsx_link:
            links.append(xlsx_link["href"])
endpoint = "https://www.ssp.df.gov.br"
links = [
    link if link.startswith("http") else endpoint + link for link in links
]
dfs = []
for link in links:
    df_violencia = pd.read_excel(link)
    natureza_linha = df_violencia[df_violencia.eq("NATUREZA").any(axis=1)].index[0]
    df_violencia.columns = df_violencia.iloc[natureza_linha]
    df_violencia = df_violencia.iloc[natureza_linha + 1:].reset_index(drop=True)
    df_violencia = df_violencia[df_violencia.iloc[:, 0].isin(["1.TOTAL C.V.L.I.", "2. TOTAL C.C.P.", "3. TOTAL OUTROS CRIMES"])]
    df_violencia = df_violencia[["EIXOS INDICADORES", "TOTAL"]]
    total_crimes = df_violencia["TOTAL"].sum()
    new_row = {"EIXOS INDICADORES": "TOTAL DE CRIMES", "TOTAL": total_crimes}
    df_violencia = pd.concat([df_violencia, pd.DataFrame([new_row])], ignore_index=True)
    regiao_nome = link.split("/")[-1].split("_")[1].replace(".xlsx", "").replace("-", " ")
    df_violencia["Regiões"] = regiao_nome
    dfs.append(df_violencia)

    ...

df_violencia = pd.concat(dfs, ignore_index=True)
df_violencia = df_violencia[df_violencia["EIXOS INDICADORES"] == "TOTAL DE CRIMES"]
df_violencia.drop_duplicates(subset=["Regiões"], keep="last", inplace=True)
df_violencia = df_violencia.rename(columns={"TOTAL": "Total de Crimes"})
df_violencia = df_violencia[["Regiões", "Total de Crimes"]]
df_violencia.reset_index(drop=True, inplace=True)


#criando o dataframe com os hospitais
df_saude = pd.read_csv("hospitais.csv", sep=",")
df_hospitais = df_saude.groupby("Regiões").size().reset_index(name="Número de Hospitais")


#ajustando os nomes das regiões para que fiquem iguais
region_mapinha = {
    "Asa Sul (Plano Piloto)": "Asa Sul",
    "Asa Norte (Plano Piloto)": "Asa Norte",
    "Sudoeste, Octogonal, Cruzeiro": "Sudoeste",
    "Octogonal": "Sudoeste",
    "Cruzeiro": "Sudoeste",
    "Lago Norte, Varjão": "Lago Norte",
    "Varjão": "Lago Norte",
    "Ceilândia (setores P Norte": "Ceilândia",
    "P Sul)": "Ceilândia",
    "Ceilândia (Sol Nascente": "Sol Nascente",
    "Expansão)": "Sol Nascente",
    "Núcleo Bandeirante, Park Way": "Núcleo Bandeirante",
    "Park Way": "Núcleo Bandeirante",
    "AGUAS CLARAS": "Águas Claras",
    "ARNIQUEIRA": "Arniqueira",
    "BRASILIA": "Brasília",
    "BRAZLANDIA": "Brazlândia",
    "CANDANGOLANDIA": "Candangolândia",
    "CEILANDIA": "Ceilândia",
    "SCIA": "SCIA Estrutural",
    "CRUZEIRO 65": "Sudoeste",
    "FERCAL": "Fercal",
    "GAMA": "Gama",
    "GUARA": "Guará",
    "ITAPOA": "Itapoã",
    "JARDIM BOTANICO": "Jardim Botânico",
    "LAGO NORTE": "Lago Norte",
    "LAGO SUL": "Lago Sul",
    "NUCLEO BANDEIRANTE": "Núcleo Bandeirante",
    "PLANALTINA": "Planaltina",
    "RECANTO DAS EMAS": "Recanto das Emas",
    "RIACHO FUNDO": "Riacho Fundo",
    "RIACHO FUNDO II": "Riacho Fundo II",
    "SAMAMBAIA": "Samambaia",
    "SANTA MARIA": "Santa Maria",
    "SAO SEBASTIAO": "São Sebastião",
    "SIA": "SIA",
    "SOBRADINHO": "Sobradinho",
    "SOBRADINHO II": "Sobradinho II",
    "SOL NASCENTE ": "Sol Nascente",
    "SUDOESTE": "Sudoeste",
    "TAGUATINGA": "Taguatinga",
    "VARJAO DO TORTO": "Varjão do Torto",
    "VICENTE PIRES": "Vicente Pires",
}
df_votos = df.copy()
df_votos["Regiões"] = df_votos["Regiões"].str.split(", ")
df_votos = df_votos.explode("Regiões").reset_index(drop=True)
...
df_votos["Regiões"] = df_votos["Regiões"].replace(region_mapinha)
df_hospitais["Regiões"] = df_hospitais["Regiões"].replace(region_mapinha)
df_violencia["Regiões"] = df_violencia["Regiões"].replace(region_mapinha)



#fazendo o merge entre os dataframes para termos de comparação
df_combinado = df_votos.merge(df_hospitais, left_on="Regiões", right_on="Regiões", how="left")
df_combinado = df_combinado.merge(df_violencia, left_on="Regiões", right_on="Regiões", how="left")
df_combinado = df_combinado.drop(columns=["Regiões"])

...


#votos por hospital
plt.figure(figsize=(8, 6))
plt.scatter(df_combinado["Número de Hospitais"], df_combinado["Quantidade de votos"], color="blue", alpha=0.7)
plt.title("Votes vs. Number of Hospitals")
plt.xlabel("Number of Hospitals")
plt.ylabel("Number of Votes")
plt.grid()
plt.show()


#votos por crime
plt.figure(figsize=(8, 6))
plt.scatter(df_combinado["Total de Crimes"], df_combinado["Quantidade de votos"], color="red")
plt.title("Votes vs. Total Crimes")
plt.xlabel("Total Crimes")
plt.ylabel("Votes")
plt.grid()
plt.show()

#relação das regiões sem votos
regioes_com_votos = df["Regiões"].unique()
regioes_sem_votos = regioes[~regioes["Regiões"].isin(regioes_com_votos)]
regioes_sem_votos = regioes_sem_votos.assign(Regiões=regioes_sem_votos["Regiões"].str.split(", ")).explode("Regiões").reset_index(drop=True)
regioes_sem_votos["Regiões"] = regioes_sem_votos["Regiões"].replace(region_mapinha)
regioes_sem_votos_crimes = regioes_sem_votos.merge(df_violencia, left_on="Regiões", right_on="Regiões", how="left")
regioes_sem_votos_hospitais = regioes_sem_votos.merge(df_hospitais, left_on="Regiões", right_on="Regiões", how="left")



#regiões sem votos com dados de violência
plt.figure(figsize=(8, 6))
plt.scatter(regioes_sem_votos_crimes["Regiões"], regioes_sem_votos_crimes["Total de Crimes"], color="orange", alpha=0.7)
plt.title("Crimes in Regions Without Votes")
plt.xlabel("Regions")
plt.ylabel("Total Crimes")
plt.xticks(rotation=90)
plt.grid()
plt.show()


#regiões sem votos com dados de hospitais
plt.figure(figsize=(8, 6))
plt.scatter(regioes_sem_votos_hospitais["Regiões"], regioes_sem_votos_hospitais["Número de Hospitais"], color="green", alpha=0.7)
plt.title("Hospitals in Regions Without Votes")
plt.xlabel("Regions")
plt.ylabel("Number of Hospitals")
plt.xticks(rotation=90)
plt.grid()
plt.show()

sem_hospitais_e_votos = df_combinado[(df_combinado["Número de Hospitais"] == 0) & (df_combinado["Quantidade de votos"] == 0)]
# Plot regions without hospitals and votes
plt.figure(figsize=(8, 6))
plt.bar(sem_hospitais_e_votos["Regiões"], sem_hospitais_e_votos["Total de Crimes"], color="red", label="Total de Crimes")
plt.title("Regiões Sem Hospitais e Sem Votos")
plt.xlabel("Regiões")
plt.ylabel("Total de Crimes")
plt.xticks(rotation=90)
plt.grid(axis="y")
plt.legend()
plt.show()

...