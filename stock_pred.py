#required modules

import numpy as np
import pandas as pd
#pip install yfinance --upgrade --no-cache-dir
import yfinance as yf
import time
import os
import plotly
import ipywidgets as widgets
from ipywidgets import interactive,interact, HBox, Layout,VBox
from datetime import date,timedelta
import plotly.graph_objects as go
#conda install -c conda-forge fbprophet
from fbprophet import Prophet

class stock_pred():
    def __init__(self):
        self.data_list = [s for s in os.listdir() if s[-4:]=='.csv']
        self.tick_val = self.get_stock_id()
    def get_stock_id(self,data_string="https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"):
        df = pd.read_html(data_string) 
        self.tick_val = df[0][["Security","Symbol"]].values
        return self.tick_val
    def dwld_data(self):
        st_id = widgets.Dropdown(options=self.tick_val[:,0],value=self.tick_val[:,0][0],description='StockID',disabled=False,)
        from_date = widgets.DatePicker(description='From ... to ... ',disabled=False,value=date.today()-timedelta(days=365))
        to_date = widgets.DatePicker(description='',disabled=False,value=date.today()-timedelta(days=1))
        get_downld = widgets.ToggleButton(value=False,description='Download',disabled=False,button_style='info',tooltip='Description',icon='download')
        def dwld_dat(opt):
            stock_id = self.tick_val[:,1][self.tick_val[:,0]==st_id.value]
            data = yf.download(stock_id[0], start=from_date.value, end=to_date.value)
            data_str = str(stock_id[0])+"_"+str(from_date.value)+"_"+str(to_date.value)+".csv"
            data.to_csv(data_str,index=True)
            print("Data saved as: "+data_str)
        display(widgets.HBox([st_id,from_date, to_date,get_downld],flex='flex-grow'))
        get_downld.observe(dwld_dat, 'value')
    def plot_stock(self):
        def f(Stock_Data):
            inp = pd.read_csv(Stock_Data)
            fig = go.Figure(data=[go.Candlestick(x=inp.Date,
                open=inp['Open'],
                high=inp['High'],
                low=inp['Low'],
                close=inp['Close'])])
            title_name = self.tick_val[:,0][self.tick_val[:,1]==Stock_Data.split("_")[0]][0]
            fig.layout.update(xaxis_rangeslider_visible=False,title=title_name)
            fig.show()
        interact(f, Stock_Data=self.data_list)
    def pred_stock(self):
        def f(Weeks_Forecast,Stock_Data):
            title_name = self.tick_val[:,0][self.tick_val[:,1]==Stock_Data.split("_")[0]][0]
            inp = pd.read_csv(Stock_Data).rename(columns={"Date" : "ds","Adj Close" : "y"})
            m = Prophet(yearly_seasonality=True,daily_seasonality=False)
            m.fit(inp)
            future = m.make_future_dataframe(periods=Weeks_Forecast*7)
            forecast = m.predict(future)
            fig = m.plot(forecast)
            ax = fig.gca()
            ax.set_title(title_name, size=34)
            fig = m.plot_components(forecast)
        w = interactive(f, Weeks_Forecast=widgets.IntSlider(min=0, max=104, step=1, value=1, continuous_update=False, description="Weeks"), Stock_Data=self.data_list)
        controls = HBox(w.children[:-1],flex='flex_flow')
        output = w.children[-1]
        display(VBox([controls, output]))
