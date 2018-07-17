# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 17:31:39 2018

@author: XRF96
"""
# import in-house lib
import updPosesHT4 as upd

# import python scientific stack
import pandas as pd
import numpy as np
import datetime

# import visual tools
import plotly.graph_objs as go
import plotly
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)

# import util libs
import ipywidgets as widgets
import warnings
warnings.filterwarnings("ignore")


def PortfolioViz1(start_date, end_date):
    
    print('Loading Data from {:%d,%b %Y} to {:%d,%b %Y}'.format(start_date, end_date))
    df = (upd.getPosesRpt(datetime.datetime.combine(start_date, datetime.time()), 
                         datetime.datetime.combine(end_date, datetime.time()),
                         1.0))
    
    ASSET_CLASS = list(df.AssetClass.unique())
    ASSET_CLASS.sort()
    FUNDS = ['DGA', 'ITX3']
    FIELDS = ['pl', 'dir', 'rv']

    
    def PlotDf(Fund, Asset_Class, Field, Managers):
        idx = pd.IndexSlice
        idx1 = idx[:, Fund, Asset_Class, :]
        dfmi = (pd.DataFrame(df.groupby([df.index.get_level_values(0), df.index.get_level_values(1), 'AssetClass', 'PM'])[Field]
                            .sum())
                .loc[idx1, :])
        
        try:
            print('Total {} from {:%d,%b %Y} to {:%d,%b %Y} = {:.2f} bp'.format(Field, 
                                                                              dfmi.index.get_level_values(0)[0],
                                                                              dfmi.index.get_level_values(0)[-1],
                                                                              dfmi[Field].sum()));
            print('Annual Vol from {:%d,%b %Y} to {:%d,%b %Y} = {:.2f} %'.format(dfmi.index.get_level_values(0)[0],
                                                                              dfmi.index.get_level_values(0)[-1],
                                                                              (dfmi[Field].sum(axis=0, level=[0]) / 100).std()
                                                                                        * np.sqrt(252)))
        except:
            print("Missing Values")
        
        #Data for the different managers
        trace_ALL = go.Scatter(x=list(dfmi.loc[idx1,:]
                                      .index.get_level_values(0)
                                      .drop_duplicates()),
                               y=list((dfmi.loc[idx[:, Fund, Asset_Class, :],:][Field]
                                       .groupby(level=[0, 1]).sum())
                                      .cumsum()),
                        name='ALL')
            
        trace_CHC = go.Scatter(x=list(dfmi.loc[idx[:, Fund, Asset_Class, 'CHC'],:]
                                      .index.get_level_values(0)
                                      .drop_duplicates()),
                               y=list((dfmi.loc[idx[:, Fund, Asset_Class, 'CHC'],:][Field]
                                       .groupby(level=[0, 1]).sum())
                                      .cumsum()),
                           name='CHC',
                           visible = False)

        trace_TAB = go.Scatter(x=list(dfmi.loc[idx[:, Fund, Asset_Class, 'TAB'],:]
                                      .index.get_level_values(0)
                                      .drop_duplicates()),
                               y=list((dfmi.loc[idx[:, Fund, Asset_Class, 'TAB'],:][Field]
                                       .groupby(level=[0, 1]).sum())
                                      .cumsum()),
                           name='TAB',
                           visible = False)


        trace_MLB = go.Scatter(x=list(dfmi.loc[idx[:, Fund, Asset_Class, 'MLB'],:]
                                      .index.get_level_values(0)
                                      .drop_duplicates()),
                               y=list((dfmi.loc[idx[:, Fund, Asset_Class, 'MLB'],:][Field]
                                       .groupby(level=[0, 1]).sum())
                                      .cumsum()),
                           name='MLB',
                           visible = False)

        data = [trace_ALL, trace_CHC, trace_TAB, trace_MLB]

        updatemenus = list([
            dict(active=0,
                 buttons=list([   
                    dict(label = 'ALL',
                         method = 'update',
                         args = [{'visible': [True, False, False, False]},
                                 {'title': 'Fund {} - Cumulative {} for ALL PM'.format(Fund, Field)}]),
                    dict(label = 'CHC',
                         method = 'update',
                         args = [{'visible': [False, True, False, False]},
                                 {'title': 'Fund {} - Cumulative {} for CHC'.format(Fund, Field)}]),
                    dict(label = 'TAB',
                         method = 'update',
                         args = [{'visible': [False, False, True, False]},
                                 {'title': 'Fund {} - Cumulative {} for TAB'.format(Fund, Field)}]),
                    dict(label = 'MLB',
                         method = 'update',
                         args = [{'visible': [False, False, False, True]},
                                 {'title': 'Fund {} - Cumulative {} for MLB'.format(Fund, Field)}]),
                ]),
            )
        ])

        layout = go.Layout(
            dict(title='Fund {} - Cumulative {} All PM Included'.format(Fund, Field), showlegend=False,
                      updatemenus=updatemenus),
            yaxis=dict(
                side='right'),
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label='1m',
                             step='month',
                             stepmode='backward'),
                        dict(count=6,
                             label='6m',
                             step='month',
                             stepmode='backward'),
                        dict(count=1,
                            label='YTD',
                            step='year',
                            stepmode='todate'),
                        dict(count=1,
                            label='1y',
                            step='year',
                            stepmode='backward'),
                        dict(step='all')
                    ])
                ),
            )
        )
        
        fig = dict(data=data, layout=layout)
        iplot(fig, filename='update_dropdown')


        
        
        #PlotLy Graph2 Asset BreakDown
        trace = []
        for i in range(len(Asset_Class)):
            if Managers == 'ALL':
                trace_i = go.Scatter(x=list(dfmi.loc[idx[:, Fund, Asset_Class[i], :],:]
                                            .index.get_level_values(0)
                                            .drop_duplicates()),
                                     y=list((dfmi.loc[idx[:, Fund, Asset_Class[i], :],:][Field]
                                             .groupby(level=[0, 1]).sum())
                                            .cumsum()),
                                     name=Asset_Class[i]
                                      )
                trace.append(trace_i)
            else:
                trace_i = go.Scatter(x=list(dfmi.loc[idx[:, Fund, Asset_Class[i], Managers],:]
                                            .index.get_level_values(0)
                                            .drop_duplicates()),
                                     y=list((dfmi.loc[idx[:, Fund, Asset_Class[i], Managers],:][Field]
                                             .groupby(level=[0, 1]).sum())
                                            .cumsum()),
                                     name=Asset_Class[i]
                                      )
                trace.append(trace_i)
        data = trace
        layout = go.Layout(
            dict(title='Fund {} - Cumulative {} AssetClass Breakdown for {}'.format(Fund, Field, Managers),
                ),
            yaxis=dict(
                side='right'),
            legend=dict(
            x=-10,
            y=1),
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label='1m',
                             step='month',
                             stepmode='backward'),
                        dict(count=6,
                             label='6m',
                             step='month',
                             stepmode='backward'),
                        dict(count=1,
                            label='YTD',
                            step='year',
                            stepmode='todate'),
                        dict(count=1,
                            label='1y',
                            step='year',
                            stepmode='backward'),
                        dict(step='all')
                    ])
                ),
            )
        )
        
        fig = dict(data=data, layout=layout)
        iplot(fig)

    #Widgets 
    AssetClassW = widgets.SelectMultiple(
        options=ASSET_CLASS,
        value=ASSET_CLASS,
        rows=len(ASSET_CLASS),
        description='AssetClass',
        disabled=False
    )

    ManagersW = widgets.RadioButtons(
        options=['ALL', 'CHC', 'TAB', 'MLB'],
        value='ALL',
        description='PM:',
        disabled=False
    )
    
    widgets.interact(PlotDf,
                        Fund = FUNDS,
                        Asset_Class = AssetClassW,
                        Field = FIELDS,
                        Managers = ManagersW
                        );
                     
                     
def PortfolioViz2(start_date, end_date):
    
    print('Loading Data from {:%d,%b %Y} to {:%d,%b %Y}'.format(start_date, end_date))
    df = (upd.getPosesRpt(datetime.datetime.combine(start_date, datetime.time()), 
                         datetime.datetime.combine(end_date, datetime.time()),
                         1.0))
    
    ASSET= list(df.Asset.unique())
    ASSET.sort()
    FUNDS = ['DGA', 'ITX3']

    
    def GetData(Fund, Asset, Managers):
        Field = ['dir','rv']
        idx = pd.IndexSlice
        if Managers == 'ALL':
            idx1 = idx[:, Fund, Asset, :, :]
        else:
            idx1 = idx[:, Fund, Asset, Managers, :]
            
        dfmi = (pd.DataFrame(df.groupby([df.index.get_level_values(0), df.index.get_level_values(1), 'Asset', 'PM', 'Code'])
                             .agg({'dir':'sum','rv':'sum'}))
                .loc[idx1, :]).dropna()
        print(dfmi.head())
        
        CODE = list(dfmi.index.get_level_values(4).unique())
        CODE.sort()
            

        def GetPlot(Code):            
            try:
                #PlotLy Graph Code Breakdown
                trace = []
                for i in range(len(Code)):
                    if Managers == 'ALL':
                        trace_i = go.Scatter(x=list(dfmi.loc[idx[:, :, :, :, Code[i]],:]
                                                    .index.get_level_values(0)
                                                    .drop_duplicates()),
                                             y=list((dfmi.loc[idx[:, :, :, :, Code[i]],:][Field[1]]
                                                     .groupby(level=[0, 1]).sum())
                                                    .cumsum()),
                                             name=Code[i]
                                              )
                        trace.append(trace_i)
                    else:
                        trace_i = go.Scatter(x=list(dfmi.loc[idx[:, :, :, Managers, Code[i]],:]
                                                    .index.get_level_values(0)
                                                    .drop_duplicates()),
                                             y=list((dfmi.loc[idx[:, :, :, Managers, Code[i]],:][Field[1]]
                                                     .groupby(level=[0, 1]).sum())
                                                    .cumsum()),
                                             name=Code[i]
                                              )
                        trace.append(trace_i)
                data = trace
                print(len(trace))

                layout = go.Layout(
                    dict(title='Fund {} - Cumulative {} Code Breakdown for {}'.format(Fund, Field[1], Managers),
                        ),
                    yaxis=dict(
                        side='right'),
                    legend=dict(
                    x=-10,
                    y=1),
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1,
                                     label='1m',
                                     step='month',
                                     stepmode='backward'),
                                dict(count=6,
                                     label='6m',
                                     step='month',
                                     stepmode='backward'),
                                dict(count=1,
                                    label='YTD',
                                    step='year',
                                    stepmode='todate'),
                                dict(count=1,
                                    label='1y',
                                    step='year',
                                    stepmode='backward'),
                                dict(step='all')
                            ])
                        ),
                    )
                )

                fig = dict(data=data, layout=layout)
                iplot(fig)
 
                
            except:
                print("Missing Values")
                       
             #Widgets 
        CodeW = widgets.SelectMultiple(
        options=CODE,
        value=CODE,
        rows=6,
        description='Code',
        disabled=False
        )
            
        widgets.interact(GetPlot,
                        Code = CodeW
                        );
        
    #Widgets 
    AssetW = widgets.SelectMultiple(
        options=ASSET,
        value=ASSET,
        rows=len(ASSET),
        description='Asset',
        disabled=False
    )

    ManagersW = widgets.RadioButtons(
        options=['ALL', 'CHC', 'TAB', 'MLB'],
        value='ALL',
        description='PM:',
        disabled=False
    )
    
    
    widgets.interact(GetData,
                        Fund = FUNDS,
                        Asset = AssetW,
                        Managers = ManagersW
                        );