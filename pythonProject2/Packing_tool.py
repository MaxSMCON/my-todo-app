from PackagingToll import *

# Import
import pandas as pd
import math
import numpy as np

names = locals()
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import statistics
# from GenerateHourlyPlan import *
import pyodbc as odbc

# Import Data
# Sequence table
# seq=pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/Activities.xlsx", sheet_name='Product Seqeunce')
server = 'cmpcsb01'
database = 'conestoga'
username = 'remotequery'
password = "excel"
cnxn = odbc.connect(
    'DRIVER={SQL Server}; SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password,
    trusted_connection='no'
)
cursor = cnxn.cursor()

query = '''select 
           convert(INT, bomkey) as BomKey,
           CONVERT(INT, sequenceno) as SequenceNo,
            CONVERT(INT, ActivityFunctionKey) as ActivityFunctionKey,
            CONVERT(INT, DurationMinutes) as DurationSeconds

   FROM [conestoga].[dbo].[DimBOMActivitiesFunctions]
    where BomKey>10000
    '''

seq = pd.read_sql(query, cnxn)

# Maximum Capacity
# cap=pd.read_excel("ActiviActivity Cap Modties.xlsx", sheet_name='Activity Cap')
# cap=pd.read_excel("Files/Activities_adjust.xlsx", sheet_name='Activity Cap')
cap = pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Activities_adjust.xlsx",
                    sheet_name='Activity Cap Mod')

# Products and Meat Relationship Table
# ProdMeat=pd.read_excel("Files/Activities.xlsx",
#                     #    sheet_name='Products and Meat'
#                     sheet_name='dataProdMeat'
#                        )
# print(ProdMeat.shape)

server = 'cmpcsb01'
database = 'conestoga'
username = 'remotequery'
password = "excel"
cnxn = odbc.connect(
    'DRIVER={SQL Server}; SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password,
    # trusted_connection='yes'
    )
cursor = cnxn.cursor()
# print(cursor)
query = '''SELECT 
              CAST(Itemkey as int) as FinishedGoodProductCode, 
              --Pieces, 
              Cast(ItemSort4Key as INT) as MeatItem
               FROM dimitem
               WHERE Itemkey >  ? and Itemkey < ?
               --and ItemSort4Key > 0
               '''
ProdMeat = pd.read_sql(query, cnxn,
                       params=['10000', '39999']
                       )

# ProdMeat.head()
# print("ss", ProdMeat.shape)


# Four Priority Requirement
# req = pd.read_excel("Files/req wihtout byproducts.xlsx")
req = pd.read_excel("Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/req wihtout byproducts.xlsx",
                    sheet_name='data (2)')
# req = pd.read_excel("Files/Cut Sheet 20221024", sheet_name='Sheet2' )

# Priority Meat Input
# meat=pd.read_excel("Files/Meats.xlsx",  sheet_name ='Priority Meat Input') #delected the byproduct,
# meat=pd.read_excel("Files/Meats_adjust_v3.xlsx",  sheet_name ='Priority Meat Input') #delected the byproduct,
# meat=pd.read_excel("Files/Meats_adjust_v3.xlsx",  sheet_name ='meat prior') #delected the byproduct,


server = 'cmpcsb01'
database = 'packagingplanner'
username = 'remotequery'
password = "excel"
cnxn = odbc.connect(
    'DRIVER={SQL Server}; SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password,
    trusted_connection='no'
    )
cursor = cnxn.cursor()
print(cursor)

query = '''SELECT 

   cast(MeatItem as INT) as Meat, 
   SUM(P1) AS 'Priority 1', 
   SUM(P2) AS 'Priority 2', 
   SUM(P3) AS 'Priority 3', 
   SUM(P4) AS 'Priority 4'
   FROM     vwPrepForCutInputPriorities
   where productiondate= ? and MeatItem < ?
   GROUP BY MeatItem'''
meat = pd.read_sql(query, cnxn,
                   params=['20230428', 800]
                   )

# Hourly Meat Input
# meat_hourly = pd.read_excel("Files/hourly_meat_input.xlsx",index_col = 0)
# Original File
# meat_hourly = pd.read_excel(
#     # "Files/hourly_meat_input_adjustment_v3.xlsx",index_col = 0, sheet_name='Sheet1'
#     "Q:\Operations\Industrial Engineering\Maxim\Packaging tool\Files/PackagingSimulationInputs v4.xlsx", index_col=0,
#     sheet_name='Summ'
# )
meat_hourly = pd.read_excel(
    # "Files/hourly_meat_input_adjustment_v3.xlsx",index_col = 0, sheet_name='Sheet1'
    "Q:\Supply Chain\Public\Packaging Capacity Team\PackagingSimulationInputs v5.xlsx", index_col=0,
    sheet_name='Summ'
)
meat_hourly = meat_hourly.fillna(0)
meat_hourly = meat_hourly.astype(int)

# relationship between hour and priority
## key represents hour, value represents priority
hour_priority = {
    6: 1,
    7: 1,
    8: 1,
    9: 1,
    10: 1,
    11: 1,
    12: 1,
    13: 1,
    14: 1,
    15: 2,
    16: 2,
    17: 3,
    18: 3,
    19: 4,
    20: 4,
    21: 4,
    22: 4
}

# List Of Chilled

# Write loop to exlude for missing meat items and let program to go


# the code
meat_hourly.columns = np.dtype('int64').type(meat_hourly.columns)
# Some products have 0 PiecesInBox, these skus are also excluded
req = req.loc[req["PiecesInBox"] != 0, :]
print(req)
# meat_hourly
print(meat_hourly)
# # exclude byproduct(just include meat_id in Meat table)
meat_hourly = meat_hourly.loc[:, list(meat.Meat.values)]
meat_hourly = meat_hourly.loc[:, list(meat.Meat.values)]

# print(meat_hourly)
# #combine meat inputs and requirements
meat_and_req = req.merge(ProdMeat, left_on='itemkey', right_on='FinishedGoodProductCode', how='left')
#
# Friltering Chilled pork Item from meat and requirements
chilled_pork = [148, 152, 348, 352, 353, 460, 461, 702, 762, 784, 786, 787]
meat_and_req = meat_and_req[~meat_and_req['MeatItem'].isin(chilled_pork)]

meat_hourly = meat_hourly[meat_hourly.columns[~meat_hourly.columns.isin(chilled_pork)]]

# print(meat_and_req.head())

# meat_pieces_check(ProdMeat, req, meat)
activity_time_check(req, hour_priority, cap, seq)
#
# # Function 7
method1_adjusting_rate_list = [0.01, 0.03]
method2_combo_ratio_list = [0.3, 0.7]
method2_adjusting_rate_list = [0.01]
result, best_plan = get_best_plan(meat_and_req,
                                  meat_hourly,
                                  hour_priority,
                                  cap,
                                  seq,
                                  req,
                                  method1_adjusting_rate_list,
                                  method2_combo_ratio_list,
                                  method2_adjusting_rate_list)

print(result)

hourly_total_position_stdev(best_plan, cap, hour_priority, seq, plot=True)

OEE, OEE_table = EEO_caculation(best_plan, cap, hour_priority, seq)
print(OEE_table)

# visualize_estimated_position_num(best_plan,cap,hour_priority,seq)


hourly_packaging_plan_method1, requirements_not_complete_method1 = plan_break_down(meat_and_req, meat_hourly,
                                                                                   hour_priority)
print(hourly_packaging_plan_method1)

# save the best plan
best_plan.to_excel("best_plan.xlsx")

hourly_packaging_plan_method1, requirements_not_complete_method1 = plan_break_down(meat_and_req, meat_hourly,
                                                                                   hour_priority)
print(hourly_packaging_plan_method1)

new_plan, new_infeasible_table = adjust_infeasible_plan(hourly_packaging_plan_method1, req, cap, seq, hour_priority,
                                                        adjusting_rate=0.01)

# hourly_total_position_stdev(hourly_packaging_plan_method1,cap,hour_priority,seq,plot=True)

hourly_total_position_stdev(new_plan, cap, hour_priority, seq, plot=True)
