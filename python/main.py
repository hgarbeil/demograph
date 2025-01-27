
import pandas as pd 
import numpy as np 
import geopandas as gpd
import requests  

states_fips = ['33','50','25','36','23','42','53','41','27']
snames = ['New Hampshire','Vermont','Massachusetts','New York', 'Maine','Pennsylvania','Washington','Oregon','Minnesota']

infile = '../data/election_2024.csv'
unempfile = '../data/laucntycur14.txt' 
taxfile = '../data/taxes.csv'
difile = '../data/cc-est2023-alldata.csv'

didf = pd.read_csv(difile,encoding = "ISO-8859-1")
print(didf.columns)
didf=didf[(didf.YEAR ==4) & (didf.AGEGRP==0)]
didf=didf[didf.STNAME.isin(snames)]
didf['fips']=didf.STATE*1000+didf.COUNTY

didf['percent_nonwhite']=100-((didf.WA_MALE+didf.WA_FEMALE)*1./didf.TOT_POP*100.)
didf=didf[['fips','TOT_POP','percent_nonwhite']]
print(didf.head(40)) 

df = pd.read_csv(infile)
df_geom = gpd.read_file('../data/geojson-counties-fips.json')
df_geom_nh = df_geom[df_geom.STATE.isin(states_fips)] 
df_geom_nh['id']=df_geom_nh['id'].astype(np.int64)
#print(df.head())

df_taxes = pd.read_csv(taxfile)
df_taxes=df_taxes[df_taxes.state.isin(snames)]
df_taxes.dropna(inplace=True)
df_taxes.drop(columns=['perc_change','perc_change_ia','perc_change_ia.1','perc_change_ia.2','perc_change_ia.3','perc_change_ia.4'],inplace=True)
print(df_taxes.columns)

df_unemp = pd.read_csv(unempfile,skiprows=6,sep='|',skipinitialspace=True)
df_unemp.dropna(inplace=True)
df_unemp.columns=['id','state_f','county_f','county','date','total','employed','unemployed','unemp_rate']
df_unemp['fips_code']=(df_unemp['state_f'].astype(np.int32)*1000+
                       df_unemp['county_f'].astype(np.int32)).astype(np.int64)
df_unemp=df_unemp.drop(columns=['id','state_f','county_f','county','total'])
df_unemp_year=df_unemp[df_unemp.date == (df_unemp['date'].max())]
print(df_unemp_year.head())


df_nh = df[df['state_name'].isin(snames)]
print(df_nh.columns)
df_nh.drop(columns=['state_name','diff','county_name','per_point_diff'],inplace=True)

df_gdf = df_geom_nh.merge(df_nh, left_on='id',right_on='county_fips')

df_gdf = df_gdf.merge(df_unemp_year, left_on='id',right_on='fips_code')
df_gdf = df_gdf.merge(df_taxes,left_on='id',right_on='fips_code')
df_gdf =df_gdf.merge(didf,left_on='id',right_on='fips')
print(df_gdf.columns)




#print(df_geom_nh.head(10) )
# print (df_nh.info())
# print (df_geom_nh.info())

# df_election_gdf.to_file('../data/nh_election_geo.json',driver='GeoJSON')
# df_unemp_year.to_file('../data/ne_unemp_geo.json',driver='GeoJSON')
df_gdf.to_file('../data/merged_gdf.json', driver='GeoJSON')