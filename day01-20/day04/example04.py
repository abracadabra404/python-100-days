import math

# 赋值运算符和复合赋值运算符
a = 10
b = 3
a += b
a *= a + 2
print(a)


# 海象运算符 :=

# print(a = 10)

print((a := 10))
print(a)

# 运算符和表达式应用
# 华氏温度转摄氏温度
# f = float(input('请输入华氏温度：'))
# c = (f - 32) / 1.8
# print('%.1f华氏度 = %.1f摄氏度' % (f, c))

# 输入半径计算圆的周长和面积
# radius = float(input('请输入圆的半径：'))
# perimeter =2 * math.pi * radius
# area = math.pi * radius ** 2
# print(f'周长：{perimeter:.2f}')
# print(f'面积：{area:.2f}')

# 判断是否为闰年
# 判断闰年的规则是：1. 公元年份非 4 的倍数是平年；2. 公元年份为 4 的倍数但非 100 的倍数是闰年；3. 公元年份为 400 的倍数是闰年
year = int(input('请输入年份：'))
is_leap = year % 4 == 0 and year % 100 != 0 or year % 400 == 0
print(f'{is_leap = }')

