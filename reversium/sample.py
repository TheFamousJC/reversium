"""A local sample archive for previewing reports; its code is never executed."""
import io
import zipfile

APP = '''import sqlite3
from storage import list_contacts, add_contact

@app.get('/contacts')
def contacts():
    connection = sqlite3.connect('contacts.db')
    return list_contacts(connection)

@app.post('/contacts')
def create_contact():
    connection = sqlite3.connect('contacts.db')
    add_contact(connection)
    connection.commit()
    return {'created': True}
'''
STORAGE = '''def list_contacts(connection):
    rows = connection.execute('SELECT name, email FROM contacts').fetchall()
    return rows

def add_contact(connection):
    connection.execute('INSERT INTO contacts(name) VALUES (?)', ('sample',))
'''


def sample_archive():
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr('app.py', APP)
        archive.writestr('storage.py', STORAGE)
    output.seek(0)
    return output


JS_APP = '''import express from 'express';
import { Pool } from 'pg';
import { listContacts } from './storage';
const app = express();
const db = new Pool();
app.get('/contacts', async (req: Request, res: Response) => {
  const rows = await listContacts(db);
  res.json({contacts: rows});
});
app.post('/contacts', async (req: Request, res: Response) => {
  await db.query('INSERT INTO contacts(name) VALUES ($1)', [req.body.name]);
  res.status(201).json({created: true});
});
'''
JS_STORAGE = '''export async function listContacts(db: Pool) {
  return await db.query('SELECT name, email FROM contacts');
}
'''


def javascript_sample_archive():
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr('app.ts', JS_APP)
        archive.writestr('storage.ts', JS_STORAGE)
        archive.writestr('package.json', '{"dependencies":{"express":"*","pg":"*"}}')
    output.seek(0)
    return output
