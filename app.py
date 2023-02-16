import os 
import pandas as pd
from flask import Flask, render_template
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table

app = Flask(__name__)

AAD_TENANT_ID = "e08c9822-9be7-4536-9a98-e6b5f3242944"
KUSTO_CLUSTER = "https://loupedatacluster.northeurope.kusto.windows.net/"
KUSTO_DATABASE = "telemetry"
SECRET_VAL = ###
APP_ID = "aa594798-f9ec-4f95-b298-e3e34c3a6a01"

KCSB = KustoConnectionStringBuilder.with_aad_application_key_authentication(
    KUSTO_CLUSTER, APP_ID, SECRET_VAL, AAD_TENANT_ID)   
KCSB.authority_id = AAD_TENANT_ID
KUSTO_CLIENT = KustoClient(KCSB)
KUSTO_QUERY = "AppExceptions | take 1000"
RESPONSE = KUSTO_CLIENT.execute(KUSTO_DATABASE, KUSTO_QUERY)

df = dataframe_from_result_table(RESPONSE.primary_results[0])
df = pd.json_normalize(df['records'])
df = pd.json_normalize(df[0])

series = df['Properties.SystemVersion']
pie = series.value_counts().plot(
   kind='pie', shadow=True, figsize=(8,8), 
   xlabel='', labeldistance=None,
   ylabel='').get_figure()
pie.suptitle('Properties.SystemVersion', fontsize=15, y=1.03)
pie.legend(bbox_to_anchor=(1, 1.02), loc='upper left')
pie.savefig(os.getcwd() + "/static/images/graph.png",  bbox_inches='tight')
pie.clf()

series = df['Properties.LoupedeckBuild']
pie = series.value_counts().plot(
   kind='bar', figsize=(8,8), rot=0).get_figure()
pie.suptitle('Properties.LoupedeckBuild', fontsize=15)
pie.savefig(os.getcwd() + "/static/images/graph2.png",  bbox_inches='tight')

# Draw graph

@app.route('/')
def index():
    num_rec = len(df)
    print('Request for index page received')
    return render_template('index.html', num_rec = num_rec)

if __name__ == '__main__':
    app.run()
