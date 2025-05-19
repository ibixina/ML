#!/usr/bin/env python
from dotenv import load_dotenv
import pandas as pd
import os, requests, time, json, tqdm, pickle

load_dotenv()

MAX_REQUESTS_PER_MINUTE = 80
SLEEP_TIME = 60 / MAX_REQUESTS_PER_MINUTE

API_KEY = os.getenv("TORN_PUBLIC_API")

def getTornData(id: str) -> dict:
    url = f"https://api.torn.com/user/{id}?selections=basic,personalstats&key={API_KEY}"
    response = requests.get(url)
    data = json.loads(response.text)
    return_data = {}
    return_data["level"] = data.get("level", 1)
    personal_stats = data.get("personalstats", {})

    for key, value in personal_stats.items():
        return_data[key] = value
    
    return return_data

def saveData():
    csv_data = pd.read_csv("./spyData.csv")

    for idx, row in tqdm.tqdm(csv_data.iterrows(), total=csv_data.shape[0], desc="Getting data"):
        user_id = row["Id"]
        stats = getTornData(user_id)
        if stats is None:
            continue
        for key, value in stats.items():
            if key not in csv_data.columns:
                csv_data[key] = ""
            csv_data.at[idx, key] = value
        time.sleep(SLEEP_TIME)

    csv_data.to_csv("./spyData.csv")


def test():
    model = pickle.load(open("./best_model_spy_prediction_ElasticNet.pkl", "rb"))
    data = getTornData("2669774")
    input_data = pd.DataFrame([ data ])
    prediction = model.predict(input_data)
    print(prediction)

test()




