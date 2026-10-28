import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

SURF="#fcfcfb"; T1="#0b0b0b"; T2="#52514e"; T3="#8a8983"; GRID="#e4e3df"
A_COL="#2a78d6"; B_COL="#eb6834"

groups = [
  ("Identical debaters: Haiku vs Haiku, 25 words each", [
     ("Original proposition", 0, 20),
     ("Flipped proposition", 0, 20)]),
  ("Stronger (Sonnet) vs weaker (Haiku) model, 25 words each", [
     ("Sonnet in A, Haiku in B", 0, 10),
     ("Haiku in A, Sonnet in B", 3, 7)]),
  ("Weaker model gets 4× the words: Haiku 100 vs Sonnet 25", [
     ("Haiku in A", 9, 1),
     ("Haiku in B", 0, 10)]),
]

plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10})
fig, ax = plt.subplots(figsize=(8,7.0), dpi=200)
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)

y=0; yt=[]; ylab=[]; heads=[]
for gname, rows in groups:
    heads.append((y, gname)); y-=0.75
    for lab,a,b in rows:
        n=a+b; fa=a/n; fb=b/n
        ax.barh(y, fa, left=0, height=0.62, color=A_COL, edgecolor=SURF, linewidth=1.5)
        ax.barh(y, fb, left=fa, height=0.62, color=B_COL, edgecolor=SURF, linewidth=1.5)
        # value labels in text ink
        if a>0: ax.text(fa/2, y, f"{a}", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        ax.text(fa+fb/2, y, f"{b}", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        yt.append(y); ylab.append(lab); y-=0.8
    y-=0.35

for hy, g in heads:
    ax.text(-0.43, hy-0.08, g, ha="left", va="center", color=T1, fontsize=10, fontweight="bold", transform=ax.get_yaxis_transform(), zorder=5)

ax.axvline(0.5, color=T3, linestyle=(0,(3,3)), linewidth=1, zorder=0.5)
ax.text(0.5, y+0.05, "fair judge: 50/50", ha="center", va="bottom", color=T2, fontsize=8.5, bbox=dict(facecolor=SURF, edgecolor="none", pad=1))

ax.set_yticks(yt); ax.set_yticklabels(ylab, color=T1)
ax.set_xlim(0,1); ax.set_ylim(y-0.05, heads[0][0]+0.5)
ax.set_xticks([0,0.25,0.5,0.75,1]); ax.set_xticklabels(["0%","25%","50%","75%","100%"], color=T2, fontsize=9)
ax.tick_params(axis="y", length=0, pad=8); ax.tick_params(axis="x", length=0)
for s in ax.spines.values(): s.set_visible(False)
ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
ax.set_xlabel("Share of debates won", color=T2, fontsize=9)

fig.text(0.02, 0.965, "An AI judge picked the second speaker 40 times out of 40", ha="left", va="top", fontsize=14.5, fontweight="bold", color=T1)
fig.text(0.02, 0.922, "Even with the proposition flipped. Only a 4× word budget beat it.", ha="left", va="top", fontsize=10.5, color=T2)
fig.text(0.02, 0.878, "Original proposition:", ha="left", va="top", fontsize=9, color=T2)
fig.text(0.205, 0.878, "“There is no correct answer to the trolley problem.”", ha="left", va="top", fontsize=9, color=T1)
fig.text(0.02, 0.852, "Flipped proposition:", ha="left", va="top", fontsize=9, color=T2)
fig.text(0.205, 0.852, "“There is a correct answer to the trolley problem.”", ha="left", va="top", fontsize=9, color=T1)
fig.text(0.02, 0.826, "Debaters:", ha="left", va="top", fontsize=9, color=T2)
fig.text(0.205, 0.826, "Claude Sonnet 4.5 (stronger) vs Claude Haiku 4.5 (weaker, cheaper).  Judge: gpt-5-mini", ha="left", va="top", fontsize=9, color=T1)
fig.legend(handles=[Patch(color=A_COL,label="Seat A: speaks first, argues for"),
                    Patch(color=B_COL,label="Seat B: speaks second, argues against")],
           loc="upper left", bbox_to_anchor=(0.015,0.805), ncol=2, frameon=False, fontsize=9.5, handlelength=1.2, labelcolor=T1)
fig.text(0.02, 0.018, "AI Argue · 80 pre-registered debates · 3 rounds · all rows except “Flipped” use the original proposition · databloom.net/ai-argue.html",
         ha="left", va="bottom", fontsize=7.5, color=T3)
plt.subplots_adjust(left=0.30, right=0.96, top=0.735, bottom=0.11)
fig.savefig("ai-argue-batch1.png", facecolor=SURF)
fig.savefig("ai-argue-batch1.svg", facecolor=SURF)
print("ok")
