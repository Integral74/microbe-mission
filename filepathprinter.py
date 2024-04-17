import os
import re
def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

agents = list(sorted_alphanumeric(os.listdir("images/agents")))
parts = list(sorted_alphanumeric(os.listdir("images/parts")))
other = list(sorted_alphanumeric(os.listdir("images/other")))
for filename in agents:
    filepath = "images/agents" + "/" + filename
    print(f'\"{filepath}\": " ",')

for filename in parts:
    filepath = "images/parts" + "/" + filename
    print(f'\"{filepath}\": " ",')

for filename in other:
    filepath = "images/other" + "/" + filename
    print(f'\"{filepath}\": " ",')