
from sklearn.neighbors import KNeighborsRegressor
import pandas as pd

def recommendation_eng(df):
    to_knn = df.groupby(['customer_id', 'product_id'])['purchase_date'].count().reset_index().pivot(index = 'customer_id', 
                                                                                             columns= 'product_id',  values = 'purchase_date')

    # Get the average rating for each user 
    avg_ratings = to_knn.mean(axis=1)

    # Center each users ratings around 0
    user_ratings_table_centered = to_knn.apply(lambda x: x-avg_ratings, axis=0)

    # Fill in the missing data with 0s
    to_knn_fill = user_ratings_table_centered.fillna(0)

    prod_l = []
    usr_l = []
    pred_l = []
    for i in [101, 102, 103, 104, 105]:
        for j in range(1, 6, 1):
            df_knn = to_knn_fill.drop(i, axis=1)
            target_user_x = df_knn.loc[[j]]
            # Get the target data from user_ratings_table
            other_users_y = to_knn[i]

            # Get the data for only those that have seen the movie
            other_users_x = df_knn[other_users_y.notnull()]
            other_users_y.dropna(inplace=True)

            # Instantiate the user KNN model
            user_knn = KNeighborsRegressor(metric='cosine', n_neighbors= 2)

            # Fit the model and predict the target user
            user_knn.fit(other_users_x, other_users_y)
            user_user_pred = user_knn.predict(target_user_x)
            prod_l.append(i)
            usr_l.append(j)
            pred_l.append(user_user_pred[0])

    df_pred = pd.DataFrame({'product_id':prod_l, 'customer_id':usr_l, 'buy_prediction': pred_l})

    #piv_pred = df_pred.pivot(index = 'customer_id', columns= 'product_id', values= 'buy_prediction')
    
    return df_pred