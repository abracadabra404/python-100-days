total = 0
for i in range(1, 101):
    if i % 2 == 0:
        total += i
print(total)

total2 = 0
for i in range(2, 101, 2):
    total2 += i
print(total2)

print(sum(range(2, 101, 2)))

total3 = 0
i = 2
while i <= 100:
    total3 += i
    i += 2
print(total3)

# break
total4 = 0
i = 2
while True:
    total4 += i
    i += 2
    if i > 100:
        break
print(total4)

# continue
total5 = 0
for i in range(1,101):
    if i % 2 != 0:
        continue
    total5 += i
print(total5)

# the multiplication table
for i in range(1, 10):
    for j in range(1,i + 1):
        print(f'{i}x{j}={i * j}', end='\t')
    print()
