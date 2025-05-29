import pandas as pd
import pickle
import os, requests, json

# load models
models = {}

model_dir = "./models"
for file in os.listdir(model_dir):
    if file.endswith(".pkl"):
        model_path = os.path.join(model_dir, file)
        with open(model_path, 'rb') as f:
            model_name = file.replace(".pkl", "")
            models[model_name] = pickle.load(f)



def get_data(ticker, period = "h6"):
    url = f"https://tornsy.com/api/{ticker}?interval={period}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")
    data = response.json()
    # print(data)
    df = pd.DataFrame(data["data"], columns=["Timestamp", "Opening Price", "Closing Price", "High Price", "Low Price", "No of Shares"])
    df = df.sort_values(by="Timestamp", ascending=True)
    return df

time_periods = {
    "d1": 24,
    "h6": 6,
    "h1": 1,
    "m30": 0.5,
}

stock_predictions = {}

def predict_n_future(X, model, n = 1):
    predictions = []
    for _ in range(n):
        
        pred = model.predict(X)
        predictions.append(pred[0])
        
        
        # Shift the previous lags
        for i in range(9, 1, -1):
            X[f"lag_{i}"] = X[f"lag_{i-1}"]
        
        # update first lag with current low price
        X["lag_1"] = X["Low Price"].values[0]
        # update low price with predicted value
        X["Low Price"] = pred[0] 
        # print(X)  

    return predictions



for modelName in models:
    stockName = modelName.split("_")[0]
    stock_period = modelName.split("_")[1]
    print(f"Predicting for {stockName} using model {modelName}")
    df = get_data(stockName, period=stock_period)

    # generate 10 lags for the latest data
    for i in range(1, 10):
        df[f"lag_{i}"] = df["Low Price"].shift(i)
    df = df.dropna()
    
    # X
    X = df.tail(1).drop(columns=["Timestamp", "Opening Price", "Closing Price", "High Price", "No of Shares"])

    # print(X)

    no_of_iterations = int(24 / time_periods[stock_period])
    
    # predict
    predictions = predict_n_future(X.copy(), models[modelName], n=no_of_iterations)
    print(predictions)
    # get the last prediction
    prediction = predictions[-1]

    if stockName not in stock_predictions:
        stock_predictions[stockName] = []
    

    current_price = float(X["Low Price"].values[0])

    change = float(prediction) - current_price
    changeperc = (change / current_price) * 100

    stock_predictions[stockName] += [changeperc]

    print(f"Current: {current_price}, Predicted: {prediction}, Change: {changeperc:.2f}%")
    if changeperc > 0.3:
        print(f"####  Buy {stockName} ####")

print(stock_predictions)

# get the average from different prediction
for stockName in stock_predictions:
    avg = sum(stock_predictions[stockName]) / len(stock_predictions[stockName])
    print(f"{stockName} average prediction: {avg}%")


