#!/usr/bin/env python3
"""VeriFake reviewer repair. Original results are never modified.

Scientific runs require local data and the archived previous results.
--smoke uses synthetic data, fewer estimators, and a separate output directory.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback
import zipfile

import joblib
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.base import clone
from sklearn.ensemble import (AdaBoostClassifier, ExtraTreesClassifier,
    GradientBoostingClassifier, RandomForestClassifier)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
    matthews_corrcoef, precision_score, recall_score, roc_auc_score, roc_curve,
    make_scorer)
from sklearn.model_selection import (GridSearchCV, GroupShuffleSplit,
    StratifiedGroupKFold, StratifiedKFold, train_test_split)
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits
from verifake_text import normalize, normalize_batch, news_input

SEED = 42
TFIDF = dict(lowercase=True, stop_words="english", ngram_range=(1, 2),
    min_df=3, max_df=0.9, sublinear_tf=True, max_features=50000, dtype=np.float32)
TITLE = "VeriFake: A TF-IDF and Ensemble Learning Framework for Web-Based Fake News Detection"

def metadata_json_safe(value):
    """Encode nonfinite estimator metadata explicitly; never sanitize metrics."""
    if isinstance(value, dict):
        return {k: metadata_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [metadata_json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return metadata_json_safe(value.tolist())
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        if np.isnan(value):
            return "NaN"
        return "+Infinity" if value > 0 else "-Infinity"
    if isinstance(value, np.generic):
        return value.item()
    return value

def json_write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, default=str, allow_nan=False))
    tmp.replace(path)

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def text_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

def models(smoke=False):
    d = {
      "LR": (LogisticRegression(solver="liblinear", max_iter=2000, random_state=SEED), {"C":[1,10,100]}),
      "MNB": (MultinomialNB(), {"alpha":[.01,.1,1.]}),
      "BNB": (BernoulliNB(), {"alpha":[.01,.1,1.]}),
      "LinearSVC": (LinearSVC(max_iter=5000, random_state=SEED), {"C":[.1,1,10]}),
      "SVC-RBF": (SVC(kernel="rbf", gamma="scale", cache_size=1000, random_state=SEED), {"C":[1,10]}),
      "KNN": (KNeighborsClassifier(metric="cosine", algorithm="brute", weights="distance", n_jobs=1), {"n_neighbors":[5,15,31]}),
      "DT": (DecisionTreeClassifier(random_state=SEED), {"max_depth":[None,50], "min_samples_leaf":[1,5]}),
      "RF": (RandomForestClassifier(n_estimators=300, n_jobs=1, random_state=SEED), {"max_features":["sqrt","log2"], "min_samples_leaf":[1,2]}),
      "ET": (ExtraTreesClassifier(n_estimators=300, n_jobs=1, random_state=SEED), {"max_features":["sqrt","log2"], "min_samples_leaf":[1,2]}),
      "AdaBoost": (AdaBoostClassifier(random_state=SEED), {"n_estimators":[200,400], "learning_rate":[.5,1.]}),
      "GB": (GradientBoostingClassifier(n_estimators=300, max_depth=3, subsample=.8, max_features=.1, random_state=SEED), {"learning_rate":[.1,.3]}),
      "MLP": (MLPClassifier(hidden_layer_sizes=(128,), batch_size=256, early_stopping=True,
          validation_fraction=.1, max_iter=50, n_iter_no_change=3, random_state=SEED), {"alpha":[1e-4,1e-3]})}
    try:
        from xgboost import XGBClassifier
        d["XGB"] = (XGBClassifier(objective="binary:logistic", max_depth=6,
            learning_rate=.1, subsample=.8, colsample_bytree=.5, tree_method="hist",
            device="cpu", n_jobs=1, random_state=SEED, eval_metric="logloss"),
            {"n_estimators":[300,600]})
    except ImportError:
        if not smoke:
            raise RuntimeError("XGBoost is missing. Activate the existing verifake environment.")
    if smoke:
        for n, (m, grid) in d.items():
            d[n] = (m, {k: [v[0]] for k,v in grid.items()})
            if "n_estimators" in m.get_params():
                m.set_params(n_estimators=5)
                if "n_estimators" in grid: d[n][1]["n_estimators"]=[5]
        d["MLP"][0].set_params(hidden_layer_sizes=(8,), max_iter=3, batch_size=32)
    return d

def pipe_for(name, params=None):
    m = clone(MODELS[name][0])
    if params: m.set_params(**params)
    return Pipeline([("tfidf", TfidfVectorizer(**TFIDF)), ("clf", m)])

def score_of(pipe, X):
    clf = pipe.named_steps["clf"]
    assert list(clf.classes_) == [0,1]
    if hasattr(clf, "predict_proba"): return pipe.predict_proba(X)[:,1]
    return pipe.decision_function(X)

def metric(y, pred, score):
    assert set(np.unique(y)) == {0,1}
    assert np.isfinite(score).all()
    tn,fp,fn,tp = [int(v) for v in confusion_matrix(y,pred,labels=[0,1]).ravel()]
    return dict(TN=tn,FP=fp,FN=fn,TP=tp,n=len(y),
      accuracy=accuracy_score(y,pred), precision=precision_score(y,pred,zero_division=0),
      recall=recall_score(y,pred,zero_division=0), f1=f1_score(y,pred,zero_division=0),
      specificity=tn/(tn+fp), mcc=matthews_corrcoef(y,pred), roc_auc=roc_auc_score(y,score))

def add_variants(df):
    for c in ["title","author","text"]:
        if c not in df: df[c]=""
        df[c]=df[c].fillna("").astype(str)
        df["n_"+c]=df[c].map(normalize)
    df["title_text"]=(df.n_title+" "+df.n_text).str.strip()
    df["title_only"]=df.n_title
    df["author_title"]=(df.n_author+" "+df.n_title).str.strip()
    df["author_title_text"]=(df.n_author+" "+df.title_text).str.strip()
    df["body_hash"]=df.n_text.map(text_hash)
    return df

def dedup(df, key, tag, audit):
    sizes=df.groupby(key).label.nunique()
    conflicts=set(sizes[sizes>1].index)
    bad=df[key].isin(conflicts)
    removed=df[bad].copy()
    removed["reason"]=tag+"_conflicting_labels"
    audit.append(removed[["sample_id","label","reason"]])
    df=df[~bad].copy()
    dup=df.duplicated(key)
    removed=df[dup].copy();removed["reason"]=tag+"_exact_duplicate"
    audit.append(removed[["sample_id","label","reason"]])
    return df[~dup].copy()

def canonical_body(s):
    # The same matching transformation is applied to both datasets.
    s=re.sub(r"^[^\n]{0,150}?\(reuters\)\s*-\s*", "", str(s), flags=re.I)
    return normalize(re.sub(r"\breuters\b", " ", s, flags=re.I))

def synthetic_data():
    rows=[]
    for i in range(360):
        y=i%2
        words="report verified science" if y==0 else "rumor fabricated claim"
        # Letter-only codes survive the exact normalization used in the study.
        code=chr(97+i//26)+chr(97+i%26)
        rows.append(dict(id=i,title="sample "+code,author="writer "+chr(97+(i//2)%30),
            text=words+" story "+code+" news discussion "+chr(97+i%7),label=y))
    return pd.DataFrame(rows)

def load_data(args):
    audit=[]
    if args.smoke:
        raw=synthetic_data()
    else:
        raw=pd.read_csv(args.data/"train.csv")
        assert raw.shape==(20800,5),raw.shape
        assert list(raw.columns)==["id","title","author","text","label"]
        assert raw.label.value_counts().to_dict()=={1:10413,0:10387}
        assert raw.id.is_unique
    raw["sample_id"]="K_"+raw.id.astype(str)
    df=add_variants(raw.copy())
    empty=df.n_text.str.len()==0
    removed=df[empty].copy();removed["reason"]="empty_normalized_body"
    audit.append(removed[["sample_id","label","reason"]])
    df=dedup(df[~empty],"title_text","title_body",audit).reset_index(drop=True)
    old_ids=df.sample_id.tolist()
    df=dedup(df,"body_hash","body",audit).reset_index(drop=True)
    same=(df.sample_id.tolist()==old_ids)
    if args.smoke:
        iso=synthetic_data()
        iso["id"]+=10000
        iso["title"]="external "+iso.title
        iso["text"]="external archive "+iso.text
        iso["sample_id"]="I_"+iso.id.astype(str)
    else:
        f=pd.read_csv(args.data/"Fake.csv");t=pd.read_csv(args.data/"True.csv")
        assert len(f)==23481 and len(t)==21417,(len(f),len(t))
        f["label"]=1;t["label"]=0
        iso=pd.concat([f,t],ignore_index=True)
        iso["sample_id"]="I_"+iso.index.astype(str)
    iso["text"]=iso.text.fillna("").map(canonical_body)
    iso=add_variants(iso)
    iso=iso[iso.n_text.str.len()>0].copy()
    iso=dedup(iso,"body_hash","isot_body",audit)
    kb=set(df.text.map(canonical_body));kt=set(df.n_title[df.n_title.str.split().str.len()>=5])
    overlap=iso.n_text.isin(kb)|iso.n_title.isin(kt)
    removed=iso[overlap].copy();removed["reason"]="cross_dataset_exact_body_or_title"
    audit.append(removed[["sample_id","label","reason"]])
    iso=iso[~overlap].reset_index(drop=True)
    assert not set(iso.n_text)&kb
    pd.concat(audit,ignore_index=True).to_csv(OUT/"removed_rows.csv",index=False)
    json_write(OUT/"data_audit.json",dict(raw_n=len(raw),clean_kaggle_n=len(df),
        clean_kaggle_labels=df.label.value_counts().to_dict(),clean_isot_n=len(iso),
        clean_isot_labels=iso.label.value_counts().to_dict(),
        primary_rows_unchanged_from_old_cleaning=same,
        author_missing_excluded_from_group_test=int((df.n_author=="").sum()),
        duplicate_scope="Exact normalized bodies and title+body; cross-dataset canonical bodies and long titles. Near duplicates are not exhaustively removed.",
        labels={"0":"reliable/real","1":"unreliable/fake"},balancing="none"))
    return df,iso,same

def get_cv(frame, grouped):
    if grouped:
        cv=list(StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=SEED).split(frame,frame.label,frame.n_author))
    else:
        cv=list(StratifiedKFold(n_splits=3,shuffle=True,random_state=SEED).split(frame,frame.label))
    fold=np.full(len(frame),-1,dtype=int)
    for j,(a,b) in enumerate(cv):
        assert set(frame.iloc[a].label)=={0,1} and set(frame.iloc[b].label)=={0,1}
        assert not set(frame.iloc[a].body_hash)&set(frame.iloc[b].body_hash)
        if grouped: assert not set(frame.iloc[a].n_author)&set(frame.iloc[b].n_author)
        fold[b]=j
    return cv,fold

def fit_one(protocol,name,train,cv,frozen=None,old_cv=None):
    folder=OUT/"checkpoints"/protocol;folder.mkdir(parents=True,exist_ok=True)
    mp=folder/(name+".joblib");jp=folder/(name+".json")
    if mp.exists() and jp.exists():
        print("RESUME",protocol,name,flush=True)
        return joblib.load(mp),json.loads(jp.read_text())
    start=time.time()
    print("FIT",protocol,name,"rows",len(train),flush=True)
    if frozen is not None:
        pipe=pipe_for(name,frozen).fit(train.title_text,train.label)
        info=dict(best_params=frozen,cv_mcc=float(old_cv),selection="original training-only CV; unchanged rows and split")
    else:
        gs=GridSearchCV(pipe_for(name),{"clf__"+k:v for k,v in MODELS[name][1].items()},
            cv=cv,scoring=make_scorer(matthews_corrcoef),n_jobs=ARGS.workers,
            pre_dispatch=ARGS.workers,refit=True,error_score="raise",return_train_score=False)
        with joblib.parallel_backend("loky",inner_max_num_threads=1):
            gs.fit(train.title_text,train.label)
        pipe=gs.best_estimator_
        info=dict(best_params={k.replace("clf__",""):v for k,v in gs.best_params_.items()},
            cv_mcc=float(gs.best_score_),selection="training-only CV for this protocol")
        pd.DataFrame(gs.cv_results_).to_csv(folder/(name+"_cv.csv"),index=False)
    info.update(model=name,protocol=protocol,fit_seconds=time.time()-start,
        full_estimator_params=metadata_json_safe(pipe.named_steps["clf"].get_params()))
    tmp=mp.with_suffix(".tmp");joblib.dump(pipe,tmp);tmp.replace(mp);json_write(jp,info)
    return pipe,info

def evaluate(pipe,test,path,column="title_text"):
    path.parent.mkdir(parents=True,exist_ok=True)
    start=time.time()
    pred=pipe.predict(test[column]);score=score_of(pipe,test[column])
    seconds=time.time()-start
    saved=pd.DataFrame(dict(sample_id=test.sample_id.to_numpy(),y_true=test.label.to_numpy(),
        y_pred=pred,score=score))
    saved.to_csv(path,index=False,compression="gzip")
    # Recompute from the on-disk output, including AUC.
    saved=pd.read_csv(path)
    result=metric(saved.y_true,saved.y_pred,saved.score)
    result["predict_and_score_seconds"]=seconds
    return result

def run_protocol(protocol,train,test,grouped=False,use_old=False,old=None):
    cv,fold=get_cv(train,grouped)
    manifest=train[["sample_id","label","body_hash"]].copy();manifest["cv_validation_fold"]=fold
    if grouped: manifest["author_group_hash"]=train.n_author.map(text_hash)
    manifest.to_csv(OUT/(protocol+"_train_manifest.csv"),index=False)
    test[["sample_id","label","body_hash"]].to_csv(OUT/(protocol+"_test_manifest.csv"),index=False)
    rows=[];info_map={}
    old_table=pd.read_csv(ARGS.previous/"table_tuning_cv.csv").set_index("model") if use_old else None
    for name in MODEL_NAMES:
        reuse=use_old and name!="XGB"
        pipe,info=fit_one(protocol,name,train,cv,
            frozen=old["tuned"][name] if reuse else None,
            old_cv=old_table.loc[name,"cv_mcc_mean"] if reuse else None)
        row=evaluate(pipe,test,OUT/"predictions"/protocol/(name+".csv.gz"))
        row.update(model=name,cv_mcc=info["cv_mcc"],params=json.dumps(info["best_params"]))
        rows.append(row);info_map[name]=info
        pd.DataFrame(rows).to_csv(OUT/("table_"+protocol+".csv"),index=False)
    return info_map

def fixed_task(key,name,train,test,params,column="title_text"):
    dest=OUT/"predictions"/key/(name+".csv.gz");jp=dest.with_suffix(".json")
    if dest.exists() and jp.exists(): return json.loads(jp.read_text())
    print("REFIT",key,name,flush=True)
    pipe=pipe_for(name,params).fit(train[column],train.label)
    row=evaluate(pipe,test,dest,column);row.update(model=name,params=json.dumps(params))
    json_write(jp,row)
    return row

def xgb_diagnostic(train):
    path=OUT/"xgb_training_diagnostic.json"
    if path.exists() or "XGB" not in MODEL_NAMES: return
    from xgboost import DMatrix
    a,b=train_test_split(np.arange(len(train)),test_size=.2,stratify=train.label,random_state=1701)
    v=TfidfVectorizer(**TFIDF);xa=v.fit_transform(train.iloc[a].title_text);xb=v.transform(train.iloc[b].title_text)
    xa.sort_indices();xb.sort_indices()
    result={"scope":"Training subset only. CPU is the prespecified primary backend; GPU comparison is diagnostic.","devices":{}}
    for device in ["cpu","cuda"]:
        if device=="cuda":
            try:
                if subprocess.run(["nvidia-smi"],capture_output=True).returncode:continue
            except FileNotFoundError: continue
        try:
            m=clone(MODELS["XGB"][0]).set_params(device=device,n_estimators=5 if ARGS.smoke else 300)
            m.fit(xa,train.iloc[a].label)
            proba=m.predict_proba(xb)[:,1]
            explicit=m.get_booster().predict(DMatrix(xb))
            delta=float(np.max(np.abs(proba-explicit)))
            result["devices"][device]=dict(metrics=metric(train.iloc[b].label,(proba>=.5).astype(int),proba),
                sklearn_vs_dmatrix_max_abs_difference=delta,
                validation_score_quantiles=np.quantile(proba,[0,.01,.5,.99,1]).tolist())
            m.get_booster().save_model(OUT/("xgb_training_diagnostic_"+device+".ubj"))
        except Exception as e:
            result["devices"][device]={"error":repr(e)}
            if device=="cpu": raise
    json_write(path,result)

def uncertainty_and_tests(best):
    rows=[];preds={};yt=None
    for name in MODEL_NAMES:
        d=pd.read_csv(OUT/"predictions"/"random"/(name+".csv.gz"));y=d.y_true.to_numpy();p=d.y_pred.to_numpy()
        if yt is not None: assert np.array_equal(yt,y)
        yt=y;preds[name]=p;rng=np.random.default_rng(SEED);acc=[];mcc=[]
        for _ in range(20 if ARGS.smoke else 1000):
            b=rng.integers(0,len(y),len(y));acc.append((y[b]==p[b]).mean());mcc.append(matthews_corrcoef(y[b],p[b]))
        al,ah=np.percentile(acc,[2.5,97.5]);ml,mh=np.percentile(mcc,[2.5,97.5])
        rows.append(dict(model=name,acc_ci_lo=al,acc_ci_hi=ah,mcc_ci_lo=ml,mcc_ci_hi=mh))
    pd.DataFrame(rows).to_csv(OUT/"table_random_intervals.csv",index=False)
    rows=[]
    for name in MODEL_NAMES:
        if name==best:continue
        a=preds[best]==yt;b=preds[name]==yt;n01=int((a&~b).sum());n10=int((~a&b).sum())
        p=binomtest(min(n01,n10),n01+n10,.5).pvalue if n01+n10 else 1.
        rows.append(dict(model=name,n01=n01,n10=n10,p_raw=p))
    d=pd.DataFrame(rows).sort_values("p_raw");run=0;adj=[]
    for i,p in enumerate(d.p_raw):run=max(run,min(1,(len(d)-i)*p));adj.append(run)
    d["p_holm"]=adj;d.to_csv(OUT/"table_mcnemar.csv",index=False)

def figures(best):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    folder=OUT/"figures";folder.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size":9,"pdf.fonttype":42,"font.family":"serif"})
    settings=[("random","Random split"),("author_disjoint","Known-author disjoint"),
              ("kaggle_to_isot","Kaggle to ISOT"),("isot_to_kaggle","ISOT to Kaggle")]
    fig,axs=plt.subplots(2,2,figsize=(7.1,5.6))
    for ax,(key,title) in zip(axs.flat,settings):
        d=pd.read_csv(OUT/"predictions"/key/(best+".csv.gz"));cm=confusion_matrix(d.y_true,d.y_pred,labels=[0,1])
        ax.imshow(cm/cm.sum(axis=1,keepdims=True),cmap="Blues",vmin=0,vmax=1)
        for (r,c),n in np.ndenumerate(cm):ax.text(c,r,str(n),ha="center",va="center",color="white" if cm[r,c]/cm[r].sum()>.5 else "black")
        ax.set(xticks=[0,1],yticks=[0,1],xticklabels=["Real","Fake"],yticklabels=["Real","Fake"],
            xlabel="Predicted",ylabel="True",title=title)
    fig.tight_layout();fig.savefig(folder/"confusion_selected.pdf");fig.savefig(folder/"confusion_selected.png",dpi=300);plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(7.1,5.6))
    for ax,(key,title) in zip(axs.flat,settings):
        for name in dict.fromkeys([best,"LR","RF","MNB"]):
            if name not in MODEL_NAMES:continue
            d=pd.read_csv(OUT/"predictions"/key/(name+".csv.gz"));fpr,tpr,_=roc_curve(d.y_true,d.score)
            ax.plot(fpr,tpr,label=f"{name} ({roc_auc_score(d.y_true,d.score):.3f})")
        ax.plot([0,1],[0,1],":",color="gray");ax.set(title=title,xlabel="False positive rate",ylabel="True positive rate");ax.legend(fontsize=7)
    fig.tight_layout();fig.savefig(folder/"roc_comparison.pdf");fig.savefig(folder/"roc_comparison.png",dpi=300);plt.close(fig)

def main():
    global ARGS,OUT,MODELS,MODEL_NAMES
    parser=argparse.ArgumentParser()
    parser.add_argument("--data",type=Path,default=Path("data"))
    parser.add_argument("--previous",type=Path,default=Path(__file__).parent/"previous_results")
    parser.add_argument("--output",type=Path,default=Path("verifake_repair_results"))
    parser.add_argument("--workers",type=int,default=min(8,int(os.environ.get("SLURM_CPUS_PER_TASK","4"))))
    parser.add_argument("--smoke",action="store_true")
    parser.add_argument("--models",default="all",help="Only restricted for synthetic smoke testing")
    ARGS=parser.parse_args();assert ARGS.workers>0
    if ARGS.models!="all" and not ARGS.smoke:raise ValueError("A scientific run must include all models.")
    OUT=ARGS.output
    if ARGS.smoke:
        OUT=OUT.with_name(OUT.name+"_SYNTHETIC_SMOKE");TFIDF.update(max_features=1000,min_df=1)
    OUT.mkdir(parents=True,exist_ok=True)
    # Prevent two jobs from writing the same checkpoint directory.
    import fcntl
    lock=open(OUT/".run.lock","w")
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    MODELS=models(ARGS.smoke);MODEL_NAMES=list(MODELS) if ARGS.models=="all" else ARGS.models.split(",")
    assert all(n in MODELS for n in MODEL_NAMES)
    versions={}
    for pkg in ["numpy","pandas","scikit-learn","xgboost","scipy","joblib","matplotlib"]:
        try:versions[pkg]=importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:versions[pkg]="unavailable"
    env=dict(python=sys.version,packages=versions,platform=platform.platform(),workers=ARGS.workers,
        slurm_job_id=os.environ.get("SLURM_JOB_ID"),slurm_cpus=os.environ.get("SLURM_CPUS_PER_TASK"))
    json_write(OUT/"environment.json",env)
    source_hashes={Path(__file__).name:sha(__file__),"verifake_text.py":sha(Path(__file__).with_name("verifake_text.py"))}
    input_hashes={} if ARGS.smoke else {n:sha(ARGS.data/n) for n in ["train.csv","Fake.csv","True.csv"]}
    old=json.loads((ARGS.previous/"summary.json").read_text()) if not ARGS.smoke else None
    identity=dict(source=source_hashes,inputs=input_hashes,versions=versions,smoke=ARGS.smoke,models=MODEL_NAMES,
        previous={} if ARGS.smoke else {n:sha(ARGS.previous/n) for n in ["summary.json","table_tuning_cv.csv","heldout_predictions.csv"]})
    signature=OUT/"run_identity.json"
    if signature.exists():assert json.loads(signature.read_text())==identity,"Inputs/code/environment changed. Use a NEW --output directory."
    else:json_write(signature,identity)
    df,iso,same=load_data(ARGS)
    tr,te=train_test_split(np.arange(len(df)),test_size=.2,stratify=df.label,random_state=SEED)
    train,test=df.iloc[tr].copy(),df.iloc[te].copy()
    assert not set(train.body_hash)&set(test.body_hash)
    known=df[df.n_author!=""].reset_index(drop=True)
    ga,gb=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=SEED).split(known,known.label,known.n_author))
    gtrain,gtest=known.iloc[ga].copy(),known.iloc[gb].copy()
    assert not set(gtrain.n_author)&set(gtest.n_author)
    assert not set(gtrain.body_hash)&set(gtest.body_hash)
    old_versions=old["env"] if old else {}
    version_keys={"scikit-learn":"sklearn","numpy":"numpy","pandas":"pandas","scipy":"scipy"}
    unchanged_env=all(versions[k]==old_versions.get(v) for k,v in version_keys.items())
    use_old=same and unchanged_env and not ARGS.smoke
    if use_old:
        assert len(train)==old["data"]["train_n"] and len(test)==old["data"]["test_n"]
        original=pd.read_csv(ARGS.previous/"heldout_predictions.csv")
        assert np.array_equal(original.y_true.to_numpy(),test.label.to_numpy())
    xgb_diagnostic(train)
    primary=run_protocol("random",train,test,use_old=use_old,old=old)
    best=max(primary,key=lambda n:primary[n]["cv_mcc"])
    group=run_protocol("author_disjoint",gtrain,gtest,grouped=True)
    reverse=run_protocol("isot_to_kaggle",iso,df)
    rows=[]
    for name in MODEL_NAMES:
        rows.append(fixed_task("kaggle_to_isot",name,df,iso,primary[name]["best_params"]))
    pd.DataFrame(rows).to_csv(OUT/"table_kaggle_to_isot.csv",index=False)
    rows=[]
    for variant in ["title_only","author_title","title_text","author_title_text"]:
        for setting,a,b,params in [("random",train,test,primary),("author_disjoint",gtrain,gtest,group)]:
            for name in dict.fromkeys(["LinearSVC","LR","MNB","RF",best]):
                if name not in MODEL_NAMES:continue
                row=fixed_task("ablation_"+setting+"_"+variant,name,a,b,params[name]["best_params"],variant)
                row.update(input=variant,setting=setting);rows.append(row)
    pd.DataFrame(rows).to_csv(OUT/"table_ablation.csv",index=False)
    uncertainty_and_tests(best)
    # A deployment model fits all cleaned Kaggle rows only after evaluation.
    final=pipe_for(best,primary[best]["best_params"]).fit(df.title_text,df.label)
    deployment=Pipeline([("normalize",FunctionTransformer(normalize_batch,validate=False)),*final.steps])
    probe=[news_input(r.title,r.text) for r in df.head(10).itertuples()]
    assert np.array_equal(deployment.predict(probe),final.predict(df.head(10).title_text))
    joblib.dump(deployment,OUT/"verifake_pipeline.joblib")
    shutil.copy2(Path(__file__).with_name("verifake_text.py"),OUT/"verifake_text.py")
    json_write(OUT/"deployment_metadata.json",dict(title=TITLE,selected_model=best,label_map={0:"real",1:"fake"},
        input="Raw title + one space + raw body. Normalization is INCLUDED in the Pipeline.",
        score="LinearSVC decision scores are not calibrated probabilities.",
        usage="Keep verifake_text.py importable when loading. Fit uses all clean Kaggle rows; do not use this deployment object to evaluate the old held-out set."))
    # Compare refitted primary predictions with the original, without overwriting either.
    comparison=[]
    if use_old:
        original=pd.read_csv(ARGS.previous/"heldout_predictions.csv")
        for name in MODEL_NAMES:
            fresh=pd.read_csv(OUT/"predictions"/"random"/(name+".csv.gz"))
            comparison.append(dict(model=name,changed_predictions=int((fresh.y_pred.to_numpy()!=original[name].to_numpy()).sum()),
                note="XGB backend retuned on CPU" if name=="XGB" else "same input and selected hyperparameters"))
    json_write(OUT/"old_vs_refit.json",dict(comparable=use_old,rows=comparison))
    figures(best)
    # Final integrity audit covers every saved prediction file including AUC.
    audits=[]
    for path in sorted((OUT/"predictions").rglob("*.csv.gz")):
        d=pd.read_csv(path);assert d.sample_id.is_unique
        audits.append(dict(file=str(path.relative_to(OUT)),**metric(d.y_true,d.y_pred,d.score)))
    pd.DataFrame(audits).to_csv(OUT/"all_prediction_audit.csv",index=False)
    json_write(OUT/"summary.json",dict(title=TITLE,smoke=ARGS.smoke,seed=SEED,selected_model=best,
        selected_by="random training CV MCC",primary_reused_hyperparameters=use_old,
        protocol="Each protocol tunes on its own training data. Known-author evaluation excludes missing authors. Reverse transfer tunes on ISOT only. Forward transfer uses Kaggle training CV parameters.",
        xgb_backend="CPU hist prespecified; GPU tested only in training diagnostic",
        limitations=["Author disjointness is not publisher disjointness.",
          "Exact duplicate control does not exclude all near duplicates or source/style cues.",
          "The public datasets do not provide independent evidence-based fact verification.",
          "One fixed outer split per protocol; bootstrap intervals condition on that split.",
          "Source-dependent label construction can confound cross-dataset performance."],
        tfidf={k:str(v) for k,v in TFIDF.items()},train_n=len(train),test_n=len(test),
        author_train_n=len(gtrain),author_test_n=len(gtest),isot_n=len(iso),
        preprocessing="Lowercase; remove URLs; letters/spaces only; collapse whitespace. No resampling or balancing.",
        ablation="Within each protocol, freeze title+body-selected parameters across all input variants.",
        warning="Synthetic smoke outputs are NOT scientific evidence." if ARGS.smoke else "Review convergence warnings and the XGB diagnostic before final manuscript claims."))
    json_write(OUT/"COMPLETED.json",dict(status="completed",smoke=ARGS.smoke,prediction_files=len(audits)))
    archive=OUT.with_suffix(".zip")
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        for path in sorted(OUT.rglob("*")):
            if path.is_file() and "checkpoints" not in path.parts and path.name!=".run.lock":z.write(path,path.relative_to(OUT))
        # Hyperparameters and CV results are included; bulky per-model checkpoints stay on ARCC.
        for path in (OUT/"checkpoints").rglob("*"):
            if path.suffix in [".json",".csv"]:z.write(path,path.relative_to(OUT))
    print("COMPLETED",archive.resolve(),flush=True)

if __name__=="__main__":
    with threadpool_limits(limits=1):
        try: main()
        except Exception:
            if "OUT" in globals():
                (OUT/"FAILED.txt").write_text(traceback.format_exc())
            raise
