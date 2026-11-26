import json,glob,re,sys
import os
W=os.path.dirname(os.path.abspath(__file__))+"/"
fx=[l.rstrip("\n").split("\t") for l in open(W+"fixes.tsv",encoding="utf-8")]
def fix(k):
    for a,b in fx:
        a=a.strip("'");b=b.strip("'")
        k=k.replace(a,b)
    return k
def norm(t):return re.sub(r"\s+"," ",t).strip()
TXT={}
for f in sorted(glob.glob(W+"tsv/u*.tsv")):
    for l in open(f,encoding="utf-8"):
        l=l.rstrip("\n")
        if not l:continue
        k,v=l.split("\t");TXT[fix(k)]=v
py=json.load(open(W+"pieces_v0.json"))["py"]
for l in open(W+"tsv/py.tsv",encoding="utf-8"):
    i,v=l.rstrip("\n").split("\t");TXT[fix(py[int(i)])]=v
BL={}
hb=json.load(open(W+"hblocks_v0.json"))
for f in sorted(glob.glob(W+"tsv/hb*.tsv")):
    for l in open(f,encoding="utf-8"):
        i,v=l.rstrip("\n").split("\t");BL[fix(hb[int(i)])]=v
sb=json.load(open(W+"blocks_v0.json"))["blocks"]
for l in open(W+"tsv/sb.tsv",encoding="utf-8"):
    i,v=l.rstrip("\n").split("\t");BL[fix(sb[int(i)])]=v
for f in sorted(glob.glob(W+"tsv/x*.tsv")):  # Nachträge
    for l in open(f,encoding="utf-8"):
        l=l.rstrip("\n")
        if not l:continue
        k,v=l.split("\t")
        (BL if k.startswith("B:") else TXT)[k[2:] if k.startswith("B:") else k]=v
RX=[l.rstrip("\n").split("\t") for l in open(W+"rx.tsv",encoding="utf-8") if l.strip()]
for k,v in BL.items():
    if "<" not in k and "<" not in v and k not in TXT: TXT[k]=v
for k,v in list(TXT.items()):
    m=re.match(r"^[.,;:)]+ ",k)
    if m and len(k)>12:
        k2=k[m.end():];v2=re.sub(r"^[.,;:)]+ ","",v)
        if k2 not in TXT:TXT[k2]=v2
TXT={k:v for k,v in TXT.items() if k!=v}
json.dump({"t":TXT,"b":BL,"r":RX},open(W+"en.json","w"),ensure_ascii=False,separators=(",",":"))
print("TXT",len(TXT),"BL",len(BL),"RX",len(RX))
