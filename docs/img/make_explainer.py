# Explainer v2: lead with the clean comparison (only speaking order changes), wording flip as control.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

SURF="#fcfcfb"; T1="#0b0b0b"; T2="#52514e"; T3="#8a8983"; PANEL="#f1f0ec"
FIRST="#2a78d6"; LAST="#eb6834"
Q1="“"; Q2="”"; DOT="·"

fig = plt.figure(figsize=(8,7.6), dpi=200); fig.patch.set_facecolor(SURF)
ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")

ax.text(3,97,"Same debaters. Change who speaks last, and the AI judge's verdict follows.", fontsize=13.2, fontweight="bold", color=T1, va="top")
ax.text(3,92.3,"Two identical AI debaters (Claude Haiku 4.5) argue the trolley problem for three rounds; another AI\n(gpt-5-mini) picks the winner. 20 debates per test. Quotes are shortened from real debates.",
        fontsize=8.8, color=T2, va="top", linespacing=1.4)

def bubble(x,y,w,h,col,head,quote,mark=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.35,rounding_size=2", fc=col,
                                ec=T1 if mark else "none", lw=2.4 if mark else 0))
    ax.text(x+1.3,y+h-1.4,head, fontsize=8.0, fontweight="bold", color="white", va="top")
    ax.text(x+1.3,y+h-4.9,quote, fontsize=8.6, color="white", va="top", linespacing=1.25)

def arrow(x0,x1,y):
    ax.annotate("", xy=(x1,y), xytext=(x0,y), arrowprops=dict(arrowstyle="-|>", color=T3, lw=1.2))

NOANS=f"{Q1}No correct answer:\nframeworks conflict.{Q2}"
ANS=f"{Q1}There is an answer:\nminimize harm.{Q2}"

# ---- Panel 1: the clean comparison
ax.add_patch(FancyBboxPatch((1.5,33.5),97,49.5,boxstyle="round,pad=0,rounding_size=2", fc=PANEL, ec="none"))
ax.text(4,81.2,"The test that matters: only the speaking order changes", fontsize=10.8, fontweight="bold", color=T1, va="top")
ax.text(4,77.3,f"Same proposition ({Q1}There is no correct answer to the trolley problem{Q2}), same sides, same arguments.",
        fontsize=8.5, color=T2, va="top")

rows=[(70.5-11, "Original order", ("Speaks 1st  "+DOT+"  for", NOANS, True), ("Speaks last  "+DOT+"  against", ANS, False), "0 of 20"),
      (70.5-11-17.5, "Order reversed", ("Speaks 1st  "+DOT+"  against", ANS, False), ("Speaks last  "+DOT+"  for", NOANS, True), "15 of 20")]
for by,label,first,last,score in rows:
    ax.text(4,by+12.6,label, fontsize=9.2, fontweight="bold", color=T1, va="bottom")
    bubble(4,by,27,10.5,FIRST,first[0],first[1],first[2]); arrow(32.2,35.0,by+5.25)
    bubble(36.2,by,27,10.5,LAST,last[0],last[1],last[2]); arrow(64.4,67.2,by+5.25)
    ax.text(69,by+8.2,f"{Q1}No correct answer{Q2} side won", fontsize=8.6, color=T2, va="center")
    ax.text(69,by+3.4,score, fontsize=15, fontweight="bold", color=T1, va="center")
ax.text(4,35.3,"Outlined box = the side arguing “no correct answer.” It lost all 20 speaking first, and won 15 of 20 speaking last.",
        fontsize=8.1, color=T1, va="bottom", style="italic")

# ---- Panel 2: control
ax.text(3,28.5,"Control: flip the wording, keep the order", fontsize=10, fontweight="bold", color=T1, va="top")
ax.text(3,24.8,f"Proposition: {Q1}There IS a correct answer to the trolley problem.{Q2}", fontsize=8.5, color=T2, va="top")
by=9.5
bubble(4,by,27,10.5,FIRST,"Speaks 1st  "+DOT+"  for",ANS); arrow(32.2,35.0,by+5.25)
bubble(36.2,by,27,10.5,LAST,"Speaks last  "+DOT+"  against",NOANS); arrow(64.4,67.2,by+5.25)
ax.text(69,by+8.2,"Last speaker won", fontsize=8.6, color=T2, va="center")
ax.text(69,by+3.4,"20 of 20", fontsize=15, fontweight="bold", color=T1, va="center")

ax.text(3,2.0,f"AI Argue {DOT} pre-registered {DOT} across all 60 identical-debater runs the last speaker won 55 {DOT} databloom.net/ai-argue.html",
        fontsize=7.4, color=T3, va="bottom")
fig.savefig("ai-argue-explainer.png", facecolor=SURF)
print("ok")
