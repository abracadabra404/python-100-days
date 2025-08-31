"""
BMI计算器
"""

height = float(input('Your height(cm):'))
weight = float(input('Your weight(kg):'))
bmi = weight / (height / 100) ** 2
print(f'{bmi = : .1f}')

if bmi < 18.5:
    print('Your body is underweight')
elif bmi < 24:
    print('Your body is great')
elif bmi < 27:
    print('Your body is overweight')
elif bmi < 30:
    print('Your body is mild obesity')
elif bmi < 35:
    print('Your body is moderate obesity')
else:
    print('Your body is server obesity')

"""
match-case 结构
"""
status_code = int(input('response code:'))

# match status_code:
#     case 400 | 405 : description = 'Invalid Request'
#     case 401 | 403 : description = 'Not Allowed'
#     case 418: description = 'I am a teapot'
#     case 429: description = 'Too many requests'
#     case _: description = 'Unknown Status Code'
# print('status code description:',description)

