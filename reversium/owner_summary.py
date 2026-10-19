"""A bounded owner-facing overview of existing evidence, not runtime claims."""
import html


def owner_summary(report):
    esc = lambda value: html.escape(str(value), quote=True)
    findings = report['findings']
    def evidence(indices):
        links = []
        for i in list(dict.fromkeys(indices))[:3]:
            f = findings[i]
            loc = f['evidence']
            label = loc['file'] + (':' + str(loc['line']) if 'line' in loc else '')
            links.append(f'<a class="evidence-link" href="#finding-{i}">{esc(label)}</a>')
        return '<details><summary>Why we say this</summary>' + ' · '.join(links) + '</details>'
    facts = []
    for names, title, text in [
        (('react',), 'It may include an interactive website.', 'React is referenced in this package. This suggests browser screens, but does not prove which screens are complete or working.'),
        (('express',), 'It may include a server behind the website.', 'Express is referenced. A developer should check which requests the server handles and what configuration it needs.'),
        (('@supabase/supabase-js', 'pg', 'mysql2'), 'Some features refer to stored records or account services.', 'Database or Supabase libraries are referenced. The required data, permissions and service configuration still need confirmation.')]:
        ids = [i for i, f in enumerate(findings) if f['kind'] in ('dependency', 'import') and f['value'] in names]
        if ids:
            facts.append('<article class="explanation"><h3>' + title + '</h3><p>' + text + '</p>' + evidence(ids) + '</article>')
    if not facts:
        facts.append('<p>This package has been inventoried, but the supported readers did not establish a simple application profile. Ask a developer to inspect its file inventory and coverage before inferring what it does.</p>')
    return ('<h3>What can you take from this result?</h3>' + ''.join(facts)
            + '<div class="owner-caution"><h3>Can I run it or accept the handover now?</h3><p>That has not been established. Reversium read files; it did not install the software, test a user journey or check live services. Use these findings as a starting point for the checks below.</p></div>')


NEXT_STEPS = '''<h3>Your next three actions</h3><ol class="action-plan">
<li><b>You: choose one feature that matters.</b><p>Write down what a user should be able to do, such as save an item and see it listed. Avoid trying to verify the entire platform at once.</p><p><b>Done when:</b> you and the developer agree on the action and its expected result.</p></li>
<li><b>Developer: explain the setup and prove that feature locally.</b><p>Use the evidence to locate the code. List the required services, configuration and sample data, then test in a separate disposable environment.</p><p><b>Done when:</b> another person can follow the setup notes and see the agreed feature succeed, with dated test results.</p></li>
<li><b>You and the developer: record what is still missing.</b><p>Save the report and agree who owns each unanswered question, access requirement and failed test.</p><p><b>Done when:</b> you have a handover checklist with owners and evidence, not just a claim that the software works.</p></li></ol>'''
