

# 顶底信号策略
# 起始价=期货合约当前交易日开盘价，产生顶信号或底信号以后重新定义起始价，起始价为产生信号时的价格。当前交易日结束后，起始价初始化，重新以期货合约当前交易日开盘价计算。

# 满足以下3个条件以当前5分钟收盘价作为顶信号：
# 条件1：当前交易日5分钟收盘价≥起始价+0.33*14日ATR
# 条件2：当前5分钟K收阴
# 条件3：当前5分钟K与上一根5分钟比较；上一根5分钟K为阴线，当前5分钟K收盘价≤上一根5分钟K收盘价；上一根5分钟K为阳线，当前5分钟K收盘价≤上一根5分钟K开盘价。
# 满足以下3个条件以当前5分钟收盘价作为产生底信号：
# 条件1：当前交易日5分钟收盘价<=起始价-0.33*14日ATR
# 条件2：当前5分钟K收阳
# 条件3：当前5分钟K与上一根5分钟比较；上一根5分钟K为阴线，当前5分钟K收盘价≥上一根5分钟K收盘价；上一根5分钟K为阳线，当前5分钟K收盘价≥上一根5分钟K开盘价

# 策略参数字典
g_params['p1'] = 20    # 参数示例


# ===================== 顶底信号策略 + 止盈止损 + 强制平仓 =====================
import numpy as np
from datetime import datetime

g_params['p1'] = 20

# 初始化策略
def initialize(context):

    
    global code
    code = context.contractNo()
    LogInfo("合约 =", code)
    ConfigParameters(context)
    SetAFunUseForHis()
    SetMargin(0, context.margin_rate, code)
    SetInitCapital(context.init_capital)
    SetBarInterval(code, 'M', context.k_period, '20250301')
    SetBarInterval(code, 'D', 1, '20250301')
    SetBarInterval(code, 'M', 5, '20250301')  # 注册1分钟K线，从同一天开始

    InitContext(context)

def ConfigParameters(context):
    context.trade_amount = 1 # 交易手数
    context.k_period = 1 # K线周期
    context.atr_period = 14 # ATR周期
    context.multiy_atr = 0.33 # 顶底ATR倍数
    context.loss_multiy_atr = 0.33 # 止损ATR倍数
    context.margin_rate = MarginRatio(code)
    context.init_capital = 100 * 10000 # 初始资金
    context.strict_signal_check = False  # ✅ 控制是否启用“更严格的第二次信号条件”


def InitContext(context):
    context.current_trade_date = None
    context.start_price = 0
    context.position = None  # 'long' or 'short'
    context.position_price = 0.0
    context.consec_signals = 0 # 连续同方向的信号次数
    context.ended_trade_days = set()
    context.open_count = 0  # 每日已开仓次数
    context.prev_close_price = None  # 昨日收盘价
    context.signal_count_today = 0  # ✅ 每日信号计数


def get_latest_bars(contract, ktype, kval, count):
    if CurrentBar(contract, ktype, kval) < count - 1:
        return None
    bars = HisBarsInfo(contract, ktype, kval, count)
    if bars is None or len(bars) < count:
        return None
    return bars

def calc_daily_atr(contract, period, current_trade_date):
    """
    计算指定合约的日线ATR（Average True Range）
    :param contract: 合约代码
    :param period: ATR周期
    :param current_trade_date: 当前交易日（字符串或日期）
    :return: ATR值（float）或 None（数据不足或异常）
    """
    bars = HisBarsInfo(contract, 'D', 1, period + 20)
    if bars is None or len(bars) < period + 1:
        # LogInfo(f"[ATR计算失败] 获取日K线不足 {period + 1} 根，当前仅有 {len(bars) if bars is not None else 0}")
        return None

    # 统一 TradeDate 格式为字符串，兼容不同格式
    def extract_date_str(b):
        dt = b['TradeDate']
        return dt.strftime('%Y%m%d') if hasattr(dt, 'strftime') else str(dt)

    curr_date_str = current_trade_date.strftime('%Y%m%d') if hasattr(current_trade_date, 'strftime') else str(current_trade_date)

    # 过滤掉当前交易日及之后的，确保都是“历史数据”
    bars_filtered = [b for b in bars if extract_date_str(b) <= curr_date_str]
    if len(bars_filtered) < period + 1:
        # LogInfo(f"[ATR计算失败] 当前交易日={curr_date_str}，过滤后历史数据仅 {len(bars_filtered)} 条")
        return None

    # 保留最近的 period + 1 根K线用于计算 TR
    bu = bars_filtered[-(period + 1):]

    # 提取高低收
    high = np.array([b['HighPrice'] for b in bu])
    low = np.array([b['LowPrice'] for b in bu])
    close = np.array([b['LastPrice'] for b in bu])

    # 前一日收盘价
    pre_close = close[:-1]

    # 计算 True Range（TR）
    tr = np.maximum.reduce([
        high[1:] - low[1:],
        np.abs(high[1:] - pre_close),
        np.abs(low[1:] - pre_close)
    ])

    atr = np.mean(tr)
    # LogInfo(f"[ATR计算成功] 合约={contract}, 当前日={curr_date_str}, ATR({period})={atr:.4f}")
    return atr

def handle_data(context):
    c = code
    # 当前1分钟K线
    bars_1min = get_latest_bars(c, 'M', 1, 1)
    if not bars_1min:
        return
    bar_1min = bars_1min[0]

    # 当前时间和交易日
    bar_time = datetime.strptime(str(bar_1min['DateTimeStamp'])[:12], '%Y%m%d%H%M')
    trade_date = bar_1min['TradeDate']

    # 每日初始化（在任何一分钟触发时进行）
    if context.current_trade_date != trade_date:
        init_trade_day(context, trade_date, bar_1min)

    # 每日14:50强制平仓
    if bar_time.strftime('%H%M') == '1450':
        force_close_position(context, bar_1min['LastPrice'], trade_date,bar_time)
        return

    # 止损逻辑（每分钟执行一次）
    check_stop_loss(context, bar_1min,bar_time)

    # 仅在每5分钟整点，才判断是否产生顶底信号
    if bar_time.minute % 5 == 0:
        bars_5min = get_latest_bars(c, 'M', 5, 2)
        if bars_5min is not None and len(bars_5min) >= 2:
            prev_5m, curr_5m = bars_5min[0], bars_5min[1]
            handle_top_bottom_signal(context, prev_5m, curr_5m, bar_time)

# 每日初始化
def init_trade_day(context, trade_date, bar):
    context.current_trade_date = trade_date
    context.start_price = bar['OpeningPrice']
    context.position = None
    context.position_price = 0.0
    context.consec_signals = 0 # 连续同方向的信号次数
    context.last_signal_type = None # 最近的一个信号类型
    context.open_count = 0 
    context.ended_trade_days = set()
    context.signal_count_today = 0  # ✅ 每日信号计数


    d_bars = get_latest_bars(code, 'D', 1, 2)
    if d_bars is not None and len(d_bars) >= 2:
        context.prev_close_price = d_bars[0]['LastPrice']

# 止损逻辑
def check_stop_loss(context, bar,bar_time):
    atr = calc_daily_atr(code, context.atr_period, context.current_trade_date)
    if atr is None or context.position is None:
        return
    price = bar['LastPrice']
    stop_gap = context.loss_multiy_atr * atr
    if context.position == 'long' and price <= context.position_price - stop_gap:
        Sell(context.trade_amount, price, code)
        context.position = None
        context.position_price = 0.0
        LogInfo(f"时间:{bar_time}，止损平多 @ {price}")
    elif context.position == 'short' and price >= context.position_price + stop_gap:
        BuyToCover(context.trade_amount, price, code)
        context.position = None
        context.position_price = 0.0
        LogInfo(f"时间:{bar_time}， 止损平空 @ {price}")

# 顶底信号逻辑处理
def handle_top_bottom_signal(context, prev, bar, bar_time):
    trade_date = bar['TradeDate']
    if trade_date in context.ended_trade_days or bar_time.strftime('%H%M') >= '1450':
        return

    atr = calc_daily_atr(code, context.atr_period, trade_date)
    if atr is None:
        return

    close_, open_ = bar['LastPrice'], bar['OpeningPrice']
    prev_close, prev_open = prev['LastPrice'], prev['OpeningPrice']

    # 当前K线的高低价
    high_ = bar['HighPrice']
    low_ = bar['LowPrice']

    # 顶/底信号判断
    top_cond = close_ >= context.start_price + context.multiy_atr * atr and close_ < open_ and (
        (prev_close < prev_open and close_ <= prev_close) or
        (prev_close >= prev_open and close_ <= prev_open))

    bot_cond = close_ <= context.start_price - context.multiy_atr * atr and close_ >= open_ and (
        (prev_close < prev_open and close_ >= prev_open) or
        (prev_close >= prev_open and close_ >= prev_close))

    # ✅ 加上 stricter 第二信号条件（开启时才检查，且至少是第2个信号）
    if context.strict_signal_check and context.signal_count_today >= 1:
        if top_cond:
            top_cond = top_cond and high_ >= context.start_price + 0.5 * atr
        if bot_cond:
            bot_cond = bot_cond and low_ <= context.start_price - 0.5 * atr

    if not (top_cond or bot_cond):
        return

    signal = 'top' if top_cond else 'bottom'

    # 连续同向信号判断
    if context.last_signal_type == signal:
        context.consec_signals += 1
    else:
        context.consec_signals = 1
        context.last_signal_type = signal

    if context.consec_signals >= 3:
        LogInfo(f"⚠️ 连续3次{signal}信号，跳过交易")
        context.ended_trade_days.add(trade_date)
        return

    only_close = check_risk_controls(context, signal, close_, bar_time.strftime('%H%M'))

    # 平仓逻辑
    if context.position:
        if signal == 'top' and context.position == 'long':
            LogInfo(f"时间:{bar_time}，平多仓, signal:{signal}, position:{context.position}, close:{close_}")
            Sell(context.trade_amount, close_, code)
            context.position = None
        elif signal == 'bottom' and context.position == 'short':
            LogInfo(f"时间:{bar_time}，平空仓, signal:{signal}, position:{context.position}, close:{close_}")
            BuyToCover(context.trade_amount, close_, code)
            context.position = None

    # 开仓逻辑
    if not context.position and not only_close:
        if signal == 'top':
            LogInfo(f"时间:{bar_time}，建空仓, signal:{signal},position:{context.position}")
            SellShort(context.trade_amount, close_, code)
            context.position = 'short'
        else:
            LogInfo(f"时间:{bar_time}，建多仓, signal:{signal},position:{context.position}")
            Buy(context.trade_amount, close_, code)
            context.position = 'long'
        context.position_price = close_
        context.open_count += 1
        # ✅ 顶/底信号确认成立后，执行以下逻辑前增加信号计数
        context.signal_count_today += 1

    # 更新起始价
    context.start_price = close_
    PlotText(close_, "顶▶空" if signal == 'top' else "底▶多", RGB_Green() if signal == 'top' else RGB_Red(), main=True)
    LogInfo(f"时间:{bar_time}，产生了{signal}信号，持仓:{context.position}@,价格为:{close_}")

# 风险控制
def check_risk_controls(context, signal, price, time_str):
    only_close = False
    if time_str >= '1430':
        if context.position:
            LogInfo(f"[风控1] {time_str} >= 14:30，有持仓，仅平不反手")
            only_close = True
        else:
            LogInfo(f"[风控2] {time_str} >= 14:30，无持仓跳过")
            return True  # 直接跳过

    if context.prev_close_price:
        price_diff_ratio = abs(price - context.prev_close_price) / context.prev_close_price
        if price_diff_ratio >= 0.04:
            LogInfo(f"[风控3] 涨跌幅超4%，禁止开仓")
            only_close = True

    if context.open_count >= 2:
        LogInfo(f"[风控4] 每日开仓次数超限，仅允许平仓")
        only_close = True

    return only_close

# 强平机制
def force_close_position(context, price, trade_date,bar_time):
    if context.position == 'long':
        Sell(context.trade_amount, price, code)
    elif context.position == 'short':
        BuyToCover(context.trade_amount, price, code)
    context.position = None
    context.ended_trade_days.add(trade_date)
    PlotText(price, "日内平仓", RGB_Blue(), main=True)
    LogInfo(f"时间 @ {bar_time} 强制平仓 @ {price}")


def hisover_callback(context):
    c = code
        
    # 检查是否有持仓
    if context.position == 'long':
        # 平多仓
        Sell(context.trade_amount, Close()[-1], c)
        LogInfo(f"回测结束平多仓，数量: {context.trade_amount}, 价格: {Close()[-1]}")
        
    elif context.position == 'short':
        # 平空仓
        BuyToCover(context.trade_amount, Close()[-1], c)
        LogInfo(f"回测结束平空仓，数量: {context.trade_amount}, 价格: {Close()[-1]}")
        
    else:


        LogInfo("回测结束时无持仓，无需平仓")
        
    # 重置持仓状态
    context.position = None
    context.position_price = 0.0
    LogInfo("回测结束")
    pass

def exit_callback(context):
    LogInfo("策略退出")

