import pandas as pd
import pickle
import os, requests, json, time, tqdm

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

time_periods = {
    "d1": 24,
    "h6": 6,
    "h4": 4,
    "h1": 1,
    "h2": 2,
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

for modelName in tqdm.tqdm(models, desc="Prediction in progress: "):
    stockName = modelName.split("_")[0]
    stock_period = modelName.split("_")[1]

    # based on the accuracy test, only use d1
    if stock_period != "d1": continue

    # print(f"Predicting for {stockName} using model {modelName}")
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
    # print(predictions)
    # get the last prediction
    prediction = predictions[-1]

    if stockName not in stock_predictions:
        stock_predictions[stockName] = []
    

    current_price = float(X["Low Price"].values[0])

    change = float(prediction) - current_price
    changeperc = (change / current_price) * 100

    stock_predictions[stockName] += [changeperc]

    # print(f"Current: {current_price}, Predicted: {prediction}, Change: {changeperc:.2f}%")
    # if changeperc > 0.3:
    #     print(f"####  Buy {stockName} {stock_period} ####")

    time.sleep(0.5)  # To avoid hitting the API too fast

print(stock_predictions)

headers = ["Stock", "Change %"]


print_row(headers, type=1)

stock_predictions_final = []

# get the average from different prediction
for stockName in stock_predictions:
    avg = sum(stock_predictions[stockName]) / len(stock_predictions[stockName])
    if avg >= 0.3:
        color = GREEN  
    elif avg < -0.3:
        color = RED
    else:
        color = RESET

    stock_predictions_final += [(stockName, round(avg, 2), color)]

sorted_stock_predictions = reversed(sorted(stock_predictions_final, key = lambda x: x[1]))

for stockName, avg, color in sorted_stock_predictions:
    print_row((stockName, avg), color = color)

