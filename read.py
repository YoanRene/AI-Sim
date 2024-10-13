a = open('aaa.md','r',encoding='utf-8').read()

# print(a)

codigos = []

ss = a.split('```python')
for i in range(1,len(ss)):
    codigos.append(ss[i].split('```')[0])

# print(len(codigos))

for code in codigos:
    exec(code)

