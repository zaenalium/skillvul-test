import seaborn as sns
from palmerpenguins import load_penguins
from shiny import App, render, ui
from model_rec import recommendation_eng  
from icons import piggy_bank, cart, item
import pandas as pd


df = pd.read_csv('purchase_history_modify.csv')
df_product_detail  = pd.read_csv('product_details.csv', sep = ';').dropna(how='all', axis=1)

app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            6, "", ui.input_numeric("id", "User Id", value =  1)),
        ui.column(
            6, "", ui.input_numeric("n", "Number of recommendation", value =  5))
            ) ,
    ui.row(
    ui.layout_column_wrap(
        ui.value_box(
            "Number of Transaction",
            "5 items",
            showcase=piggy_bank,
            theme="bg-gradient-orange-cyan",
            full_screen=True
        ),
        ui.value_box(
            "Total of Transaction",
            "$200",
            showcase=cart,
            theme="text-green",
            showcase_layout="top right",
            full_screen=True
        ),
        ui.value_box(
            "Most Bought Product",
            "$1 Billion Dollars",
            showcase=item,
            theme="purple",
            showcase_layout="top right",
            full_screen=True
        ),
        ui.value_box(
            "Total Page View",
            "1000",
            showcase=piggy_bank,
            theme="bg-gradient-orange-cyan",
            full_screen=True
        ),
        ui.value_box(
            "Time spent in minutes",
            "100",
            showcase=cart,
            theme="text-green",
            showcase_layout="top right",
            full_screen=True
           
        )
    )
    ),
    ui.output_data_frame("recomend_tbl") 
    
)

def server(input, output, session):  

    @render.data_frame()  
    def recomend_tbl():  
        df_rec = recommendation_eng(df)
        rec = df_rec[df_rec.customer_id == input.id()][['product_id', 'buy_prediction']]
        rec['recommendation score'] = (rec['buy_prediction']/rec['buy_prediction'].sum()).round(3) * 100 
        rec = rec.merge(df_product_detail, on = 'product_id', how = 'left')
        rec = rec[['product_id', 'category','price', 'ratings', 'recommendation score']].sort_values('recommendation score', ascending = False)
        rec.drop('recommendation score', axis = 1, inplace = True)
        rec['rank of recommendation'] = list(range(1, 6 ,1))
        rec = rec[rec['rank of recommendation'] <= input.n()]
        return render.DataTable(
            rec,  width='100%'
        )
    

app = App(app_ui, server, debug=True)
