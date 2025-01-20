import plot
import prepare
import pandas as pd
import os
import backtrader as bt
import stock_hist_em as hist_em

high_turns = []
up_zs_open = []
up_zs_close = []
zs = []


class point:
    def __init__(self, i, x, y, state):
        self.i = i
        self.x = x
        self.y = y
        self.state = state

    def __sub__(self, other):
        return self.i - other.i


class Interval:
    def __init__(self, y1, y2):
        self.y1 = y1
        self.y2 = y2

    def __float__(self):
        return self.y2 - self.y1

    def intersection(self, y):
        if y >= self.y1 and y <= self.y2:
            return True
        return False


class ZS:
    def __init__(self, j, i, k, l):
        self.j = j
        self.i = i
        self.k = k
        self.l = l
        self.interval = Interval(y1=high_turns[k].y, y2=high_turns[i].y)

    def __float__(self):
        return self.interval.y2 - self.interval.y1


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


def valid(x):
    if x >= 4 and x <= 7:
        return True
    return False


def ZS_Observer(code, time: list, high: list, low: list):
    zs.clear()
    high_turns.clear()
    up_zs_open.clear()
    up_zs_close.clear()
    for i in range(1, len(high) - 1):
        if (high[i] - high[i - 1]) * (high[i + 1] - high[i]) < 0:
            high_turns.append(point(i, time[i], high[i], (high[i] - high[i - 1]) > 0))
    for i in range(1, len(high_turns) - 2):

        def low_turn(x, state):
            for i in range(max(x - 2, 1), min(x + 3, len(low) - 1)):
                if (
                    abs(low[i] / low[x] - 1) < 0.02
                    and (low[i] - low[i - 1]) * (low[i + 1] - low[i]) < 0
                ):
                    if state == 1 and low[i] - low[i - 1] > 0:
                        return True
                    if state == 0 and low[i] - low[i - 1] < 0:
                        return True
            return False

        def min_y(x):
            min_j = float("inf")
            for i in range(max(x - 2, 1), min(x + 3, len(low) - 1)):
                if abs(low[i] / low[x] - 1) < 0.02 and low[i] < min_j:
                    min_j = low[i]
            return min_j

        def similar(x, y):
            if abs((x - y) / x) < 0.5 and abs((x - y) / y) < 0.5:
                return True
            return False

        if not low_turn(high_turns[i].i, high_turns[i].state):
            continue
        if high_turns[i].state == 1:
            i_minus = []
            i_plus = []
            i_plus_plus = []

            for j in range(i - 1, max(0, i - 1 - 12), -2):
                if valid(high_turns[i] - high_turns[j]):
                    i_minus.append(j)
            for j in range(i + 1, min(len(high_turns), i + 1 + 12), 2):
                if valid(high_turns[j] - high_turns[i]):
                    i_plus.append(j)
            for j in range(i + 2, min(len(high_turns), i + 2 + 12), 2):
                if (
                    high_turns[j] - high_turns[i] >= 8
                    and high_turns[j] - high_turns[i] <= 14
                ):
                    i_plus_plus.append(j)
            flag = False
            contin = False
            for j in i_minus:
                min_j = min_y(high_turns[j].i)
                for ji in range(high_turns[j].i, high_turns[i].i + 1):
                    if low[ji] < min_j:
                        contin = True
                        break
                    if high[ji] > high_turns[i].y:
                        contin = True
                        break
                if contin:
                    contin = False
                    continue
                for k in i_plus:
                    min_k = min_y(high_turns[k].i)
                    for ik in range(high_turns[i].i, high_turns[k].i + 1):
                        if high[ik] > high_turns[i].y:
                            contin = True
                            break
                        if low[ik] < min_k:
                            contin = True
                            break
                    if contin:
                        contin = False
                        continue
                    for l in i_plus_plus:
                        for kl in range(high_turns[k].i, high_turns[l].i + 1):
                            if high[kl] > high_turns[l].y:
                                contin = True
                                break
                            if low[kl] < min_k:
                                contin = True
                                break
                        if contin:
                            contin = False
                            continue
                        if (
                            high_turns[k].y > high_turns[j].y
                            and high_turns[l].y > high_turns[i].y
                            and high_turns[i].y > high_turns[j].y
                            and high_turns[k].y < high_turns[i].y
                            and high_turns[l].y > high_turns[k].y
                            and high_turns[l].y - high_turns[k].y
                            and j < i
                            and i < k
                            and k < l
                            and similar(
                                high_turns[l].y - high_turns[k].y,
                                high_turns[i].y - high_turns[j].y,
                            )
                            and valid(high_turns[l] - high_turns[k])
                            and low_turn(high_turns[k].i, 0)
                            and low_turn(high_turns[l].i, 1)
                            and low_turn(high_turns[j].i, 0)
                        ):
                            print(
                                f"{code}, ZS:UP, from {high_turns[j].x}, to {high_turns[l].x}, points: {high_turns[i].x}, {high_turns[k].x}"
                            )
                            up_zs_open.append(high_turns[j].x)
                            up_zs_close.append(high_turns[l].x)
                            zs.append(ZS(j, i, k, l))
                            flag = True
                            break
                    if flag:
                        break
                if flag:
                    break


def main(num, date1, date2):
    # if not os.path.exists("stock_data.csv"):
    prepare.main(num, date1, date2)
    df = pd.read_csv("stock_data.csv")
    high = df["High"].tolist()
    low = df["Low"].tolist()
    time = df["Date"].tolist()
    ZS_Observer(num, time, high, low)
    if len(zs) > 0 and __name__ == "__main__":
        cerebro = bt.Cerebro()
        cerebro.addstrategy(bt.Strategy)
        cerebro.addobserver(ZSObserver)
        plot.main(cerebro)


if __name__ == "__main__":
    stock_list = [i for i in hist_em.code_id_map_em().keys()]
    # stock_list = ["603039"]
    for i in stock_list:
        try:
            main(i, "20250114", "20250122")
        except:
            pass
