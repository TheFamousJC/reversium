"""Evidence-linked platform and supporting-service candidates, never deployment claims."""
import re
from pathlib import PurePosixPath


CONFIG_NAMES = {'Dockerfile', 'compose.yml', 'compose.yaml', 'docker-compose.yml', 'docker-compose.yaml'}
STACK = {'flask': 'Flask web application', 'django': 'Django web application', 'fastapi': 'FastAPI web API',
         'express': 'Express web application', 'react': 'React user interface', 'next': 'Next.js web application',
         'vue': 'Vue user interface', 'electron': 'Electron desktop application'}
SERVICES = {'psycopg': ('PostgreSQL', 'database'), 'psycopg2': ('PostgreSQL', 'database'),
            'psycopg2-binary': ('PostgreSQL', 'database'), 'psycopg-binary': ('PostgreSQL', 'database'),
            'pg': ('PostgreSQL', 'database'), 'mysql': ('MySQL', 'database'), 'mysql2': ('MySQL', 'database'),
            'pymysql': ('MySQL', 'database'), 'redis': ('Redis', 'cache / data store'),
            'ioredis': ('Redis', 'cache / data store'), 'pymongo': ('MongoDB', 'database'),
            'mongoose': ('MongoDB', 'database'), 'pika': ('RabbitMQ-compatible broker', 'message broker'),
            'amqplib': ('AMQP-compatible broker', 'message broker'),
            'stripe': ('Stripe API', 'payments integration'), 'boto3': ('AWS services', 'cloud SDK; specific services unknown'),
            'firebase-admin': ('Firebase services', 'backend integration; exact services unknown')}


def config_details(source, name, finding):
    """Record image identifiers only; never execute build instructions or scripts."""
    docker = PurePosixPath(name).name == 'Dockerfile'
    for number, line in enumerate(source.splitlines(), 1):
        pattern = r'^\s*FROM\s+(?:--platform=\S+\s+)?([\w./:@${}-]+)' if docker else r'^\s*image:\s*[\'\"]?([\w./:@${}-]+)'
        match = re.match(pattern, line, flags=re.I if docker else 0)
        if match:
            finding('container_image_candidate', match.group(1), name, number, 'heuristic')


def platform_profile(report):
    stack, services, targets, runtimes = [], [], [], []
    for finding in report['findings']:
        value, kind = finding['value'], finding['kind']
        evidence = finding['evidence']
        key = value.lower().replace('_', '-').split('.')[0]
        if kind in ('dependency', 'import'):
            if key in STACK:
                stack.append({'name': STACK[key], 'confidence': 'candidate', 'evidence': evidence})
            if key in SERVICES:
                name, role = SERVICES[key]
                services.append({'name': name, 'role': role, 'status': 'client reference; requirement unconfirmed', 'evidence': evidence})
        if kind == 'container_image_candidate':
            key = value.split('/')[-1].split(':')[0].lower()
            if key in {'postgres', 'redis', 'mysql', 'mariadb', 'mongo', 'rabbitmq', 'nginx'}:
                services.append({'name': key, 'role': 'declared container image', 'status': 'configuration candidate; not validated', 'evidence': evidence})
    for file in report['files']:
        runtime = {'.py': 'Python', '.js': 'JavaScript runtime (browser or server unknown)', '.ts': 'TypeScript build toolchain', '.java': 'Java toolchain', '.cs': '.NET toolchain'}.get(PurePosixPath(file['path']).suffix.lower())
        if runtime and file['category'] == 'source':
            runtimes.append({'name': runtime, 'confidence': 'source-language candidate; version unknown', 'evidence': {'file': file['path'], 'line': 1}})
        binary = file.get('binary')
        if binary:
            targets.append({'file': file['path'], 'format': binary['format'], 'target': binary.get('target', binary.get('runtime', 'Unknown')),
                            'architecture': binary.get('architecture', 'Unknown'), 'status': binary['status'],
                            'evidence': {'file': file['path'], 'offset': 0}})
    # Preserve one entry per supporting location, rather than implying independent confirmation.
    def unique(entries):
        seen, output = set(), []
        for entry in entries:
            key = (entry.get('name'), str(entry['evidence']))
            if key not in seen:
                output.append(entry)
                seen.add(key)
        return output
    return {'stack_candidates': unique(stack), 'runtime_candidates': unique(runtimes), 'supporting_services': unique(services), 'binary_targets': targets,
            'purpose': 'Web-facing software candidate' if any(f['kind'] == 'route_candidate' for f in report['findings']) else 'Business purpose not determined from supported evidence',
            'readiness': 'Not verified: this report does not install dependencies, build, start or health-check the software.',
            'unknowns': ['Actual business purpose and completeness of the archive', 'Required runtime/service versions, credentials and external access',
                         'Database schema/migrations and initial data', 'Resource sizing, supported OS and deployment configuration',
                         'Backups, monitoring, updates, recovery and load/stability testing'],
            'next_steps': ['Review the referenced files and confirm intended features.', 'Confirm which referenced services are required versus optional or development-only.',
                           'Prepare an isolated disposable VM, dependency versions and non-production configuration before any future execution.',
                           'Validate installation, migrations, health checks and recovery before calling a deployment stable.']}
