// Provider-neutral account-session controller. No provider URLs, credentials or network calls.
export function validatePacket(value){
 if(!value||Object.keys(value).sort().join(',')!=='evidence,question'||typeof value.question!=='string'||!value.question.trim()||value.question.length>4000||!Array.isArray(value.evidence)||value.evidence.length<1||value.evidence.length>20)throw Error('Review a question and 1–20 findings.');
 const ids=new Set();for(const e of value.evidence){if(!e||Object.keys(e).sort().join(',')!=='id,text'||!Number.isSafeInteger(e.id)||e.id<0||ids.has(e.id)||typeof e.text!=='string'||!e.text.trim()||e.text.length>4000)throw Error('Invalid selected evidence.');ids.add(e.id)}
 if(JSON.stringify(value).length>64000)throw Error('Selected evidence exceeds the request limit.');
 return JSON.parse(JSON.stringify(value));
}
export function validateAnswer(value,packet){
 if(!value||Object.keys(value).sort().join(',')!=='claims,unknowns'||!Array.isArray(value.claims)||value.claims.length>30||!Array.isArray(value.unknowns)||value.unknowns.length>30)throw Error('The reply format could not be verified.');
 const ids=new Set(packet.evidence.map(e=>e.id));
 for(const c of value.claims){if(!c||Object.keys(c).sort().join(',')!=='evidence_ids,text'||typeof c.text!=='string'||!c.text.trim()||c.text.length>5000||!Array.isArray(c.evidence_ids)||!c.evidence_ids.length||!c.evidence_ids.every(i=>Number.isSafeInteger(i)&&ids.has(i)))throw Error('The reply cites evidence outside your approved selection.');}
 if(!value.unknowns.every(s=>typeof s==='string'&&s.length<=5000))throw Error('Invalid unknowns in reply.');
 return JSON.parse(JSON.stringify(value));
}
export function createOnlineAI({enabled=false,adapter=null}={}){
 let state=enabled&&adapter?'disconnected':'awaiting_approval',generation=0,active=null,answer=null;
 const snapshot=()=>({state,answer});
 function clear(){generation++;active?.abort();active=null;answer=null;}
 return {snapshot,
 async connect(){if(!enabled||!adapter)return snapshot();clear();const turn=generation;state='connecting';active=new AbortController();try{const result=await adapter.connect({signal:active.signal});if(turn!==generation)return snapshot();if(result?.connected!==true)throw Error();state='connected';}catch{if(turn===generation)state='disconnected';}return snapshot();},
 async ask(value,approved){if(!enabled||!adapter)throw Error('ChatGPT account access is awaiting approval.');if(state!=='connected')throw Error('Connect your account before sending.');if(approved!==true)throw Error('Review and approve the exact request first.');const packet=validatePacket(value);clear();const turn=generation;active=new AbortController();state='sending';try{const result=await adapter.ask(JSON.parse(JSON.stringify(packet)),{signal:active.signal});if(turn!==generation)return snapshot();answer=validateAnswer(result,packet);state='connected';}catch(error){if(turn===generation){answer=null;state=error?.code==='SESSION_EXPIRED'?'disconnected':'connected';throw Error(error?.code==='SESSION_EXPIRED'?'Your session expired. Connect again.':'No verified answer was returned. Review the evidence or retry explicitly.');}}finally{if(turn===generation)active=null;}return snapshot();},
 async disconnect(){clear();state=enabled&&adapter?'disconnected':'awaiting_approval';try{await adapter?.disconnect();}catch{}return snapshot();},
 cancel(){clear();if(state==='sending')state='connected';return snapshot();}
 };
}
