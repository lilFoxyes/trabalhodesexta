import pandas as pd
import requests
import matplotlib.pyplot as plt

...
#criando o dataframe com os dados de votação para o meu candidato
#importando os dados de votação
df = pd.read_csv('votacao_secao_2022_DF.csv', sep=';', encoding='latin1')
df = df[df["DS_CARGO"] == "DEPUTADO DISTRITAL"]
df = df[["NM_VOTAVEL", "QT_VOTOS", "NR_ZONA"]]
df = df.groupby(["NM_VOTAVEL", "NR_ZONA"]).sum().reset_index()
df = df.rename(columns={"QT_VOTOS": "Quantidade de votos", "NR_ZONA": "Número das zonas", "NM_VOTAVEL": "Candidato"})

...
#criando o dataframe com os dados de regiões
regioes = pd.read_csv("zonas_eleitorais.csv", sep=";")
regioes["Número das zonas"] = regioes["Número das zonas"].str.extract(r'(\d+)').astype(int)

#realizando o merge entre os dataframes de votação e regiões
df = df.merge(regioes, on= "Número das zonas" , how="left")
df = df.drop(columns=["Número das zonas"])


#criando o dataframe com os dados de violência
df_violencia = pd.read_excel("violencia_2022.xlsx")


#criando o dataframe com os hospitais
df_saude = pd.read_csv("hospitais.csv", sep=",")
df_hospitais = df_saude.groupby("Regiões").size().reset_index(name="Número de Hospitais")

df_perfil_eleitores = pd.read_csv("perfil_eleitor_secao_2022_DF.csv", sep=";", encoding="latin1")
df_perfil_eleitores.rename(columns={"NR_ZONA": "Número das zonas"}, inplace=True)
df_perfil_eleitores = df_perfil_eleitores[["DS_GRAU_ESCOLARIDADE", "DS_GENERO", "Número das zonas"]]
df_perfil_eleitores.rename(columns={"DS_GRAU_ESCOLARIDADE": "Escolaridade", "DS_GENERO": "Gênero"}, inplace=True)
df_perfil_eleitores = df_perfil_eleitores.merge(regioes, on="Número das zonas", how="left")
df_perfil_eleitores = df_perfil_eleitores.drop(columns=["Número das zonas"])
df_perfil_eleitores = df_perfil_eleitores.groupby(["Escolaridade", "Gênero", "Regiões"]).size().reset_index(name="Número de Eleitores")



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
    "Brasília - Asa Sul": "Asa Sul",
    "Brasília - Asa Norte": "Asa Norte",
    "Paranoá, Varjão, Itapoã, Lago Norte": "Paranoá, Varjão, Itapoã, Lago Norte",
    "Taguatinga": "Taguatinga",
    "Santa Maria": "Santa Maria",
    "Sobradinho": "Sobradinho",
    "Planaltina": "Planaltina",
    "Ceilândia Centro": "Ceilândia Centro",
    "Guará": "Guará",
    "Núcleo Bandeirante, Riacho Fundo, Park Way, Candangolândia": "Núcleo Bandeirante",
    "Samambaia": "Samambaia",
    "Águas Claras": "Águas Claras",
    "Ceilândia Norte, Brazlândia": "Ceilândia Norte",
    "Gama": "Gama",
    "Lago Sul, Jardim Botânico, São Sebastião": "Lago Sul",
    "Ceilândia Sul": "Ceilândia Sul",
    "Recanto das Emas": "Recanto das Emas",
    "Cruzeiro, Sudoeste, Octogonal": "Sudoeste"
}
df_votos = df.copy()
df_votos["Regiões"] = df_votos["Regiões"].str.split(", ")
df_votos = df_votos.explode("Regiões").reset_index(drop=True)
...
df_votos["Regiões"] = df_votos["Regiões"].replace(region_mapinha)
df_hospitais["Regiões"] = df_hospitais["Regiões"].replace(region_mapinha)
df_violencia["Regiões"] = df_violencia["Regiões"].replace(region_mapinha)
df_perfil_eleitores["Regiões"] = df_perfil_eleitores["Regiões"].replace(region_mapinha)



#fazendo o merge entre os dataframes para termos de comparação
df_combinado = df_votos.merge(df_hospitais, left_on="Regiões", right_on="Regiões", how="left")
df_combinado = df_combinado.merge(df_violencia, left_on="Regiões", right_on="Regiões", how="left")

...



...