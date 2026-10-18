import unittest,threading,urllib.request,urllib.error,json,base64,gzip
from reversium.cms_preview import Preview,valid_target,CSP
class PreviewTests(unittest.TestCase):
 def test_targets_cannot_select_external_upstreams(self):
  for path in ('http://evil.test/','//evil.test/','/\\evil.test','/x\r\ny'):
   self.assertFalse(valid_target(path))
  self.assertTrue(valid_target('/rest/v1/tours?select=id'))
  self.assertIn("connect-src 'self'",CSP)
 def test_relay_refuses_untrusted_host_origin_and_oversize(self):
  p=Preview();threading.Thread(target=p.server.serve_forever,daemon=True).start()
  calls=[]
  class Guest:
   def command(self,command,seconds):
    calls.append(command);return 0,'guest:/work# REVERSIUM_HTTP:'+json.dumps({'status':200,'headers':{'content-type':'text/plain'},'body':base64.b64encode(gzip.compress(b'guest response')).decode()})
  p.guest=Guest()
  def request(headers=None,data=None):
   try:
    with urllib.request.urlopen(urllib.request.Request(p.origin+'/rest/v1/tours',data=data,headers=headers or {}),timeout=3) as r:return r.status,r.read()
   except urllib.error.HTTPError as e:return e.code,e.read()
   except ConnectionResetError:return 0,b''
  try:
   self.assertEqual(request()[0],403)
   cookie={'Cookie':'reversium_preview='+p.token}
   self.assertEqual(request({**cookie,'Host':'evil.test'})[0],403)
   self.assertEqual(request({**cookie,'Origin':'https://evil.test'},b'')[0],403)
   self.assertEqual(request(cookie,b'')[0],403)
   self.assertIn(request({**cookie,'Origin':p.origin,'Content-Length':'2097153'},b'x')[0],(0,413))
   self.assertEqual(len(calls),0)
   self.assertEqual(request(cookie),(200,b'guest response'))
   packet=json.loads(base64.b64decode(calls[0].split()[-1]));self.assertNotIn('cookie',packet['headers']);self.assertEqual(packet['path'],'/rest/v1/tours')
   self.assertEqual(request(cookie),(200,b'guest response'))
   repeat=json.loads(base64.b64decode(calls[1].split()[-1]));self.assertNotIn('headers',repeat);self.assertEqual(repeat['headers_key'],packet['headers_key'])
  finally:p.server.shutdown();p.close()
 def test_stop_form_requires_independent_csrf_token_and_entry_cookie(self):
  p=Preview();threading.Thread(target=p.server.serve_forever,daemon=True).start()
  def stop(cookie,token,origin='null'):
   headers={'Cookie':cookie,'Origin':origin,'Content-Type':'application/x-www-form-urlencoded'}
   req=urllib.request.Request(p.origin+'/__reversium_finish',data=('confirm='+token).encode(),headers=headers)
   try:
    with urllib.request.urlopen(req,timeout=3) as r:return r.status
   except urllib.error.HTTPError as e:return e.code
   except ConnectionResetError:return 0
  try:
   cookie='reversium_preview='+p.token
   self.assertIn(stop('',p.stop_token),(0,403));self.assertFalse(p.done.is_set())
   self.assertEqual(stop(cookie,'wrong'),403);self.assertFalse(p.done.is_set())
   self.assertEqual(stop(cookie,p.stop_token),200);self.assertTrue(p.done.is_set())
  finally:p.server.shutdown();p.close()
if __name__=='__main__':unittest.main()
