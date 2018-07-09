from dataUlt import *
from statsmodels.tsa.stattools import adfuller
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import talib
import ffn
from HdfUtility import HdfUtility
from matplotlib.backends.backend_pdf import PdfPages
import json
from Indicator_calculating import *

path = 'C:\\Users\\user\\GitHub\\Project1\\out.hdf5'
result_path = 'C:\\Users\\user\\GitHub\\Project1\\Test_Results'
hdf = HdfUtility()

def find_active_asset(asset_list):
    compari_all = []
    for excode,symbol in asset_list.items():
        for i in range(len(symbol)):
            rawdata = hdf.hdfRead(EXT_Hdf_Path,excode,symbol[i],'Rawdata',None,'1d',startdate=EXT_Start,enddate=EXT_End)
            ###排序规则：在整个样本期内，20天日均成交量为基准
            rawdata = rawdata.reset_index().sort_values(by = EXT_Out_Date, ascending = 1)
            rawdata = rawdata.groupby(EXT_Out_Date).sum()
            rawdata[EXT_Bar_Volume] = talib.MA(rawdata[EXT_Bar_Volume].values,timeperiod=20)
            compari_all.append([excode,symbol[i],rawdata[EXT_Bar_Volume].mean()])
    # sort_by_value
    compari_all.sort(key=lambda x:x[2],reverse=True)
    return compari_all[0:10]

def Ind_Stability(data,excode,Asset):
    '''
    Unit Root Test
    The null hypothesis of the Augmented Dickey-Fuller is that there is a unit
    root, with the alternative that there is no unit root. That is to say the
    bigger the p-value the more reason we assert that there is a unit root
    使用单位根检验
    ts只能输入一列
    输出值有 t统计量 p值 滞后阶数 观测值数量 1% 5% 10%分位点数 icbest
    '''
    dfOutputAll = pd.DataFrame([])
    temp = data.reset_index().dropna()
    if mode =='prod':
        temp['ret'] = (1+temp['ret']).cumprod()
    elif mode =='sum':
        temp['ret'] = (temp['ret']).cumsum()
    for i in data.columns:
        if 'ret' not in i:
            dftest = adfuller(temp[i])
            # 对上述函数输出值进行语义描述
            dfoutput = pd.Series(dftest[0:4], index = ['t_Statistic','p_value','lags_used','Obs_used'])
            for key,value in dftest[4].items():
                dfoutput['Critical Value (%s)' %key] = value
            dfoutput['icbest'] = dftest[5]
            dfOutputAll[i] = dfoutput
    dfOutputAll.T.to_csv(result_path+'\\'+excode+'_'+Asset+'_StabilityTest.csv')
    return dfOutputAll.T

def Ind_Eff(data,excode,Asset, mode = 'prod'):
    #mode为'sum'时累积收益率为累加
    #mode为'prod'时累积收益率为1+收益率的累乘
    #TimeSeries结构为：MultiIndex为时间和资产；有两列数据 ret 和对应所有的Ind
    #最大每页行数为MaxPlotNum
    MaxPlotNum = 6
    temp = data.reset_index().dropna()
    j = 0
    figsize = 10,15
    f = plt.figure(figsize = figsize)
    with PdfPages(result_path+'\\'+excode+'_'+Asset+'_Plot.pdf') as pdf:
        for i in data.columns:
            if 'ret' not in i:
                ##因子排序和收益率的
                TimeSeries = temp[[EXT_Bar_Date,'ret',i]]
                TimeSeries = TimeSeries.sort_values(by = i, ascending = 1)
                if mode =='prod':
                    TimeSeries['ret'] = (1+TimeSeries['ret']).cumprod()
                elif mode =='sum':
                    TimeSeries['ret'] = (TimeSeries['ret']).cumsum()
                df = TimeSeries[[i,'ret']].set_index([i])
                j = j+1
                ax = plt.subplot(MaxPlotNum,2,j)
                ax.plot(df)
                ax.set_xlabel(i,fontsize = 10/6.0*MaxPlotNum)
                ax.tick_params(labelsize=8/6.0*MaxPlotNum)
                ax.set_title('Cum_return orderd by Ind_'+i)
                xlabels = ax.get_xticklabels()
                #ax.suptitle()
                for xl in xlabels:
                    xl.set_rotation(30) #把x轴上的label旋转30度,以免太密集时有重叠
                ax.set_ylabel('cum_ret',fontsize = 10/6.0*MaxPlotNum)
                #现在只画前两个图
                ##因子的时间序列
                ts = TimeSeries[[i,EXT_Bar_Date]]
                ts = ts.sort_values(by = EXT_Bar_Date).set_index([EXT_Bar_Date])
                j = j+1
                ax = plt.subplot(MaxPlotNum,2,j)
                ax.plot(ts,marker='o', markersize = 1.3,linewidth = 1)
                ax.set_xlabel('Date',fontsize = 10/6.0*MaxPlotNum)
                ax.tick_params(labelsize=8/6.0*MaxPlotNum)
                ax.set_title('TimeSeries of Ind_'+i)
                xlabels = ax.get_xticklabels()
                for xl in xlabels:
                    xl.set_rotation(30) #把x轴上的label旋转15度,以免太密集时有重叠
            f.tight_layout()
            if (j % (MaxPlotNum*2) == 0 and j !=0):
                f.tight_layout()
                #plt.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0,wspace=0)
                plt.suptitle(Asset+'  Plot',fontsize=16/6.0*MaxPlotNum,x=0.52,y=1.03)#储存入pdf后不能正常显示
                pdf.savefig()
                plt.close()
                figsize = 10,15
                f = plt.figure(figsize = figsize)
                j = 0
            if i == data.columns[-1]:
                #plt.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0,wspace=0)
                pdf.savefig()
                plt.close()
    return
if __name__ =='__main__':
    # 因子的参数文件

    asset_list = {}
    asset_list[EXT_EXCHANGE_CFE] = EXT_CFE_ALL
    asset_list[EXT_EXCHANGE_SHFE] = EXT_SHFE_ALL
    asset_list[EXT_EXCHANGE_DCE] = EXT_DCE_ALL
    #asset_list[EXT_EXCHANGE_CZCE] = EXT_CZCE_ALL
    #按照交易量由高至低排列，得到排序后的active_asset
    ##排序规则：在整个样本期内，20天日均成交量为基准
    active_asset = find_active_asset(asset_list)
    list_Ind = param['Ind_func'] #技术指标列表
    for i in range(len(active_asset)):
        print(' '.join([active_asset[i][0],active_asset[i][1]]))
        df = hdf.hdfRead(path,active_asset[i][0],active_asset[i][1],'Stitch','00','1d',startdate = '20120101',enddate = '20171231')
        df[EXT_Bar_Close] = df[EXT_Bar_Close] * df[EXT_AdjFactor]
        df['ret'] = ffn.to_returns(df[EXT_Bar_Close])
        mode = 'prod'
        All_Ind = pd.DataFrame([])
        for Ind_func in list_Ind:
            Ind_temp = globals().get(Ind_func)(df.copy())
            if All_Ind.size == 0:
                All_Ind = Ind_temp
            else:
                All_Ind = All_Ind.merge(Ind_temp,left_index = True,right_index = True, how = 'outer')
        df = df[['ret']].merge(All_Ind,left_index = True,right_index = True, how = 'outer')
        dfOutputAll = Ind_Stability(df,active_asset[i][0],active_asset[i][1])
        df['ret'] = df['ret'].shift(-1)
        Ind_Eff(data = df,excode = active_asset[i][0],Asset = active_asset[i][1])
