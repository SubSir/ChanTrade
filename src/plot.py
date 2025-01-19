import backtrader as bt
import pandas as pd
from datetime import datetime, timedelta
from backtrader.feeds import GenericCSVData
import numpy as np
import matplotlib

tq07_corUp, tq07_corDown = ["#E1440F", "#B0F76D"]

tq_ksty07 = dict(
    volup=tq07_corUp, voldown=tq07_corDown, barup=tq07_corUp, bardown=tq07_corDown
)


# 定义自定义数据类
class MyCSVData(GenericCSVData):
    # 定义列名映射到Backtrader字段
    lines = ("datetime", "open", "close", "high", "low", "volume")
    params = (
        ("timeframe", bt.TimeFrame.Minutes),
        ("compression", 1),
        ("dtformat", "%Y-%m-%d %H:%M:%S"),  # 日期格式
        ("tmformat", "%H:%M:%S"),  # 时间格式
        ("datetime", 0),  # 日期列索引
        ("open", 1),  # 开盘价列索引
        ("close", 2),  # 收盘价列索引
        ("high", 3),  # 最高价列索引
        ("low", 4),  # 最低价列索引
        ("volume", 5),  # 成交量列索引
        ("openinterest", -1),  # 开仓兴趣列索引，如果不存在可以设置为-1
    )


class MyStrategy(bt.Strategy):
    def __init__(self):
        pass

    def next(self):
        pass


def main(cerebro):
    # cerebro = bt.Cerebro()

    # 加载数据
    data = MyCSVData(
        dataname="stock_data.csv",
    )

    # 添加数据到回测引擎
    cerebro.adddata(data)

    # 添加策略
    # cerebro.addstrategy(MyStrategy)

    # 设置初始资金
    start_cash = 100000.0
    cerebro.broker.setcash(start_cash)

    # 运行回测
    cerebro.run()

    # # 获取回测结束后的总资金
    # end_cash = cerebro.broker.getvalue()

    # # 计算总收益率
    # total_return_percentage = ((end_cash - start_cash) / start_cash) * 100

    # # 假设回测周期是从date1到date2，计算总天数
    # total_days = (to_date - from_date).days
    # # 假设一年有365天，计算平均年化收益率
    # annualized_return_percentage = (
    #     (1 + total_return_percentage / 100) ** (365 / total_days)
    # ) - 1
    # annualized_return_percentage *= 100  # 转换为百分比形式

    # # 打印最终的资产价值、总收益率和平均年化收益率
    # print(f"Final Portfolio Value: {end_cash:.2f}")
    # print(f"Total Return Percentage: {total_return_percentage:.2f}%")
    # print(f"Average Annualized Return Percentage: {annualized_return_percentage:.2f}%")

    # matplotlib.use("agg")
    # if abs(annualized_return_percentage) > 0.1:
    cerebro.plot(style="candle", **tq_ksty07)
    #     fig = figs[0][0]
    #     fig.savefig("photo/" + code + ".png")
    # return annualized_return_percentage


if __name__ == "__main__":
    cerebro = bt.Cerebro()

    cerebro.addstrategy(MyStrategy)

    main(cerebro)
