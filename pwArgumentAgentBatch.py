import os
import warnings
from itertools import combinations

from tqdm import tqdm

warnings.filterwarnings("ignore")

player_names = ["Bob", "Alice", "Eve", "John"]

item_names = [
    "Diesel Engine",
    "Electric Engine",
    "Compressed Natural GAS",
    "Fuel Cell",
    "Hybrid Engine",
]

agents_couple = combinations(player_names, 2)

if os.path.exists("figures/results.csv"):
    os.remove("figures/results.csv")
file = open("figures/results.csv", "w")
file.write("agent1,agent2,iswin,item\n")
file.close()
for epoch in tqdm(range(8)):
    for first, second in agents_couple:
        os.system(f"python pwArgumentAgent.py {first} {second}")

import pandas as pd
import plotly.express as px

results = pd.read_csv('figures/results.csv')
results["epoch"] = [i // 6 for i in range(len(results))]

df = pd.DataFrame()
for epoch in range(8):
    for agent in player_names:
        temp = results[results.agent1 == agent]
        temp["cumulative_wins"] = temp.iswin.cumsum()
        df = pd.concat([df, temp[["cumulative_wins", "epoch", "agent1"]]])

fig = px.line(df, x="epoch", y="cumulative_wins", color="agent1", template="plotly_white")
fig.write_image("figures/cumulative_wins_per_agent.png")

df = pd.DataFrame()

for item in item_names:
    temp = results[results.item == item]
    temp["cumulative_wins"] = temp.iswin.cumsum()
    df = pd.concat([df, temp[["cumulative_wins", "epoch", "item"]]])

fig = px.line(df, x="epoch", y="cumulative_wins", color="item", template="plotly_white")
fig.write_image("figures/cumulative_wins_per_item.png")
