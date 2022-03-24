import json
f = open('aa.txt', 'w')
f.write(json.dumps({"a": "1"}))
f.close()

f = open('aa.txt', 'r')

a = json.loads(f.read())
print(a['a'])
f.close()