# Salve como gerar_geojson_regioes.py e execute: python gerar_geojson_regioes.py
import geopandas as gpd
from geobr import read_region

# Carrega as macro-regiões (2010 ou 2020 disponíveis)
gdf = read_region(year=2020)

# Mantém só as colunas necessárias
gdf = gdf[["code_region", "name_region", "geometry"]]

# Exporta como GeoJSON no mesmo diretório do HTML
gdf.to_file("br_regioes.geojson", driver="GeoJSON")
print("Arquivo 'br_regioes.geojson' gerado com sucesso.")
