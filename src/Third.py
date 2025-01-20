import ZS
import prepare
import pandas as pd
import backtrader as bt
import plot
import stock_hist_em as hist_em

third = []


class ThirdObserver(bt.Observer):
    lines = ("third",)

    plotinfo = dict(
        plot=True,
        plotname="Third Point",
        plotabove=True,
        plotlinelabels=True,
        plotmarkers=True,
        plotmarkerfacecolor="green",
        plotmarkercolor="green",
        plotmarkersize=12,
        plotmarker="^",
    )

    def __init__(self):
        self.third_marker = False

    def next(self):
        current_date = self.datas[0].datetime.datetime(0).strftime("%Y-%m-%d %H:%M:%S")
        if current_date in third:
            self.third_marker = True
        else:
            self.third_marker = False

        self.lines.third[0] = self.third_marker


def main(num, date1, date2):
    # if not os.path.exists("stock_data.csv"):
    third.clear()
    prepare.main(num, date1, date2)
    df = pd.read_csv("stock_data.csv")
    high = df["High"].tolist()
    low = df["Low"].tolist()
    time = df["Date"].tolist()

    def strength(x):
        strength = 0
        for i in range(x, min(len(high), x + 2)):
            strength = max(high[i] - low[i], strength)
        return strength

    ZS.ZS_Observer(num, time, high, low)
    for i in ZS.zs:
        for j in range(i.l + 1, len(ZS.high_turns), 2):
            if ZS.valid(ZS.high_turns[j].i - ZS.high_turns[i.l].i):
                if (
                    i.interval.y2 < ZS.high_turns[j].y
                    and ZS.high_turns[j].y < ZS.high_turns[i.l].y
                ):
                    if float(i) < strength(ZS.high_turns[j].i):
                        third.append(time[ZS.high_turns[j].i])
                        print(f"{num}, Third point, {time[ZS.high_turns[j].i]}")
                        break
    if len(third) > 0 and __name__ == "__main__":
        cerebro = bt.Cerebro()
        cerebro.addstrategy(bt.Strategy)
        cerebro.addobserver(ZS.ZSObserver)
        cerebro.addobserver(ThirdObserver)
        plot.main(cerebro)


if __name__ == "__main__":
    stock_list = [i for i in hist_em.code_id_map_em().keys()]
    # stock_list = ["605117"]
    for i in stock_list:
        try:
            main(i, "20250114", "20250122")
        except:
            pass
