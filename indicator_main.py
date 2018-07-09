# encoding:utf-8


# test the single Indicator 

from Indicator_Base import Indicator_Fetch
from dataUlt import (EXT_CFE_ALL,EXT_SHFE_ALL, EXT_DCE_ALL)
from Indicator_testing import find_active_asset,Ind_Stability,Ind_Eff

if __name__ == '__main__':
    with open('Indicator_setting.json','r') as f:
        param = json.load(f)
    
    asset_list[EXT_EXCHANGE_CFE] = EXT_CFE_ALL
    asset_list[EXT_EXCHANGE_SHFE] = EXT_SHFE_ALL
    asset_list[EXT_EXCHANGE_DCE] = EXT_DCE_ALL

    List_Asset = find_active_asset(asset_list)
    List_Ind= param['Ind_func']
    
    window_prd = 15
    vt = ['IF']
    excode = ['CFE']
    for i in List_Asset:
        excode = i[0]
        vt = i[1]
        for j in List_Ind:
            indicator_name = j
    #excode = ['CFE']*len(EXT_CFE_ALL) + ['SHFE']*len(EXT_SHFE_ALL) + ['DCE']*len(EXT_DCE_ALL)
    #vt = EXT_CFE_ALL + EXT_SHFE_ALL + EXT_DCE_ALL
    Setting = {'data_setting':{'startdate':'20120101', 'enddate':'20171231', 'vt' : vt, 'excode': excode,
               'COLUMNS':['datetime', 'AdjFactor', 'Open', 'Low', 'High', 'Close', 'Delistdate'],
               'loading_datatype':{'domdata':True, 'subdomdata':False, 'rawdata':False, 'extradata':False} },
               'indsave':True
               }
    #indicator_fetch = Indicator_Fetch()
    Indicator_Fetch.run_indicator(indicator_name= indicator_name, indicator_params = {'window_prd':window_prd}, SETTING = Setting)
    
    

