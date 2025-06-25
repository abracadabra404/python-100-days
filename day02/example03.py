# 二进制
print(0b100)

# 八进制
print(0o100)
# 十进制
print(100)

# 十六进制
print(0x100)

# 数学写法
print(123.456)

# 科学计数法
print(1.23456e2)

# 使用type函数检查变量的类型
a = 100;
b = 123.44
c = 'hello,python'
d = True;
e = '123.45'
f = '123'
g = '100'

print(type(a))
print(type(b))
print(type(c))
print(type(d))

# 变量的类型转换操纵

print(float(a))
print(int(b))
print(int(f))
print(int(f, base=16))  # str类型的123按照十六进制转换成int
print(int(g, base=2)) # str类型的100按照二进制转成int
print(float(e))
print(bool(c))
print(int(d))
print(chr(a)) # int 类型的100转成str，输出'd'
print(ord('d')) # str类型的’d‘ 转换成int，输出100

