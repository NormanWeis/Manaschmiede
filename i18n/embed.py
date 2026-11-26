import os,re,zlib,base64,sys
p=sys.argv[1]
s=open(p,encoding="utf-8").read()
z=base64.b64encode(zlib.compress(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"en.json"),"rb").read(),9)).decode()
s,n=re.subn(r'\nI18N_Z = "[^"]*"\n','\nI18N_Z = "'+z+'"\n',s)
assert n==1
open(p,"w",encoding="utf-8").write(s)
print("embedded",len(z))
