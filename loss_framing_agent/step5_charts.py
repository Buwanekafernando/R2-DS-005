# CHARTS 

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("charts", exist_ok=True)

df = pd.read_csv("outputs/final_results.csv")
print(f"Loaded {len(df)} rows")

# BERT scores
df['ab_winner'] = np.where(df['bert_gain_score'] >= df['bert_loss_score'], 'A - Gain', 'B - Loss')

total = len(df)
gain_win = (df['ab_winner'] == 'A - Gain').sum()
loss_win = (df['ab_winner'] == 'B - Loss').sum()

fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Loss Framing Agent — Research Results',
             fontsize=16, fontweight='bold', y=1.01)

# A/B winner
ax1 = axes[0, 0]
bars = ax1.bar(['Gain Framing', 'Loss Framing'],
               [gain_win, loss_win],
               color=['#2196F3', '#FF5722'], width=0.5, edgecolor='white')
ax1.set_title('A/B Test: Overall Winner', fontweight='bold')
ax1.set_ylabel('Number of wins')
ax1.set_ylim(0, total)
for bar, val in zip(bars, [gain_win, loss_win]):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 4,
             f'{val}\n({val/total*100:.1f}%)', ha='center', fontweight='bold')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# A/B wins by category
ax2 = axes[0, 1]
cat_ab = df.groupby('product_category')['ab_winner'].value_counts().unstack(fill_value=0)
categories = cat_ab.index.tolist()
x = np.arange(len(categories))
gain_vals = cat_ab.get('A - Gain', pd.Series([0]*len(categories), index=cat_ab.index)).values
loss_vals = cat_ab.get('B - Loss', pd.Series([0]*len(categories), index=cat_ab.index)).values
ax2.bar(x - 0.2, gain_vals, 0.35, label='Gain wins', color='#2196F3', edgecolor='white')
ax2.bar(x + 0.2, loss_vals, 0.35, label='Loss wins', color='#FF5722', edgecolor='white')
ax2.set_title('A/B Test Wins by Category', fontweight='bold')
ax2.set_ylabel('Number of wins')
ax2.set_xticks(x)
ax2.set_xticklabels(categories, rotation=35, ha='right', fontsize=9)
ax2.legend()
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Average sentiment scores
ax3 = axes[0, 2]
g_avg = df['gain_sentiment'].mean()
l_avg = df['loss_sentiment'].mean()
bars3 = ax3.bar(['Gain Sentiment', 'Loss Sentiment'],
                [g_avg, l_avg],
                color=['#4CAF50', '#FF9800'], width=0.4, edgecolor='white')
ax3.set_title('Average Sentiment Score', fontweight='bold')
ax3.set_ylabel('Sentiment score (-1 to +1)')
ax3.set_ylim(0, 1.0)
ax3.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
for bar, val in zip(bars3, [g_avg, l_avg]):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             f'{val:.3f}', ha='center', fontweight='bold')
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# Tone distribution
ax4 = axes[1, 0]
tone_counts = df['tone_label'].value_counts()
ax4.pie(tone_counts.values,
        labels=[f"{l}\n({v})" for l, v in zip(tone_counts.index, tone_counts.values)],
        colors=['#4CAF50', '#FF9800', '#F44336'],
        autopct='%1.1f%%', startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2})
ax4.set_title('Tone Distribution', fontweight='bold')

# FOMO score 
ax5 = axes[1, 1]
ax5.hist(df['fomo_score'], bins=8, color='#9C27B0', edgecolor='white')
ax5.axvline(df['fomo_score'].mean(), color='red', linestyle='--',
            label=f"Mean = {df['fomo_score'].mean():.2f}")
ax5.set_title('FOMO Score Distribution', fontweight='bold')
ax5.set_xlabel('FOMO score')
ax5.set_ylabel('Number of messages')
ax5.legend()
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)

# Avg BERT scores by category
ax6 = axes[1, 2]
cat_gain = df.groupby('product_category')['bert_gain_score'].mean()
cat_loss = df.groupby('product_category')['bert_loss_score'].mean()
x6 = np.arange(len(cat_gain))
ax6.bar(x6 - 0.2, cat_gain.values, 0.35, label='Gain', color='#2196F3', edgecolor='white')
ax6.bar(x6 + 0.2, cat_loss.values, 0.35, label='Loss', color='#FF5722', edgecolor='white')
ax6.set_title('Avg BERT Score by Category', fontweight='bold')
ax6.set_ylabel('BERT confidence score')
ax6.set_xticks(x6)
ax6.set_xticklabels(cat_gain.index, rotation=35, ha='right', fontsize=9)
ax6.legend()
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig("charts/loss_framing_charts.png", dpi=150, bbox_inches='tight')
plt.show()
print("Charts saved to charts/loss_framing_charts.png")