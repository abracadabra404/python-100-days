import pandas as pd

# 贷款参数
loan_amount = 1000000
years = 5
months = years * 12
annual_rate = 0.021
monthly_rate = annual_rate / 12

# 公积金参数
initial_balance = 300000
monthly_contrib = 4800

# 每月固定本金
monthly_principal = loan_amount / months

# 收入 & 支出参数
monthly_income = 38000  # 税后收入
current_rent = 3600  # 当前房租
monthly_expenses = 15000  # 当前总支出(含房租)

# 存储结果
records = []
remaining_principal = loan_amount
pf_balance = initial_balance

for m in range(1, months + 1):
    # 当月利息
    interest = remaining_principal * monthly_rate
    repayment = monthly_principal + interest

    # 公积金入账
    pf_balance += monthly_contrib

    # 公积金扣款
    if pf_balance >= repayment:
        pf_pay = repayment
        bank_pay = 0
    else:
        pf_pay = pf_balance
        bank_pay = repayment - pf_balance
    pf_balance -= pf_pay

    # 实际银行卡月供
    actual_bank_pay = bank_pay

    # 计算买房后的支出情况
    # 注意：买房后房租抵扣掉 (即不用再支出3600租金)
    new_expenses = monthly_expenses - current_rent + actual_bank_pay
    savings_after_buy = monthly_income - new_expenses
    extra_cost = new_expenses - monthly_expenses  # 比当前多出的支出

    # 保存记录
    records.append({
        "月份": m,
        "应还本金": round(monthly_principal, 2),
        "应还利息": round(interest, 2),
        "应还总额": round(repayment, 2),
        "公积金支付": round(pf_pay, 2),
        "银行卡支付": round(bank_pay, 2),
        "月末公积金余额": round(pf_balance, 2),
        "买房后支出": round(new_expenses, 2),
        "比当前多出支出": round(extra_cost, 2),
        "买房后每月可存": round(savings_after_buy, 2)
    })

    # 更新剩余本金
    remaining_principal -= monthly_principal

# 转换为DataFrame
df2 = pd.DataFrame(records)

# 导出Excel
file_path2 = "C:/Users/许亚西/Desktop/python/公积金贷款还款与收支明细-100.xlsx"
df2.to_excel(file_path2, index=False)

file_path2
