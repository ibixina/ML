import requests, json, math, csv, time

stockData = []

def getStockData(stockTicker, to=""):
    global stockData

    url = f"https://tornsy.com/api/{stockTicker}?interval=h6&to={to}"
    print(f"Making request to {url}")

    response = requests.get(url)

    print(f"Response: {response.status_code}")
    jsonResponse = json.loads(response.text)

    earliestTimeStamp = math.inf

    if "data" in jsonResponse and len(jsonResponse["data"]) > 0:
        for data in jsonResponse["data"]:
            timestamp = data[0]
            if timestamp < earliestTimeStamp:
                earliestTimeStamp = timestamp
            stockData += [data]

        time.sleep(2)
        getStockData(stockTicker, earliestTimeStamp)

def saveAsCSV(stockData, filename):
    print(stockData[:10])
    headers = ["Timestamp", "Opening Price", "High Price", "Low Price", "Closing Price", "No of Shares"]
    with open(filename, "w") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for data in stockData:
            writer.writerow(data)


def main():
    stockTickers = ["lag",
                    "tcc",
                    "evl",
                    "sym",
                    "prn",
                    "fhg",
                    "tmi",
                    "wlt",
                    "cnc",
                    "tgp",
                    "yaz",
                    "tcp",
                    "elt",
                    "grn",
                    "tci",
                    "los",
                    "msg",
                    "ass",
                    "wsu",
                    "ths",
                    "ist",
                    "iou",
                    "lsc",
                    "iil",
                    "hrg",
                    "mun",
                    "bag",
                    "cbd",
                    "pts",
                    "tct",
                    "tcm",
                    "tsb",
                    "sys",
                    "mcs",
                    "ewm",
                    ]

    for stockTicker in stockTickers:
        print(f"Getting data for {stockTicker}")
        getStockData(stockTicker)
        saveAsCSV(stockData, f"{stockTicker}_h6.csv")

    
if __name__ == "__main__":
    main()
