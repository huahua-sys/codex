#!/usr/bin/env python3
"""Reproducible presentation of already frozen evidence, no additional tests."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'research/phase3/figures'
data=list(csv.DictReader((BASE/'relative_vol_falsification.csv').open()))
for r in data:
    for k in ['mean_pp','low_pp','high_pp']:r[k]=float(r[k])
fig,axes=plt.subplots(1,2,figsize=(12,4.8),sharey=True)
for axis,h in zip(axes,['12m','24m']):
    rows=[r for r in data if r['horizon']==h]
    for i,r in enumerate(rows):
        color='#146b78' if r['low_pp']>0 else '#666666'
        axis.errorbar(r['mean_pp'],3-i,xerr=[[r['mean_pp']-r['low_pp']],[r['high_pp']-r['mean_pp']]],fmt='o',capsize=4,color=color,linewidth=1.8)
        axis.text(r['high_pp']+.6,3-i,f"nq={r['quarters']}",va='center',fontsize=9,color='#444444')
    axis.axvline(0,ls='--',color='#bbbbbb');axis.set_title(h+' holding return contrast');axis.set_xlabel('High relative-vol minus other group (percentage points)');axis.set_yticks(range(4));axis.grid(axis='x',alpha=.2)
    axis.set_xlim(min(r['low_pp'] for r in data)-3,max(r['high_pp'] for r in data)+8)
axes[0].set_yticklabels([r['label'] for r in data if r['horizon']=='12m'][::-1]);fig.suptitle('A local association survives some attacks; no alpha or investment principle established',fontsize=12)
fig.text(.02,.015,'500 joint two-calendar-year block draws; exploratory, unadjusted for multiple testing. nq = paired quarters, not independent worlds.',fontsize=9,color='#555555');fig.tight_layout(rect=[0,.08,1,.92])
for suffix in ['png','svg']:fig.savefig(BASE/f'relative_vol_falsification.{suffix}',dpi=170)
plt.close(fig)
print('Saved complete intervals; PNG/SVG plus source CSV. New tests=0.')
