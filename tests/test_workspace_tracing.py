import json
import unittest
from reversium.analyze import inspect_zip
from reversium.report import render
from test_reversium import archive

CLIENT = "import {createClient} from '@supabase/supabase-js'; export const db=createClient(url,key);"


def inspect(files):
    return inspect_zip(archive(list(files.items())))


def labels(report):
    graph = report['workspace_graph']
    nodes = {n['id']: n['label'] for n in graph['nodes']}
    return [(nodes[e['source']], e['label'], nodes[e['target']]) for e in graph['edges']]


class WorkspaceTracingTests(unittest.TestCase):
    def test_nested_router_factory_and_literal_mount(self):
        r = inspect({'server.ts': "import express from 'express'; import {makeRouter} from './router'; async function start(){const app=express();app.use('/api',makeRouter());}",
                     'router.ts': "import {Router} from 'express'; export function makeRouter(){const r=Router(); r.get('/items', (req,res)=>res.json({ok:true}));return r;}"})
        self.assertIn('GET /api/items', [f['name'] for f in r['feature_map']['features']])
        self.assertTrue(any(f['kind'] == 'router_mount_candidate' and f['evidence']['file'] == 'server.ts' for f in r['findings']))

    def test_regex_and_division_do_not_invent_code(self):
        r = inspect({'app.ts': "import express from 'express';const app=express();const p=/app.get('fake')\\/[{}]/g;const n=10 / 2;app.get('/real',(req,res)=>{if(!/^x/.test(req.query.q)) res.json({ok:true});});"})
        self.assertEqual([f['name'] for f in r['workspace_graph']['roots']], ['GET /real'])
        self.assertFalse(any('tracing skipped' in w for w in r['warnings']))

    def test_multiline_imports_react_callbacks_and_supabase(self):
        r = inspect({'db.ts': CLIENT, 'ops.ts': "import {db} from './db'; export async function save(){return db.from('tours').insert({title:'PRIVATE'}).select('id');}",
                     'Panel.tsx': "import React from 'react'; import {\n save\n} from './ops';export const Panel: React.FC<Props> = ({title})=>{const submit=async()=>{await save();};return <form onSubmit={submit}>Don't parse db.from('FAKE') <span>{title}</span></form>;};"})
        feature = next(f for f in r['feature_map']['features'] if f['name'] == 'UI Panel.tsx')
        self.assertIn('adds: Supabase: tours', feature['description'])
        self.assertNotIn('Supabase: FAKE', str(r['workspace_graph']))
        self.assertNotIn('PRIVATE', json.dumps(r['workspace_graph']))
        self.assertTrue(any(e[1] == 'JSX value reference' for e in labels(r)))
        self.assertTrue(any(f['kind'] == 'source_reference' and f['evidence'] == {'file':'ops.ts','line':1} for f in r['findings']))

    def test_jsx_component_reference_and_generic_arrow(self):
        r = inspect({'Child.tsx': 'export function Child(){return <div>hello</div>;}',
                     'App.tsx': "import {Child} from './Child';const update=<T extends string>(x:T)=>{return x;};export function App(){return <><Child /><div>{update('x')}</div></>;}"})
        self.assertTrue(any(e[1:] == ('JSX reference', 'Child.tsx') for e in labels(r)))
        self.assertEqual(r['workspace_graph']['parsed_files'], 2)

    def test_rpc_auth_storage_and_no_payloads(self):
        r = inspect({'db.ts':CLIENT, 'App.tsx': "import {db} from './db';export function App(){const submit=()=>{db.rpc('submit_tour',{private:'SECRET'});db.auth.signInWithPassword({password:'SECRET'});db.storage.from('audio').upload('PRIVATE_PATH',file);};return <button onClick={submit}/>;}"})
        text = json.dumps(r['workspace_graph'])
        self.assertIn('RPC: submit_tour', text)
        self.assertIn('Storage: audio', text)
        self.assertIn('auth signInWithPassword', text)
        self.assertNotIn('SECRET', text)
        self.assertNotIn('PRIVATE_PATH', text)

    def test_unrelated_from_and_shadowed_client_not_supabase(self):
        r = inspect({'db.ts': CLIENT, 'ops.ts': "import {db} from './db';function run(db){db.from('hidden').delete();}function otherRun(){const db=unknown();db.from('also_hidden').delete();}const other=unknown();other.from('fake').delete();"})
        self.assertFalse(any(n['kind']=='data' for n in r['workspace_graph']['nodes']))

    def test_factory_inside_unrelated_object_or_call_is_not_client(self):
        r = inspect({'ops.ts': "import {createClient} from '@supabase/supabase-js';const holder={db:createClient(url,key)};const other=unknown(createClient(url,key));holder.from('fake').delete();other.from('fake').delete();"})
        self.assertFalse(any(n['kind']=='data' for n in r['workspace_graph']['nodes']))

    def test_typed_client_and_factory_return(self):
        r = inspect({'db.ts': "import {createClient as make, SupabaseClient} from '@supabase/supabase-js';export function factory(){return make(url,key);}export function list(client:SupabaseClient){return client.from('tours').select('*');}",
                     'ops.ts': "import {factory} from './db';const admin=enabled?factory():null;function save(){admin.from('tours').upsert({id:1});}"})
        self.assertTrue(any(e[1:] == ('reads', 'Supabase: tours') for e in labels(r)))
        self.assertTrue(any(e[1:] == ('upserts', 'Supabase: tours') for e in labels(r)))

    def test_dynamic_targets_are_unknown(self):
        r = inspect({'db.ts': CLIENT, 'ops.ts': "import {db} from './db';function run(){db.from(table).select('*');db.rpc(name);fetch(target);}"})
        self.assertTrue(any('dynamic Supabase table' in x for x in r['warnings']))
        self.assertTrue(any('dynamic Supabase RPC' in x for x in r['warnings']))
        self.assertFalse(any(n['kind']=='data' for n in r['workspace_graph']['nodes']))

    def test_sql_rpc_to_table_evidence_is_inferred(self):
        r = inspect({'db.ts':CLIENT,'App.tsx':"import {db} from './db';export function App(){db.rpc('submit_tour');return <div/>;}",
                     'migrations/one.sql': "create or replace function public.submit_tour() returns void language plpgsql as $$ begin insert into public.tours(title) values('PRIVATE');end;$$;"})
        self.assertIn(('RPC: submit_tour','SQL adds candidate','Supabase: tours'),labels(r))
        edge = next(e for e in r['workspace_graph']['edges'] if e['label']=='SQL adds candidate')
        self.assertEqual(edge['confidence'],'inferred')
        self.assertEqual(r['findings'][edge['evidence_indices'][0]]['evidence']['file'],'migrations/one.sql')
        self.assertNotIn('PRIVATE',json.dumps(r['workspace_graph']))

    def test_html_and_graph_integrity(self):
        r = inspect({'db.ts':CLIENT,'App.tsx':"import {db} from './db';export function App(){db.from('tours').delete();return <div/>;}"})
        g = r['feature_map']; ids={n['id'] for n in g['nodes']}
        self.assertTrue(all(e['source'] in ids and e['target'] in ids for e in g['edges']))
        self.assertTrue(all(0 <= i < len(r['findings']) for e in g['edges'] for i in e['evidence_indices']))
        html=render(r)
        self.assertIn('function drawMap',html)
        self.assertIn('Select a feature to rebuild',html)
        self.assertIn('not runtime verified',html)

    def test_sql_keywords_and_variables_are_not_tables(self):
        r = inspect({'db.ts':CLIENT,'App.tsx':"import {db} from './db';export function App(){db.rpc('save');return <div/>;}",
                     'one.sql': 'create function public.save() returns void language plpgsql as $$ begin if x is distinct from p_liked then update public.tours set x=1;end if;insert into public.tours(id) values(1) on conflict(id) do update set id=2;end;$$;'})
        names = [n['label'] for n in r['workspace_graph']['nodes'] if n['kind']=='data']
        self.assertEqual(names,['Supabase: tours'])

    def test_structural_map_ids_survive_line_movement(self):
        code="import express from 'express';const app=express();app.get('/items',(req,res)=>{res.json({ok:true});});"
        before=inspect({'app.ts':code})['feature_map']
        after=inspect({'app.ts':'\n\n'+code})['feature_map']
        self.assertEqual([n['id'] for n in before['nodes']],[n['id'] for n in after['nodes']])
        self.assertEqual([e['id'] for e in before['edges']],[e['id'] for e in after['edges']])
