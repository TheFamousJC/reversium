"""Plain-language, evidence-linked interpretation using local rules only."""
from .platform import STACK, SERVICES

MAX_EXPLANATIONS = 16


def explain_software(report):
    findings = report['findings']
    profile = report.get('platform', {})
    explanations = []
    seen = set()
    group_count = 0
    by_location = {}
    for index, item in enumerate(findings):
        by_location.setdefault(tuple(sorted(item['evidence'].items())), []).append(index)

    def add(topic, text, unknown, indices):
        nonlocal group_count
        indices = sorted(set(indices))
        key = (topic, text)
        if not indices or key in seen:
            return
        seen.add(key)
        group_count += 1
        if len(explanations) < MAX_EXPLANATIONS:
            explanations.append({'topic': topic, 'explanation': text, 'assessment': 'Suggested by files; not verified by running',
                                 'unknown': unknown, 'evidence_indices': indices})

    def references(evidence, predicate):
        return [index for index in by_location.get(tuple(sorted(evidence.items())), []) if predicate(findings[index])]

    def component_key(item):
        return item['value'].lower().replace('_', '-').split('.')[0]

    traced_routes = set()
    mapped = report.get('feature_map', {}).get('features', [])
    for group in ('react', 'route'):
        count = 0
        for feature in mapped:
            if feature.get('type') != group or feature['description'].startswith('Source references mapped;'):
                continue
            add('Mapped source connections', feature['name'] + ' has source references to: ' + feature['description'],
                ' '.join(feature['unknowns']), feature['evidence_indices'])
            count += 1
            if count >= 7:
                break
    for trace in report.get('route_traces', []):
        if not trace['operations']:
            continue
        traced_routes.add(trace['route'])
        descriptions = list(dict.fromkeys(item['description'] for item in trace['operations']))
        add('Feature traced through code', f'The handler “{trace["handler"]}” for {trace["method"]} {trace["route"]} contains code that: ' + ' '.join(descriptions[:8]),
            ' '.join(trace['unknowns']) + (' Additional operations are available in Evidence.' if len(descriptions) > 8 else ''), trace['evidence_indices'])

    for index, item in enumerate(findings):
        kind, value = item['kind'], item['value']
        if kind == 'route_candidate':
            if value in traced_routes:
                continue
            add('Possible web entry point', f'The code contains a possible web entry point named “{value}”. Other software or a browser may be able to send requests to it.',
                'The name does not establish what it returns, who can access it, whether it is enabled, or what business task it performs.', [index])
        elif kind == 'model_candidate':
            add('Possible stored information', f'The code defines a possible data-record type named “{value}”. This may describe information the application organizes.',
                'Storage, fields, validation rules and actual database use have not been confirmed.', [index])
        elif kind == 'endpoint_host_candidate':
            add('Possible outside connection', f'The source mentions the web host “{value}”. This could point to an outside integration or a reference in text.',
                'A mention does not prove a connection is made or establish what data is sent.', [index])

    for stack in profile.get('stack_candidates', []):
        add('Application building blocks', f'A reference to {stack["name"]} suggests part of the software uses that framework.',
            'A framework reference does not establish the finished product, its screens or its business features. It could be optional or unused.',
            references(stack['evidence'], lambda item: item['kind'] in ('import', 'dependency') and STACK.get(component_key(item)) == stack['name']))
    for service in profile.get('supporting_services', []):
        role = service['role']
        purpose = {'database': 'keep organized records', 'cache / data store': 'keep data for quick access',
                   'message broker': 'pass tasks or messages between components', 'payments integration': 'communicate with a payment service'}.get(role)
        text = (f'A reference to {service["name"]} suggests the software may {purpose}.' if purpose else
                f'The package references {service["name"]} as a supporting component ({role}).')
        add('Possible supporting service', text,
            'This reference may be optional, unused or development-only. Required settings, versions and actual behavior are unknown.',
            references(service['evidence'], lambda item: (item['kind'] in ('import', 'dependency') and SERVICES.get(component_key(item), (None,))[0] == service['name']) or
                       (item['kind'] == 'container_image_candidate' and item['value'].split('/')[-1].split(':')[0].lower() == service['name'])))
    for index, item in enumerate(findings):
        if item['kind'] == 'binary_format':
            add('Compiled component', f'A file has signs of the {item["value"]} format. This helps identify how it is packaged, rather than what it does.',
                'File format and library names do not explain the component’s business purpose. This component was not executed or decompiled.', [index])

    unknowns = ['The complete business purpose, user workflows and feature set.',
                'What each entry point actually does, including outputs, side effects and permission checks.',
                'Behavior controlled by configuration, missing services, plugins or dynamically loaded code.',
                'Whether the software runs correctly, handles real data safely or is stable.']
    if any(file.get('analysis') in ('inventory_only', 'parse_failed') for file in report['files']):
        unknowns.append('Some files received inventory only or could not be parsed; their behavior is not explained.')
    if any(file.get('binary') for file in report['files']):
        unknowns.append('Compiled code was inspected only for supported metadata; hidden or obfuscated logic remains unknown.')
    if report.get('warnings'):
        unknowns.append('Inspection warnings or limits may leave gaps. Review the Coverage tab for details.')
    return {'method': 'Local rules based on static findings; no AI service and no program execution.',
            'summary': 'These are clues about possible behavior, not an exact description of everything the software does.' if explanations else
                       'There is not enough supported evidence to explain what this software does.',
            'explanations': explanations, 'omitted_groups': max(0, group_count - len(explanations)),
            'unknowns': unknowns,
            'next_steps': ['Trace the referenced code to confirm its inputs, outputs and side effects.',
                           'Ask the software owner which workflows and services are intended.',
                           'Use isolated runtime tests to check representative scenarios; those tests are not performed by Reversium.']}
