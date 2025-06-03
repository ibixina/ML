import pandas as pd
import pickle
import os, requests, json, time, tqdm

# load models
models = {}

model_dir = "./models/day_2"
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



time_periods = {
    "d1": 24,
    "h6": 6,
    "h4": 4,
    "h1": 1,
    "h2": 2,
    "m30": 0.5,
}


def test_accuracy(time):
    stockNames = [
        "TSB", "TCI", "SYS", "LAG", "IOU", "GRN", "THS", "YAZ", "TCT", "CNC", "MSG", "TMI",
        "TCP", "IIL", "FHG", "SYM", "LSC", "PRN", "EWM", "TCM", "ELT", "HRG", "TGP", "MUN",
        "WSU", "IST", "BAG", "EVL", "MCS", "WLT", "TCC", "ASS", "CBD", "LOS", "PTS"
    ]

    accuracies = {}

    hours_per_step = time_periods[time]

    prediction_window = 3

    for stock in stockNames:
        df = get_data(stock, time)
        model_name = f"{stock}_{time}"
        if model_name not in models: continue
        model = models[f"{stock}_{time}"]

        for i in range(1, 10):
            df[f"lag_{i}"] = df["Low Price"].shift(i)

        df = df.dropna().reset_index(drop=True)

        X_all = df.drop(columns=["Timestamp", "Opening Price", "Closing Price", "High Price", "No of Shares"])
        low_prices = df["Low Price"].values
        preds = model.predict(X_all)

        total = 0
        complete = 0
        active_preds = []

        for i in range(len(df)):
            current_price = float(low_prices[i])


            new_active = []
            for pred in active_preds:
                if not pred["active"]:
                    continue
                pred["remaining_time"] -= 1
                price_met = current_price >= pred["target_price"]
                time_expired = pred["remaining_time"] <= 0

                if price_met:
                    complete += 1
                    pred["active"] = False
                elif time_expired:
                    pred["active"] = False
                else:
                    new_active.append(pred)


            # Check if prediction at i indicates >0.5% increase
            percent_change = (float(preds[i]) - current_price) / current_price
            if percent_change > 0.003:
                target_price = current_price * 1.003
                new_active.append({
                    "remaining_time": prediction_window,
                    "target_price": target_price,
                    "active": True
                })
                total += 1

            active_preds = new_active

        accuracies[stock] = complete / total if total > 0 else 0.0

    return accuracies

with open("all_prediction_accuracies.txt", "w") as file:
    for time in tqdm.tqdm(time_periods):
        accuracy = test_accuracy(time)
        file.write(f"=== Accuracy for {time} ===\n")
        file.write(str(accuracy) + "\n\n")

