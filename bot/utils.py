import string
import random
import json
import re

def string_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_config():
    with open('../config.json', 'r',  encoding='utf-8') as f:
     config = json.load(f)
     return config

def check_ip(ip):
    res = [0<=int(x)<256 for x in re.split(r'\.',re.match(r'^\d+\.\d+\.\d+\.\d+$', ip).group(0))].count(True)==4
    return res

if __name__ == '__main__':
    res = string_generator()
    print(res)

