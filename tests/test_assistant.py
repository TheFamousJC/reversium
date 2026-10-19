import io
import json
import time
import unittest
from unittest.mock import patch
from reversium.assistant import Assistant, validate_packet, validate_answer, validate_identity


class AssistantTests(unittest.TestCase):
    def test_http_session_and_origin_gates(self):
        import http.client
        import threading
        from reversium.__main__ import Handler, LocalHTTPServer
        server = LocalHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            origin = 'http://127.0.0.1:' + str(server.server_port)
            for sent_origin, capability, expected in ((origin, '', 403), ('https://evil.test', server.assistant_session, 403), (origin, server.assistant_session, 200)):
                conn = http.client.HTTPConnection('127.0.0.1', server.server_port)
                conn.request('POST', '/assistant/status', '{}', {'Origin': sent_origin, 'X-Reversium-Session': capability})
                response = conn.getresponse()
                self.assertEqual(response.status, expected)
                response.read()
                conn.close()
            from urllib.error import HTTPError
            error = HTTPError('https://api.openai.com/v1/responses', 400, 'Bad request', {},
                              io.BytesIO(b'{"error":{"code":"unsupported_parameter","param":"max_output_tokens","message":"private request text"}}'))
            with patch.object(server.assistant, 'ask', side_effect=error):
                conn = http.client.HTTPConnection('127.0.0.1', server.server_port)
                conn.request('POST', '/assistant/ask', '{}', {'Origin': origin, 'X-Reversium-Session': server.assistant_session})
                response = conn.getresponse()
                text = response.read().decode()
                self.assertEqual(response.status, 502)
                self.assertIn('unsupported_parameter', text)
                self.assertNotIn('private request text', text)
                conn.close()
        finally:
            server.shutdown()
            server.server_close()

    def packet(self):
        return {'question': 'Explain this', 'evidence': [{'id': 3, 'text': 'handler calls database'}]}

    def test_only_selected_evidence_allowed(self):
        self.assertEqual(validate_packet(self.packet()), {3})
        for changes in ({'archive': 'secret'}, {'question': ''}, {'evidence': []}, {'evidence': [{'id': True, 'text': 'x'}]}):
            packet = self.packet() | changes
            with self.assertRaises(ValueError):
                validate_packet(packet)

    def test_citations_required_and_bounded(self):
        good = {'claims': [{'text': 'Candidate operation', 'evidence_ids': [3]}], 'unknowns': ['Runtime success']}
        self.assertEqual(validate_answer(json.dumps(good), {3}), good)
        for refs in ([], [4], [True], ['3']):
            good['claims'][0]['evidence_ids'] = refs
            with self.assertRaises(ValueError):
                validate_answer(json.dumps(good), {3})

    def test_offline_defaults_and_consent(self):
        a = Assistant()
        self.assertFalse(a.status()['connected'])
        with patch('reversium.assistant.request') as network:
            with self.assertRaises(ValueError):
                a.ask({'packet': self.packet(), 'consent': False})
            network.assert_not_called()

    def test_callback_rejects_expired_replayed_and_wrong_state(self):
        for expires, state in ((time.time() - 1, 'correct'), (time.time() + 60, 'wrong')):
            a = Assistant()
            a.pending = {'state': 'correct', 'expires': expires}
            with patch('reversium.assistant.read_json') as network:
                with self.assertRaises(ValueError):
                    a.callback({'state': [state]})
                with self.assertRaises(ValueError):
                    a.callback({'state': ['correct']})
                network.assert_not_called()

    def test_complete_stream_only_and_no_tools(self):
        a = Assistant()
        a.account = {'token': 'test', 'label': 'test', 'expires': time.time() + 60}
        a.models = [{'id': 'allowed', 'name': 'Allowed'}]
        answer = json.dumps({'claims': [{'text': 'Candidate', 'evidence_ids': [3]}], 'unknowns': ['Execution']})
        events = [{'type': 'response.output_text.delta', 'delta': answer}, {'type': 'response.completed'}]
        stream = b''.join(b'data: ' + json.dumps(e).encode() + b'\n\n' for e in events)
        with patch('reversium.assistant.request', return_value=io.BytesIO(stream)) as network:
            result = a.ask({'packet': self.packet(), 'consent': True, 'model': 'allowed'})
            self.assertEqual(result['claims'][0]['evidence_ids'], [3])
            payload = network.call_args.kwargs['data']
            self.assertFalse(payload['store'])
            self.assertTrue(payload['stream'])
            self.assertNotIn('tools', payload)
        for ending in ('response.failed', 'response.incomplete', 'error', 'unknown'):
            event = b'data: ' + json.dumps({'type': ending}).encode() + b'\n'
            with patch('reversium.assistant.request', return_value=io.BytesIO(event)):
                with self.assertRaises(ValueError):
                    a.ask({'packet': self.packet(), 'consent': True, 'model': 'allowed'})
        a.disconnect()
        self.assertIsNone(a.account)

    def test_real_signature_claim_validation(self):
        try:
            import jwt
            from cryptography.hazmat.primitives.asymmetric import rsa
        except ImportError:
            self.skipTest('Optional AI dependencies not installed')
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key())) | {'kid': 'test'}
        claims = {'iss': 'https://auth.openai.com', 'sub': 'user', 'aud': 'oaiapp_test',
                  'iat': int(time.time()), 'exp': int(time.time()) + 60, 'nonce': 'nonce'}
        def signed(c):
            return jwt.encode(c, key, algorithm='RS256', headers={'kid': 'test'})
        self.assertEqual(validate_identity(signed(claims), 'oaiapp_test', 'nonce', {'keys': [jwk]})['sub'], 'user')
        for change in ({'nonce': 'other'}, {'aud': 'other'}, {'iss': 'https://evil.test'}, {'exp': 1}):
            with self.assertRaises(Exception):
                validate_identity(signed(claims | change), 'oaiapp_test', 'nonce', {'keys': [jwk]})
