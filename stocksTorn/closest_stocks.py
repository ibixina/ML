import os
import pandas as pd
import json


def normalize(data):
    max_value = max(data)
    min_value = min(data)
    return [(x - min_value) / (max_value - min_value) for x in data]

def find_distance(stock1, stock2):
    total_sum = 0;
    for a, b in zip(stock1, stock2):
        total_sum += abs(a - b)
    return total_sum

def print_matrix(matrix):
    for item in matrix:
        key = item[0]
        stock1, stock2 = key
        if stock1 == stock2:
            continue
        print(f"{stock1} and {stock2} are {item[1]} away")

def find_closeness_matrix(stocks):
    # 2d matrix
    closeness = {}
    for stock1name, stock1 in stocks:
        for stock2name, stock2 in stocks:
            key = sorted([stock1name, stock2name])
            key = tuple(key)
            print(key)
            if stock1 == stock2 or key in closeness:
                continue
            closeness[key] = find_distance(stock1, stock2)
    return closeness

def main():
    files_dir = "./stocksData/"
    files = os.listdir(files_dir)
    stocks_data = []
    for file in files:
        if file.endswith(".csv"):
            file_path = os.path.join(files_dir, file)
            stocks = pd.read_csv(file_path)
            stocks = stocks["Low Price"].tolist()
            normalize_stocks = normalize(stocks)
            stocks_data.append([file.replace(".csv", ""), normalize_stocks])

    closeness_matrix = find_closeness_matrix(stocks_data)
    # sort the matrix
    sorted_matrix = sorted(closeness_matrix.items(), key=lambda x: x[1])
    print_matrix(sorted_matrix)

    # print the matrix in pretty format

if __name__ == "__main__":
    main()

