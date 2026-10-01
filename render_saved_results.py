"""Render confusion matrices and ROC curves from saved results. No training or inference."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
ROOT=Path(__file__).resolve().parent
P=ROOT/'results'; O=P/'figures'
O.mkdir(parents=True,exist_ok=True)
settings=[('random','Random Kaggle'),('author_disjoint','Known-author\nKaggle'),('kaggle_to_isot','Kaggle to ISOT'),('isot_to_kaggle','ISOT to Kaggle')]
plt.rcParams.update({'font.family':'serif','font.size':8,'pdf.fonttype':42,'axes.labelsize':8,'axes.titlesize':8,'legend.fontsize':7})
fig,axs=plt.subplots(1,4,figsize=(7.16,1.9))
for ax,(key,title) in zip(axs,settings):
 r=pd.read_csv(P/'tables'/('table_'+key+'.csv')).set_index('model').loc['LinearSVC']
 import numpy as np
 cm=np.array([[r.TN,r.FP],[r.FN,r.TP]],dtype=int)
 ax.imshow(cm/cm.sum(axis=1,keepdims=True),cmap='Blues',vmin=0,vmax=1)
 for (i,j),n in np.ndenumerate(cm):ax.text(j,i,str(n),ha='center',va='center',fontsize=9,color='white' if cm[i,j]/cm[i].sum()>.5 else 'black')
 ax.set(xticks=[0,1],xticklabels=['Real','Fake'],yticks=[0,1],yticklabels=['Real','Fake'],xlabel='Predicted',title=title)
 ax.tick_params(length=0)
axs[0].set_ylabel('True')
fig.tight_layout(pad=.4,w_pad=1.1);fig.savefig(O/'confusion_row.pdf');fig.savefig(O/'confusion_row.png',dpi=200);plt.close(fig)
fig,ax=plt.subplots(figsize=(3.45,2.75))
styles=['-','--','-.',':']
for (key,title),sty in zip(settings,styles):
 d=pd.read_csv(P/'predictions'/key/'LinearSVC.csv.gz');fpr,tpr,_=roc_curve(d.y_true,d.score)
 r=pd.read_csv(P/'tables'/('table_'+key+'.csv')).set_index('model').loc['LinearSVC']
 ax.plot(fpr,tpr,sty,lw=1.3,label=f'{title.replace(chr(10)," ")} ({r.roc_auc:.4f})')
ax.plot([0,1],[0,1],color='0.65',lw=.7)
ax.set(xlabel='False positive rate',ylabel='True positive rate',xlim=(0,1),ylim=(0,1.02))
ax.legend(loc='lower right',frameon=False);ax.grid(alpha=.15)
fig.tight_layout(pad=.4);fig.savefig(O/'roc_selected.pdf');fig.savefig(O/'roc_selected.png',dpi=200);plt.close(fig)
