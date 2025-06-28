

# 顶底信号策略
# 起始价=期货合约当前交易日开盘价，产生顶信号或底信号以后重新定义起始价，起始价为产生信号时的价格。当前交易日结束后，起始价初始化，重新以期货合约当前交易日开盘价计算。

# 满足以下3个条件以当前5分钟收盘价作为顶信号：
# 条件1：当前交易日5分钟收盘价≥起始价+0.33*14日ATR
# 条件2：当前5分钟K收阴
# 条件3：当前5分钟K与上一根5分钟比较；上一根5分钟K为阴线，当前5分钟K收盘价≤上一根5分钟K收盘价；上一根5分钟K为阳线，当前5分钟K收盘价≤上一根5分钟K开盘价。
# 满足以下3个条件以当前5分钟收盘价作为产生底信号：
# 条件1：当前交易日5分钟收盘价≥起始价-0.33*14日ATR
# 条件2：当前5分钟K收阳
# 条件3：当前5分钟K与上一根5分钟比较；上一根5分钟K为阴线，当前5分钟K收盘价≥上一根5分钟K收盘价；上一根5分钟K为阳线，当前5分钟K收盘价≥上一根5分钟K开盘价

# 策略参数字典
g_params['p1'] = 20    # 参数示例


import talib
import pandas as pd
import numpy as np
from datetime import datetime



code = ""
# code = "DCE|F|JM|2501"

# 策略参数字典（平台使用）
g_params['p1'] = 20    # 参数示例


# 初始化函数：运行一次
def initialize(context): 
    global code


    code = context.contractNo()
    LogInfo("合约代码 =", code)

    # 设置参数
    ConfigParameters(context)
    SetAFunUseForHis()

    # 设置保证金比例与初始资金
    SetMargin(0, context.margin_rate, code)
    SetInitCapital(context.init_capital)

    # 注册5分钟K线，从 2025-01-15 开始
    SetBarInterval(code, 'M', context.k_period, '20250514')
    SetBarInterval(code, 'D', 1, '20250514')

    # 初始化标志变量
    InitContext(context)


# 参数配置
def ConfigParameters(context):
    context.margin_rate = MarginRatio(code)
    context.init_capital = 100 * 10000
    context.trade_amount = 10
    context.k_period = 5
    context.atr_period = 14
    context.multiy_atr = 0.33
    context.start_price_new = 0  # 起始价初始化
    context.ended_trade_days = set()


def InitContext(context):
    context.current_trade_date = None
    context.is_top_confirmed = False
    context.is_bottom_confirmed = False
    context.atr_cache = {}


# 每根5分钟K线触发时运行
def handle_data(context):
    c = context.contractNo()

    bars = get_latest_bars(c, 'M', context.k_period, 2)
    if bars is None or len(bars) < 2:
        return

    prev = bars[0]  # 上一根K线
    bar = bars[1]   # 当前K线

    # 时间与交易日
    dt = str(bar['DateTimeStamp'])[:12]
    bar_time = datetime.strptime(dt, '%Y%m%d%H%M')
    trade_date = bar['TradeDate']


     # 若当前交易日已结束信号处理，则直接返回
    if trade_date in context.ended_trade_days:
        return

    # 新交易日初始化起始价
    if context.current_trade_date != trade_date:
        context.current_trade_date = trade_date
        context.start_price = bar['OpeningPrice']
        LogInfo("新交易日初始化起始价:",bar['OpeningPrice'],",trade_date:",trade_date)

    
    # 每次都重新计算最新的atr
    atr = calc_daily_atr(c, context.atr_period, trade_date)
    if atr is None:
        return

    # 如果当前K线为 14:55，则标记今天已结束信号判断
    if bar_time.strftime('%H%M') == '1455':
        context.ended_trade_days.add(trade_date)
        # LogInfo(f"[{dt}] 到14:55，结束今日信号判断")
        PlotText(Close()[-1], "结束", RGB_Green(), main=True)
        return

    close_ = bar['LastPrice']
    open_ = bar['OpeningPrice']
    prev_close = prev['LastPrice']
    prev_open = prev['OpeningPrice']



    # 顶信号
    if (close_ >= context.start_price + context.multiy_atr * atr and
        close_ < open_ and
        ((prev_close < prev_open and close_ <= prev_close) or
         (prev_close > prev_open and close_ <= prev_open))):
        LogInfo(f"[{dt}] 顶信号 | 收盘:{close_:.2f} | 起始:{context.start_price:.2f} | ATR:{atr:.2f} | 开盘:{open_:.2f}")
        PlotText(Close()[-1], "顶", RGB_Green(), main=True)
        context.start_price = close_
        return

    # 底信号
    if (close_ <= context.start_price - context.multiy_atr * atr and
        close_ > open_ and
        ((prev_close < prev_open and close_ >= prev_close) or
         (prev_close > prev_open and close_ >= prev_open))):
        LogInfo(f"[{dt}] 底信号 | 收盘:{close_:.2f} | 起始:{context.start_price:.2f} | ATR:{atr:.2f} | 开盘:{open_:.2f}")
        PlotText(Close()[-1], "底", RGB_Red(), main=True)
        context.start_price = close_



def calc_daily_atr(contract, period, current_trade_date):
    # 多取一些历史日K，确保足够
    bars = HisBarsInfo(contract, 'D', 1, period + 10)
    if bars is None or len(bars) < period + 1:
        LogInfo("⚠️ 无法获取足够的历史日K线数据用于ATR计算")
        return None

    # 筛选出早于当前交易日的日K
    bars_filtered = [b for b in bars if b['TradeDate'] <= current_trade_date]

    # 取最近 period+1 条
    if len(bars_filtered) < period + 1:
        LogInfo(f"⚠️ 有效历史日K线数量不足，当前只有 {len(bars_filtered)} 条")
        return None

    bars_used = bars_filtered[-(period + 1):]

    # 提取数据计算 ATR
    high = np.array([b['HighPrice'] for b in bars_used])
    low = np.array([b['LowPrice'] for b in bars_used])
    close = np.array([b['LastPrice'] for b in bars_used])

    pre_close = close[:-1]
    tr = np.maximum.reduce([
        high[1:] - low[1:],
        np.abs(high[1:] - pre_close),
        np.abs(low[1:] - pre_close)
    ])

    atr = np.mean(tr)
    return atr


# 获取最近count根K线前，判断是否满足当前进度
def get_latest_bars(contract, ktype, kval, count):
    if CurrentBar(contract, ktype, kval) < count - 1:
        return None
    return HisBarsInfo(contract, ktype, kval, count)

# 回测结束
def hisover_callback(context):
    LogInfo("回测结束。")


# 策略退出前
def exit_callback(context):
    LogInfo("策略退出。")
