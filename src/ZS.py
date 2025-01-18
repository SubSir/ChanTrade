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
        current_date = self.datas[0].datetime.date(0).strftime("%Y-%m-%d")
        if current_date in up_zs_open:
            self.up_zs_marker = True
        elif current_date in up_zs_close:
            self.up_zs_marker = False
        else:
            self.up_zs_marker = False

        self.lines.up_zs[0] = self.up_zs_marker


class point:
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.state = state


def ZS_Observer(time: list, high: list, low: list):
    high_turns = []
    for i in range(1, len(high) - 1):
        if (high[i] - high[i - 1]) * (high[i + 1] - high[i]) < 0:
            high_turns.append(point(time[i], high[i], (high[i] - high[i - 1]) > 0))
    for i in range(1, len(high_turns) - 2):
        if high_turns[i].state == 1:
            if (
                high_turns[i + 1].y > high_turns[i - 1].y
                and high_turns[i + 2].y > high_turns[i].y
            ):
                print(f"ZS:UP, from {high_turns[i-1].x}, to {high_turns[i+2].x}")
                up_zs_open.append(high_turns[i - 1].x)
                up_zs_close.append(high_turns[i + 2].x)


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
    plot.main(date1, date2, "301210", cerebro)


if __name__ == "__main__":
    main("301210", "20230830", "20250830")
