import json
import unittest
from reversium.analyze import inspect_zip
from test_reversium import archive


def inspect(files):
    return inspect_zip(archive(list(files.items())))


def edges(report):
    g = report['workspace_graph']
    nodes = {n['id']: n['label'] for n in g['nodes']}
    return [(nodes[e['source']], e['label'], nodes[e['target']]) for e in g['edges']]


SERVER = "import express from 'express';const app=express();app.get('/api/a',(req,res)=>res.json({ok:true}));app.post('/api/b',(req,res)=>res.json({ok:true}));app.post('/api/chat',(req,res)=>res.json({reply:true}));app.get('/api/media/:id',(req,res)=>res.json({ok:true}));"


class WorkflowTests(unittest.TestCase):
    def test_chat_callback_reaches_parent_api_and_keeps_binding_evidence(self):
        r = inspect({'server.ts':SERVER, 'Child.tsx': 'export function Child({onSend}){const submit=()=>onSend(text);return <button onClick={submit}/>;}',
                     'App.tsx': "import {Child} from './Child';export function App(){const send=async()=>fetch('/api/chat',{method:'POST'});return <Child onSend={send}/>;}"})
        e = edges(r)
        self.assertIn(('Child.prop:onSend','prop binding candidate','App.send'),e)
        self.assertIn(('Child.submit','invokes prop candidate','Child.prop:onSend'),e)
        self.assertIn(('App.send','API target candidate POST','POST /api/chat'),e)
        child = next(f for f in r['feature_map']['features'] if f['name']=='UI Child.tsx')
        self.assertIn('POST /api/chat',child['description'])
        self.assertTrue(any('component instances' in u for u in child['unknowns']))

    def test_forwarded_object_props_and_destructured_alias(self):
        r = inspect({'Child.tsx':'export function Child({onSend:send}){return <button onClick={()=>send()}/>;}',
                     'Middle.tsx':"import {Child} from './Child';export function Middle(props){return <Child onSend={props.send}/>;}",
                     'App.tsx':"import {Middle} from './Middle';export function App(){const submit=()=>{};return <Middle send={submit}/>;}"})
        self.assertIn(('Child.prop:onSend','prop binding candidate','Middle.prop:send'),edges(r))
        self.assertIn(('Middle.prop:send','prop binding candidate','App.submit'),edges(r))

    def test_lazy_named_component_and_hook_return_callback(self):
        r = inspect({'db.ts':"import {createClient} from '@supabase/supabase-js';const db=createClient(url,key);export function save(){return db.from('cities').insert({});}",
                     'hook.ts':"import {useMemo} from 'react';import {save} from './db';export function useContent(){return useMemo(()=>({saveCity:()=>save()}),[]);}",
                     'Panel.tsx':'export function Panel({onSave}){return <button onClick={()=>onSave()}/>;}',
                     'App.tsx':"import {lazy} from 'react';import {useContent} from './hook';const Panel=lazy(()=>import('./Panel').then(module=>({default:module.Panel})));export function App(){const cms=useContent();return <Panel onSave={cms.saveCity}/>;}"})
        self.assertIn(('Panel.prop:onSave','prop binding candidate','useContent.return:saveCity'),edges(r))
        feature = next(f for f in r['feature_map']['features'] if f['name']=='UI Panel.tsx')
        self.assertIn('adds: Supabase: cities',feature['description'])

    def test_component_export_alias_is_resolved(self):
        r=inspect({'Child.tsx':'export function Child({onSend}){onSend();return <div/>;}export const Alias=Child;',
                   'App.tsx':"import {Alias} from './Child';export function App(){const send=()=>{};return <Alias onSend={send}/>;}"})
        self.assertIn(('Child.prop:onSend','prop binding candidate','App.send'),edges(r))

    def test_lazy_default_component(self):
        r=inspect({'Child.tsx':'export default function Child({onSend}){onSend();return <div/>;}',
                   'App.tsx':"import {lazy} from 'react';const Child=lazy(()=>import('./Child'));export function App(){const send=()=>{};return <Child onSend={send}/>;}"})
        self.assertIn(('Child.prop:onSend','prop binding candidate','App.send'),edges(r))

    def test_use_callback_return_shorthand(self):
        r=inspect({'hook.ts':"import {useCallback} from 'react';export function useContent(){const save=useCallback(()=>{},[]);return {save};}",
                   'Child.tsx':'export function Child({onSave}){onSave();return <div/>;}',
                   'App.tsx':"import {useContent} from './hook';import {Child} from './Child';export function App(){const content=useContent();return <Child onSave={content.save}/>;}"})
        self.assertIn(('Child.prop:onSave','prop binding candidate','useContent.save'),edges(r))

    def test_inner_parameter_shadows_component_prop(self):
        r=inspect({'Child.tsx':'export function Child({onSend}){function helper(onSend){onSend();}return <div/>;}'})
        self.assertFalse(any(e[1]=='invokes prop candidate' for e in edges(r)))

    def test_memoized_scalar_is_not_a_callable(self):
        r=inspect({'App.tsx':"import {useMemo} from 'react';export function App(){const value=useMemo(()=>42,[]);value();return <div/>;}"})
        self.assertFalse(any('value' in e[2] and e[1] in ('callback/call candidate','call reference') for e in edges(r)))

    def test_const_concat_template_and_query_values(self):
        r=inspect({'server.ts':SERVER,'api.ts':"const base='/api';const path=base+'/a';function load(){fetch(path+'?secret='+privateValue);}function media(id){fetch(`/api/media/${encodeURIComponent(id)}?token=${secret}`);}"})
        self.assertIn(('load','API target candidate GET','GET /api/a'),edges(r))
        self.assertIn(('media','API target candidate GET','GET /api/media/:id'),edges(r))
        self.assertNotIn('privateValue',json.dumps(r['workspace_graph']))

    def test_call_site_arguments_do_not_cross_connect_wrappers(self):
        r=inspect({'server.ts':SERVER,'api.ts':"async function request(path:string,init?:RequestInit){\nreturn fetch(path,{...init,headers:{}});}\nexport function load(){return request('/api/a');}\nexport function save(){return request('/api/b',{method:'POST'});}"})
        e=edges(r)
        self.assertIn(('load','API target candidate GET','GET /api/a'),e)
        self.assertIn(('save','API target candidate POST','POST /api/b'),e)
        self.assertNotIn(('load','API target candidate POST','POST /api/b'),e)
        edge=next(x for x in r['workspace_graph']['edges'] if x['label']=='API target candidate POST')
        self.assertGreaterEqual(len(edge['evidence_indices']),2)

    def test_request_method_spread_precedence(self):
        r=inspect({'server.ts':SERVER,'api.ts':"const headers={headers:{}};const post={method:'POST'};function save(){fetch('/api/b',{...post,...headers});}function unknown(init){fetch('/api/a',{...init});}"})
        self.assertIn(('save','API target candidate POST','POST /api/b'),edges(r))
        self.assertFalse(any(e[0]=='unknown' and e[1]=='API target candidate GET' for e in edges(r)))

    def test_mutable_env_and_unknown_helpers_do_not_become_targets(self):
        r=inspect({'server.ts':SERVER,'api.ts':"let path='/api/a';path=input;function run(){fetch(path);fetch(process.env.URL || '/api/a');fetch(makePath());}"})
        self.assertFalse(any(e[1].startswith('API target') for e in edges(r)))
        self.assertTrue(any('API target remains unresolved' in g for g in r['workspace_graph']['gaps']))

    def test_shadowed_fetch_and_encoder_are_not_builtin_operations(self):
        r=inspect({'server.ts':SERVER,'api.ts':"function fake(fetch){fetch('/api/a');}function media(id,encodeURIComponent){fetch(`/api/media/${encodeURIComponent(id)}`);}"})
        self.assertFalse(any(e[1].startswith('API target') for e in edges(r)))
        self.assertTrue(any('shadowed fetch' in g for g in r['workspace_graph']['gaps']))

    def test_wrapper_argument_does_not_override_inner_local(self):
        r=inspect({'server.ts':SERVER,'api.ts':"function request(path){queue(()=>{const path=unknown();fetch(path);});}function load(){request('/api/a');}"})
        self.assertFalse(any(e[1]=='API target candidate GET' for e in edges(r)))

    def test_destructured_fetch_shadows_global(self):
        r=inspect({'server.ts':SERVER,'api.ts':"function run({fetch}){fetch('/api/a');}"})
        self.assertFalse(any(e[1]=='API target candidate GET' for e in edges(r)))

    def test_request_output_bound_is_disclosed(self):
        code='function many(){'+"fetch('/api/a');"*405+'}'
        r=inspect({'server.ts':SERVER,'api.ts':code})
        self.assertEqual(r['workspace_graph']['workflow_coverage']['api_targets'],400)
        self.assertTrue(any('400 requests' in g for g in r['workspace_graph']['gaps']))

    def test_non_component_parameters_are_not_props(self):
        r=inspect({'server.ts':SERVER,'other.ts':"function handler(req){req.header('x');req.get('x');}"})
        self.assertFalse(any('.prop:' in n['label'] for n in r['workspace_graph']['nodes']))

    def test_default_prop_and_unresolved_provider_stay_unknown(self):
        r=inspect({'Child.tsx':'export function Child({onSend=unknown}){onSend();return <div/>;}',
                   'App.tsx':"import {Child} from './Child';export function App(){return <Child onSend={provider()}/>;}"})
        self.assertFalse(any(e[1]=='prop binding candidate' for e in edges(r)))
        self.assertTrue(any('JSX callback binding' in g for g in r['workspace_graph']['gaps']))

    def test_callback_inside_unknown_provider_is_not_the_prop_value(self):
        r=inspect({'Child.tsx':'export function Child({onSend}){onSend();return <div/>;}',
                   'App.tsx':"import {Child} from './Child';export function App(){return <Child onSend={provider(()=>secret())}/>;}"})
        self.assertFalse(any(e[1]=='prop binding candidate' for e in edges(r)))

    def test_nested_callback_inside_hook_result_is_not_returned_function(self):
        r=inspect({'hook.ts':'export function useContent(){return {save:unknown(()=>sideEffect())};}',
                   'Child.tsx':'export function Child({onSave}){onSave();return <div/>;}',
                   'App.tsx':"import {useContent} from './hook';import {Child} from './Child';export function App(){const cms=useContent();return <Child onSave={cms.save}/>;}"})
        self.assertFalse(any(e[1]=='prop binding candidate' for e in edges(r)))

    def test_reassigned_global_fetch_is_unknown(self):
        r=inspect({'server.ts':SERVER,'api.ts':"fetch=other;function load(){fetch('/api/a');}"})
        self.assertFalse(any(e[1]=='API target candidate GET' for e in edges(r)))

    def test_multiple_providers_are_candidates_not_instances(self):
        r=inspect({'Child.tsx':'export function Child({onSend}){onSend();return <div/>;}',
                   'App.tsx':"import {Child} from './Child';export function App(){const first=()=>{};const second=()=>{};return <><Child onSend={first}/><Child onSend={second}/></>;}"})
        bindings=[e for e in r['workspace_graph']['edges'] if e['label']=='prop binding candidate']
        self.assertEqual(len(bindings),2)
        self.assertTrue(all(e['confidence']=='inferred' for e in bindings))

    def test_external_targets_omit_credentials_and_queries(self):
        r=inspect({'api.ts':"const base='https://user:PRIVATE@example.test';function load(){fetch(base+'/api?token=SECRET');}"})
        text=json.dumps(r['workspace_graph'])
        self.assertIn('example.test',text)
        self.assertNotIn('PRIVATE',text)
        self.assertNotIn('SECRET',text)

    def test_new_workflow_ids_survive_line_moves(self):
        code="export function Child({onSend}){return <button onClick={()=>onSend()}/>;}"
        a=inspect({'Child.tsx':code})['feature_map']
        b=inspect({'Child.tsx':'\n\n'+code})['feature_map']
        self.assertEqual([n['id'] for n in a['nodes']],[n['id'] for n in b['nodes']])
        self.assertEqual([e['id'] for e in a['edges']],[e['id'] for e in b['edges']])
