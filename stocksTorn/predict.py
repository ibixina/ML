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


for modelName in models:
    stockName = modelName.split("_")[0]
    print(f"Predicting for {stockName} using model {modelName}")
    df = get_data(stockName)

    # generate 10 lags for the latest data
    for i in range(1, 10):
        df[f"lag_{i}"] = df["Low Price"].shift(i)
    df = df.dropna()
    
    # latest
    latest_data = df.tail(1).drop(columns=["Timestamp", "Opening Price", "Closing Price", "High Price", "No of Shares"])
    
    # predict
    prediction = models[modelName].predict(latest_data)
    current_price = float(latest_data["Low Price"].values[0])

    change = float(prediction[0]) - current_price
    changeperc = (change / current_price) * 100
    print(f"Current Price: {current_price}, Predicted Price: {prediction[0]}, Change: {change}, Change Percentage: {changeperc:.2f}%")
    if changeperc > 0.5:
        print(f"####  Buy {stockName} ####")
    # break


