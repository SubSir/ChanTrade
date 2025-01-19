import plot
import prepare
import pandas as pd
import os
import backtrader as bt

up_zs_open = []
up_zs_close = []


class ZSObserver(bt.Observer):
    lines = ("up_zs",)

    plotinfo = dict(
        plot=True,
        plotname="Up ZS",
        plotabove=True,
        plotlinelabels=True,
        plotmarkers=True,
        plotmarkerfacecolor="green",
        plotmarkercolor="green",
        plotmarkersize=12,
        plotmarker="^",
    )

    def __init__(self):
        self.up_zs_marker = False

    def next(self):
        current_date = self.datas[0].datetime.datetime(0).strftime("%Y-%m-%d %H:%M:%S")
        if current_date in up_zs_open:
            self.up_zs_marker = True
        elif current_date in up_zs_close:
            self.up_zs_marker = False

        self.lines.up_zs[0] = self.up_zs_marker


class point:
    def __init__(self, i, x, y, state):
        self.i = i
        self.x = x
        self.y = y
        self.state = state

    def __sub__(self, other):
        return self.i - other.i


def ZS_Observer(time: list, high: list, low: list):
    high_turns = []
    up_zs_open.clear()
    up_zs_close.clear()
    for i in range(1, len(high) - 1):
        if (high[i] - high[i - 1]) * (high[i + 1] - high[i]) < 0:
            high_turns.append(point(i, time[i], high[i], (high[i] - high[i - 1]) > 0))
    for i in range(1, len(high_turns) - 2):

        def low_turn(x, state):
            for i in range(max(x - 2, 1), min(x + 3, len(high_turns) - 1)):
                if (low[i] - low[i - 1]) * (low[i + 1] - low[i]) < 0:
                    if state == 1 and low[i] - low[i - 1] > 0:
                        return True
                    if state == 0 and low[i] - low[i - 1] < 0:
                        return True
            return False

        def valid(x):
            if x >= 4 and x <= 11:
                return True
            return False

        if not low_turn(i, high_turns[i].state):
            continue
        if high_turns[i].state == 1:
            i_minus = []
            i_plus = []
            i_plus_plus = []

            for j in range(i - 1, 0, -2):
                if valid(high_turns[i] - high_turns[j]):
                    i_minus.append(j)
            for j in range(i + 1, len(high_turns), 2):
                if valid(high_turns[j] - high_turns[i]):
                    i_plus.append(j)
            for j in range(i + 2, len(high_turns), 2):
                if (
                    high_turns[j] - high_turns[i] >= 8
                    and high_turns[j] - high_turns[i] <= 22
                ):
                    i_plus_plus.append(j)
            flag = False
            for j in i_minus:
                for k in i_plus:
                    for l in i_plus_plus:
                        if (
                            high_turns[k].y > high_turns[j].y
                            and high_turns[l].y > high_turns[i].y
                            and high_turns[i].y > high_turns[j].y
                            and high_turns[k].y < high_turns[i].y
                            and high_turns[l].y > high_turns[k].y
                            and j < i
                            and i < k
                            and k < l
                            and valid(high_turns[l] - high_turns[k])
                            and low_turn(k, 0)
                            and low_turn(l, 1)
                            and low_turn(j, 0)
                        ):
                            print(
                                f"ZS:UP, from {high_turns[j].x}, to {high_turns[l].x}, points: {high_turns[i].x}, {high_turns[k].x}"
                            )
                            up_zs_open.append(high_turns[j].x)
                            up_zs_close.append(high_turns[l].x)
                            flag = True
                            break
                    if flag:
                        break
                if flag:
                    break


def main(num, date1, date2):
    if not os.path.exists("stock_data.csv"):
        prepare.main(num, date1, date2)
    df = pd.read_csv("stock_data.csv")
    high = df["High"].tolist()
    low = df["Low"].tolist()
    time = df["Date"].tolist()
    ZS_Observer(time, high, low)
    cerebro = bt.Cerebro()

    cerebro.addstrategy(bt.Strategy)

    cerebro.addobserver(ZSObserver)
    plot.main(cerebro)


if __name__ == "__main__":
    main("301210", "20250117", "20250118")
