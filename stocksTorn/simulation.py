from typing import List, Tuple
import pandas as pd


def simulate(data:List[int]) -> int:
    starting_balance = 10000000
    current_balance = starting_balance
    invested = [0, 0] # price and amount

    window_50 = data[150:200]
    window_200 = data[:200]

    sum_50 = sum(window_50)
    sum_200 = sum(window_200)

    prev_week_balance = current_balance

    for i in range(200, len(data)):
        old_50 = window_50.pop(0)
        old_200 = window_200.pop(0)

        window_50.append(data[i])
        window_200.append(data[i])

        sum_50 += data[i] - old_50
        sum_200 += data[i] - old_200

        ma_50 = sum_50 / 50
        ma_200 = sum_200 / 200

        # print(ma_50, ma_200)

        price = data[i]

        if ma_50 > ma_200 and invested[0] == 0:
            # buy the stock
            amt = current_balance // price
            trade_value = amt * price
            current_balance -= trade_value
            invested = [price, amt]
            # print(f"Buy Price: {price}, Amt: {amt}, Trade Value: {trade_value}, Current Balance: {current_balance}")
        elif price > 1.01*invested[0] and invested[0] > 0:
            # sell the stock
            if invested[1] > 0:
                invested_value = price * invested[1]
                invested_value_after_fee = 0.999 * invested_value
                current_balance += invested_value_after_fee

                # print(f"Buy Price: {invested[0]}, Sell Price: {price}, Amount: {invested[1]}, Trade Value: {invested_value}, Current Balance: {current_balance}")

                invested = [0, 0]

        # calculate weekly ROI
        if i % 28 == 0:
            total_value = invested[0] * invested[1] * 0.999 + current_balance
            weekly_roi = (total_value - prev_week_balance) / prev_week_balance * 100
            prev_week_balance = total_value
            print(f"Week {i//(24/6 * 7)} ROI: {weekly_roi}%")

    # sell any remaining stocks
    if invested[1] > 0:
        invested_value = invested[0] * invested[1]
        invested_value_after_fee = 0.999 * invested_value
        current_balance += invested_value_after_fee
        print("Selling remaining stocks...")
        print(f"Sell Price: {invested[0]}, Amount: {invested[1]}, Trade Value: {invested_value}, Current Balance: {current_balance}")
        invested = [0, 0]

    # final data
    net_profit = current_balance - starting_balance
    print(f"Net Profit: {net_profit}")
    print(f"ROI: {(net_profit / starting_balance) * 100}%")

    return net_profit



with open("./stocksData/lag_h6.csv", "r") as file:
    data = pd.read_csv(file)
    closing_price = data["Closing Price"].values.tolist()
    closing_price = closing_price[::-1]

    print(closing_price)
    simulate(closing_price)





