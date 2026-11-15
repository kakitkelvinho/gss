import json,sys
sys.path.insert(0,'.')
from sim import Episode
from solution.expert import Expert
ep=Episode(1,1); scans=[]
def call(tool,**a):
    r=ep.call(tool,a)
    if tool=="scan" and "points" in r: scans.append({"args":a,"points":r["points"]})
    return r
Expert(call).run()
res={k:v for k,v in ep.result().items() if isinstance(v,(int,float,str,bool))}
json.dump({"result":res,"scans":scans},open('deck/scans.json','w'))
print(res.get('reward'), [ (s['args'],len(s['points'])) for s in scans])
