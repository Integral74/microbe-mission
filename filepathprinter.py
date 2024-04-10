import os

for filename in os.listdir("images/agents/"):
    filepath = "images/agents" + "/" + filename

    print(f"\'{filepath}\':")

for filename in os.listdir("images/parts/"):
    filepath = "images/parts" + "/" + filename

    print(f"\'{filepath}\':")

for filename in os.listdir("images/other/"):
    filepath = "images/other" + "/" + filename

    print(f"\'{filepath}\':")