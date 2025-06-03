import pandas as pd
import pickle
import os, requests, json

# load models
models = {}

RESET = '\033[0m'
RED = "\033[91m"
GREEN = "\033[92m"

model_dir = "./models"
for file in os.listdir(model_dir):
    if file.endswith(".pkl"):
        model_path = os.path.join(model_dir, file)
        with open(model_path, 'rb') as f:
            model_name = file.replace(".pkl", "")
            models[model_name] = pickle.load(f)


def print_row(data, type = 0, spacing = 10, color = RESET):
# type 0: row, type 1: header, type 2: footer
    row ="|"
    for d in data:
        row += str(d).rjust(spacing) + " |"

    if type == 1:
        print("-" * len(row))

    print(color + row + RESET)

    if type == 1:
        print("-" * len(row))
    

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


period = "d1"
headers = ["Stock", "Current", "Predicted", "Change %", "ModelName"]
print_row(headers, type=1)
for modelName in models:
    if period not in modelName: continue
    stockName = modelName.split("_")[0]
    df = get_data(stockName, period)

    # generate 10 lags for the latest data
    for i in range(1, 10):
        df[f"lag_{i}"] = df["Low Price"].shift(i)
    df = df.dropna()
    
    # latest
    latest_data = df.tail(1).drop(columns=["Timestamp", "Opening Price", "Closing Price", "High Price", "No of Shares"])
    
    # predict
    prediction = models[modelName].predict(latest_data)[0]
    current_price = float(latest_data["Low Price"].values[0])

    change = float(prediction) - current_price
    changeperc = (change / current_price) * 100

    color = RESET
    if changeperc >= 0.03:
        color = GREEN
    elif changeperc < -0.03:
        color = RED

    row = [stockName, current_price, round(prediction, 2), "{:.2f}".format(changeperc), modelName]
    print_row(row, color = color)
    if changeperc > 0.3:
        print(f"####  Buy {stockName} ####")


