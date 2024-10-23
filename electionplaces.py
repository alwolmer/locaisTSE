# -*- coding: utf-8 -*-
"""electionPlaces.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1utyiCP72SLBvZLV4jcA6xUKG6t8bOSGM
"""

import pandas as pd
import numpy as np
import requests
import zipfile
import io
import os

project_root = os.getcwd() + '/'
os.makedirs(project_root + 'raw', exist_ok=True)
os.makedirs(project_root + 'abbrev', exist_ok=True)
os.makedirs(project_root + 'grouped', exist_ok=True)
os.makedirs(project_root + 'mapped', exist_ok=True)

for year in range(2010, 2024+1, 2):

    file_name = f'eleitorado_local_votacao_{year}'

    locais_year = None

    try:
        locais_year = pd.read_csv(project_root + 'raw/' + f'{file_name}.csv')
        print(f'Loaded {file_name}.csv')
    except:
        print(f'Downloading {file_name}.csv')
        url = f'https://cdn.tse.jus.br/estatistica/sead/odsele/eleitorado_locais_votacao/eleitorado_local_votacao_{year}.zip'
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            print('Download successful')
            # Open the ZIP file
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # List the contents to find the CSV file
                for file in z.namelist():
                    if file.endswith('.csv'):
                        # Read the CSV file into a pandas DataFrame
                        with z.open(file) as csvfile:
                            locais_year = pd.read_csv(csvfile, encoding='latin 1', delimiter=';')
                            locais_year.to_csv(project_root + 'raw/' + f'{file_name}.csv', index=False)
        else:
            print('Download failed')
            print(response.status_code)
            print(response.text)

    print(locais_year.shape)

    locais_cols = ['AA_ELEICAO', 'NR_TURNO', 'SG_UF', 'NM_MUNICIPIO', 'CD_MUNICIPIO', 'NR_SECAO', 'NR_ZONA', 'NR_LOCAL_VOTACAO', 'NM_LOCAL_VOTACAO', 'DS_ENDERECO', 'NM_BAIRRO', 'NR_CEP', 'NR_LATITUDE', 'NR_LONGITUDE', 'QT_ELEITOR_SECAO']
    locais_year_abbrev = locais_year[locais_cols]
    locais_year_abbrev.to_csv(project_root + 'abbrev/' + f'{file_name}_abbrev.csv', index=False)

    # """# Loading prefiltered data"""

    # locais_year_abbrev = pd.read_csv(project_root + 'abbrev/' + 'eleitorado_local_votacao_2022_abbrev.csv')

    """# Group sections by location"""

    locais_year_grouped = locais_year_abbrev.groupby(['NR_TURNO', 'CD_MUNICIPIO', 'NR_ZONA', 'NR_LOCAL_VOTACAO']).agg(
        NR_SECAO=('NR_SECAO', lambda x: sorted(list(x.unique()))),  # Collect unique NR_SECAO as list
        QT_ELEITOR_SECAO=('QT_ELEITOR_SECAO', 'sum')        # Sum QT_ELEITOR_SECAO
    ).reset_index()

    locais_year_grouped = locais_year_grouped[locais_year_grouped['NR_TURNO'] == 1]

    locais_year_unique = locais_year_abbrev.drop_duplicates(subset=['CD_MUNICIPIO', 'NR_ZONA', 'NR_LOCAL_VOTACAO']).drop(columns=['NR_SECAO', 'QT_ELEITOR_SECAO', 'NR_TURNO'])

    locais_year_grouped = pd.merge(locais_year_unique, locais_year_grouped, on=['CD_MUNICIPIO','NR_ZONA', 'NR_LOCAL_VOTACAO'], how='left')

    # Display the result
    # locais_24_grouped[locais_24_grouped['NR_TURNO'] == 1]
    locais_year_grouped.to_csv(project_root + 'grouped/' + f'{file_name}_grouped.csv', index=False)
    # locais_year_grouped

    """# Mapping TSE and IBGE municipality codes"""

    # extract municipios and map TSE to IBGE codes
    # util_root = '/content/gdrive/My Drive/datasets/utils/'

    # import pandas as pd
    # import numpy as np
    # try:
    #   from rapidfuzz import fuzz
    #   from rapidfuzz import process
    #   from unidecode import unidecode
    # except:
    #   !pip install rapidfuzz -q
    #   !pip install unidecode -q
    #   from rapidfuzz import fuzz
    #   from rapidfuzz import process
    #   from unidecode import unidecode

    # match_cache = {}

    # def fuzzy_match(mun_name, mun_df, min_score=80):
    #     if mun_name in match_cache:
    #         return match_cache[mun_name]
    #     best_match = process.extractOne(unidecode(mun_name.strip()), mun_df['NM_MUNICIPIO'], scorer=fuzz.ratio, score_cutoff=min_score)
    #     if best_match:
    #         matched_row = mun_df[mun_df['NM_MUNICIPIO'] == best_match[0]]
    #         code = matched_row['CD_IBGE'].values[0]
    #         match_cache[mun_name] = code
    #         return code
    #     return None

    # tse_muni = locais_year_abbrev[['SG_UF', 'NM_MUNICIPIO', 'CD_MUNICIPIO']].drop_duplicates(subset='CD_MUNICIPIO', keep='first').rename(columns={'CD_MUNICIPIO': 'CD_TSE'})
    # tse_muni = tse_muni[tse_muni['SG_UF'] != 'ZZ']
    # ibge_muni = pd.read_csv(util_root + 'brasil_subdivision_gt.csv')[['UF', 'MUN', 'COD_MUN']].rename(columns={'UF': 'SG_UF', 'MUN': 'NM_MUNICIPIO', 'COD_MUN': 'CD_IBGE'})

    # print(tse_muni.shape)
    # print(ibge_muni.shape)

    # muni_map = tse_muni.copy()

    # for uf in ibge_muni['SG_UF'].unique():
    #     print(uf, end=' ')
    #     ref_df = ibge_muni[ibge_muni['SG_UF'] == uf]
    #     muni_map.loc[muni_map['SG_UF'] == uf, 'CD_IBGE'] = muni_map[muni_map['SG_UF'] == uf].apply(lambda row: fuzzy_match(row['NM_MUNICIPIO'], ref_df, min_score=40), axis=1)

    # muni_map['CD_IBGE'] = muni_map['CD_IBGE'].astype(int)

    # muni_map.to_csv(util_root + 'muni_TSE_IBGE_map.csv', index=False)
    # muni_map

    """# Adding the IBGE codes to the location data"""

    muni_map = pd.read_csv(project_root + 'utils/' + 'muni_TSE_IBGE_map.csv')

    # locais_year_grouped = pd.read_csv(project_root + 'eleitorado_local_votacao_2022_grouped.csv')

    locais_year_grouped = locais_year_grouped[locais_year_grouped['SG_UF'] != 'ZZ']

    locais_year_mapped = locais_year_grouped.merge(muni_map[['CD_IBGE', 'CD_TSE']], left_on='CD_MUNICIPIO', right_on='CD_TSE', how='left')
    locais_year_mapped.drop(columns=['CD_MUNICIPIO', 'NR_TURNO'], inplace=True)

    locais_year_mapped.to_csv(project_root + 'mapped/' + f'{file_name}_mapped.csv', index=False)
    locais_year_mapped

    """# create geodataframes"""

    # import geopandas as gpd
    # import pandas as pd
    # import numpy as np
    # from shapely.geometry import Point

    # locais_year_mapped = pd.read_csv(project_root + 'eleitorado_local_votacao_2022_mapped.csv')

    # locais_year_geo = gpd.GeoDataFrame(locais_year_mapped, geometry=gpd.points_from_xy(locais_year_mapped['NR_LONGITUDE'], locais_year_mapped['NR_LATITUDE']))
    # # turn points on -1, -1 into empty points
    # locais_year_geo.loc[locais_year_geo['NR_LONGITUDE'] == -1, 'geometry'] = Point(np.nan, np.nan)
    # locais_year_geo.to_file(project_root + 'eleitorado_local_votacao_2022_mapped.geojson', driver='GeoJSON')
    # locais_year_geo