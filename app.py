from shiny import App, render, ui
from model_rec import recommendation_eng  
from icons import piggy_bank, cart, item, eye, clock
import pandas as pd


df = pd.read_csv('purchase_history_modify.csv')
df_product_detail  = pd.read_csv('product_details.csv', sep = ';').dropna(how='all', axis=1)
df2 = df.merge(df_product_detail, on = 'product_id', how = 'left')

cust = pd.read_csv('customer_interactions.csv')

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            6, "", ui.input_numeric("id", "Customer Id", value =  1)),
        ui.column(
            6, "", ui.input_numeric("n", "Number of recommendation", value =  5))
            ) ,
    ui.row(
    ui.layout_column_wrap(
        ui.value_box(
            title = "Number of Transaction",
            value = ui.output_ui("trans_no"),
            showcase=item,
            theme="sky-blue",
            full_screen=True
        ),
        ui.value_box(
            title = "Total of Transaction Amount",
            value = ui.output_ui("trans_amt"),
            showcase=piggy_bank,
            theme="green",
            full_screen=True
        ),
        ui.value_box(
            title = "Total Page View",
            value = ui.output_ui("view"),
            showcase=eye,
            theme="bg-gradient-orange-cyan",
            full_screen=True
        ),
        ui.value_box(
            title = "Most Bought Product",
            value = ui.output_ui("prod"),
            showcase=cart,
            theme="pink",
            full_screen=True
        ),
        ui.value_box(
            title = "Time spent in Minutes",
            value = ui.output_ui("time"),
            showcase=clock,
            theme="red",
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
        rec = rec.rename(columns = {'product_id':'Product Id', 'category': 'Category',
                                    'price': 'Price', 'ratings': 'Ratings', 'rank of recommendation': 'Rank of Recommendation' })
        return render.DataTable(
            rec,  width='100%'
        )
    
    @render.text()
    def trans_no():
        return (df.customer_id == input.id()).sum()

    @render.text()
    def trans_amt():
        total_amt = df2[df2.customer_id == input.id()]['price'].sum()
        return human_format(total_amt)
    
    @render.text()
    def prod():
        value_cnt = df2[df2.customer_id == input.id()].category.value_counts()
        value = value_cnt[0]
        product = value_cnt.index[0]
        return f"{product} with {value} transactions"
    
    @render.text()
    def view():
        value_cnt = cust[cust.customer_id == input.id()].page_views.tolist()[0]
        return value_cnt
    
    @render.text()
    def time():
        value_cnt = cust[cust.customer_id == input.id()].time_spent.tolist()[0]
        return value_cnt
    
app = App(app_ui, server, debug=True)
