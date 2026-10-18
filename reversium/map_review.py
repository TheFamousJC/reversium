"""Bounded structural graph comparison and candidate impact, without a service."""
FUNCTIONS = r"""
function compareFeatureMaps(current,previous){
 if(!current.feature_map||!previous.feature_map)return {status:'unavailable',reason:'One report has no feature map. Missing coverage is not evidence that relationships were removed.'};
 function checked(report){
  const g=report.feature_map;
  for(const [key,limit] of [['nodes',20000],['edges',40000],['features',1000]]){
   if(!Array.isArray(g[key])||g[key].length>limit)throw Error('Invalid or oversized feature map.');
   const seen=new Set();for(const item of g[key]){if(!item||typeof item.id!=='string'||item.id.length>300||seen.has(item.id))throw Error('Invalid or duplicate graph identity.');seen.add(item.id);
    for(const field of ['label','name','description','confidence','source','target','node_id','kind','file'])if(item[field]!==undefined&&(typeof item[field]!=='string'||item[field].length>10000))throw Error('Invalid graph text.');
    for(const field of ['features','unknowns'])if(item[field]!==undefined&&(!Array.isArray(item[field])||item[field].length>1000||item[field].some(x=>typeof x!=='string'||x.length>10000)))throw Error('Invalid graph metadata.');
    if(item.evidence_indices!==undefined&&(!Array.isArray(item.evidence_indices)||item.evidence_indices.length>200000||item.evidence_indices.some(i=>!Number.isInteger(i)||i<0||i>=report.findings.length)))throw Error('Invalid graph evidence reference.');
   }
  }
  const nodes=new Map(g.nodes.map(n=>[n.id,n]));for(const e of g.edges)if(!nodes.has(e.source)||!nodes.has(e.target))throw Error('Graph relationship has a missing endpoint.');
  for(const f of g.features)if(!nodes.has(f.node_id))throw Error('Feature has a missing graph node.');
  return g;
 }
 const before=checked(previous),after=checked(current),diff={};
 const normalized=(item,fields)=>JSON.stringify(fields.map(k=>k==='features'?[...(item[k]||[])].sort():k==='unknowns'?(item[k]||[]).map(t=>t.replace(/Call on line \d+/g,'Call on line #').replace(/(Call at .+:)\d+( was)/g,'$1#$2')):item[k]??null));
 for(const kind of ['nodes','edges','features']){
  const old=new Map(before[kind].map(x=>[x.id,x])),now=new Map(after[kind].map(x=>[x.id,x]));
  const fields=kind==='edges'?['source','target','label','confidence','features','unknowns']:kind==='nodes'?['kind','label','confidence','features','unknowns']:['name','description','unknowns','node_id'];
  diff[kind]={added:[...now.keys()].filter(id=>!old.has(id)),removed:[...old.keys()].filter(id=>!now.has(id)),changed:[...now.keys()].filter(id=>old.has(id)&&normalized(now.get(id),fields)!==normalized(old.get(id),fields))};
 }
 function indexed(g){const adjacency=new Map();for(const e of g.edges){for(const id of [e.source,e.target]){if(!adjacency.has(id))adjacency.set(id,[]);adjacency.get(id).push(e);}}return {g,nodes:new Map(g.nodes.map(n=>[n.id,n])),edges:new Map(g.edges.map(e=>[e.id,e])),features:new Map(g.features.map(f=>[f.id,f])),adjacency};}
 const old=indexed(before),now=indexed(after);
 function impact(edge,index){
  if(!edge)return {features:[],direct:[],limited:false,absent:true};
  const direct=new Set(edge.features||[]),found=new Set(direct),seen=new Set([edge.source,edge.target]),queue=[[edge.source,0],[edge.target,0]];let visits=0,limited=false;
  while(queue.length){const [id,depth]=queue.shift();const node=index.nodes.get(id);for(const f of node?.features||[])found.add(f);for(const f of index.g.features)if(f.node_id===id)found.add(f.id);if(depth===2)continue;
   for(const link of index.adjacency.get(id)||[]){if(++visits>200){limited=true;break;}const next=link.source===id?link.target:link.source;if(!seen.has(next)){if(seen.size>=120){limited=true;break;}seen.add(next);queue.push([next,depth+1]);}}if(limited)break;
  }
  return {direct:[...direct].filter(id=>index.features.has(id)).map(id=>({id,name:index.features.get(id).name||id})),features:[...found].filter(id=>index.features.has(id)).sort().map(id=>({id,name:index.features.get(id).name||id})),limited};
 }
 // Only materialize the bounded displayed relationship review, never an unbounded traversal per edge.
 const changes=['added','removed','changed'].flatMap(type=>diff.edges[type].map(id=>({id,type})));
 const relationships=changes.slice(0,100).map(({id,type})=>{const a=old.edges.get(id),b=now.edges.get(id);return {id,type,before:a,after:b,oldImpact:impact(a,old),newImpact:impact(b,now)};});
 return {status:'compared',diff,relationships,omitted:Math.max(0,changes.length-100),before,after};
}
"""

UI = r"""
function drawMapComparison(current,previous,area){
 const result=compareFeatureMaps(current,previous),h=document.createElement('h2');h.textContent='Feature-map changes';area.append(h);
 const p=document.createElement('p');p.textContent=result.status==='unavailable'?result.reason:'Static relationships only, not confirmed execution or breakage. Stable identities are compared; renamed identities can appear as a removal plus an addition. Evidence line movement alone is ignored. Analyzer and coverage changes can alter the map without a software change. Candidate effects use recorded feature membership and a bounded neighborhood in each report: two hops, 120 nodes and 200 edge visits per relationship side. Baseline references belong to the earlier report.';area.append(p);if(result.status!=='compared')return;
 for(const kind of ['features','nodes','edges']){const heading=document.createElement('h3'),d=result.diff[kind];heading.textContent=kind+': '+d.added.length+' added, '+d.removed.length+' removed, '+d.changed.length+' changed';area.append(heading);if(kind==='edges')continue;const old=new Map(result.before[kind].map(x=>[x.id,x])),now=new Map(result.after[kind].map(x=>[x.id,x]));let count=0;for(const type of ['added','removed','changed'])for(const id of d[type]){if(count++>=100)continue;const item=type==='removed'?old.get(id):now.get(id),line=document.createElement('p');line.textContent=type+': '+(item.name||item.label||id);area.append(line);}if(count>100){const note=document.createElement('p');note.textContent=(count-100)+' further '+kind+' omitted from this view.';area.append(note);}}
 const beforeNodes=new Map(result.before.nodes.map(n=>[n.id,n])),afterNodes=new Map(result.after.nodes.map(n=>[n.id,n]));
 function evidence(edge,report,target,isCurrent){if(!edge)return;const indices=edge.evidence_indices||[];for(const i of indices.slice(0,4)){const f=report.findings[i],label=(isCurrent?'Current: ':'Earlier: ')+f.evidence.file+':'+(f.evidence.line||1);const el=document.createElement(isCurrent?'a':'span');el.textContent=label+' ';if(isCurrent){el.href='#finding-'+i;el.onclick=e=>{e.preventDefault();revealFinding(el.getAttribute('href'));};}target.append(el);}if(indices.length>4)target.append(document.createTextNode((indices.length-4)+' further evidence references omitted. '));if(!indices.length)target.append(document.createTextNode('No direct relationship evidence recorded. '));}
 for(const change of result.relationships){const card=document.createElement('article');card.className='relationship-change';const title=document.createElement('h3');title.textContent=change.type+' relationship';card.append(title);
  for(const [label,edge,nodes,report,isCurrent] of [['Earlier',change.before,beforeNodes,previous,false],['Current',change.after,afterNodes,current,true]]){const line=document.createElement('p');line.textContent=label+': '+(edge?(nodes.get(edge.source)?.label||edge.source)+' → '+edge.label+' → '+(nodes.get(edge.target)?.label||edge.target)+' ('+(edge.confidence||'unspecified confidence')+')':'No relationship with this identity recorded.');card.append(line);evidence(edge,report,card,isCurrent);}
  const edge=change.after||change.before,nodes=change.after?afterNodes:beforeNodes,svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 800 100');svg.setAttribute('role','img');svg.setAttribute('aria-label','Relationship: '+(nodes.get(edge.source)?.label||edge.source)+' to '+(nodes.get(edge.target)?.label||edge.target));svg.style.width='100%';svg.style.maxWidth='800px';const color={added:'#247344',removed:'#a73939',changed:'#916000'}[change.type];
  for(const [x,id] of [[5,edge.source],[490,edge.target]]){const box=document.createElementNS(svg.namespaceURI,'rect');for(const [k,v]of Object.entries({x,y:15,width:300,height:65,rx:10,fill:'#eef2ff',stroke:color}))box.setAttribute(k,v);svg.append(box);const t=document.createElementNS(svg.namespaceURI,'text');t.setAttribute('x',x+10);t.setAttribute('y',52);t.setAttribute('fill','#17253c');t.textContent=(nodes.get(id)?.label||id).slice(0,34);svg.append(t);}const t=document.createElementNS(svg.namespaceURI,'text');t.setAttribute('x','325');t.setAttribute('y','52');t.setAttribute('fill',color);t.textContent='────→';svg.append(t);card.append(svg);
  for(const [label,data]of [['Earlier candidates',change.oldImpact],['Current candidates',change.newImpact]]){const direct=document.createElement('p');direct.textContent=label+' — directly recorded feature membership: '+(data.absent?'Relationship absent on this side.':data.direct.length?data.direct.slice(0,20).map(f=>f.name).join('; ')+(data.direct.length>20?' · '+(data.direct.length-20)+' further names omitted.':''):'None recorded; coverage is incomplete.');card.append(direct);if(data.absent)continue;const details=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Broader neighborhood: '+data.features.length+' candidate features'+(data.limited?' · traversal limited':'')+' (may include unrelated features)';details.append(summary);const line=document.createElement('p');line.textContent='Broader neighborhood (may include unrelated features through shared nodes): '+data.features.length+' found'+(data.limited?' (traversal limit reached; more may be missing)':'')+'. '+data.features.slice(0,20).map(f=>f.name).join('; ')+(data.features.length>20?' · '+(data.features.length-20)+' further names omitted.':'')+(data.features.length===0?' No feature candidate found within these bounds; this does not prove no effect.':'');details.append(line);card.append(details);}
  const next=document.createElement('p');next.textContent='Next check: inspect both source locations and test the relevant workflow in an isolated environment. Candidate association does not establish that a feature changed or failed.';card.append(next);area.append(card);
 }
 if(!result.relationships.length){const note=document.createElement('p');note.textContent='No relationship changes found in the recorded maps. Missing or dynamic behavior remains unknown.';area.append(note);}if(result.omitted){const note=document.createElement('p');note.textContent=result.omitted+' further relationship changes omitted; only the first 100 are reviewed here.';area.append(note);}
}
"""
