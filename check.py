import re

ips = []
with open('./abc.txt', 'r') as f:
    pattern = re.compile('\d{,3}\.\d{,3}\.\d{,3}\.\d{,3}')
    for line in f.readlines():
        result = pattern.findall(line)
        if result:
            ips.append(result[0])
    ips = set(ips)

with open('./abb.txt', 'w') as f:
    f.write(str(ips))
