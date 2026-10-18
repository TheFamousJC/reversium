"""Portable, log-free result from the reviewed offline guest profile."""
from datetime import datetime, timezone
from . import __version__

ISOLATION_KEYS=('expected_alpine','loopback_only','no_routes','host_http_unreachable','no_host_filesystems','probe_media_mounted','probe_readable','input_write_rejected','no_windows_mount','input_media_unchanged','host_canary_unchanged','no_host_connection','fresh_guest_no_marker','hard_timeout_stops_process')
APPLICATION_KEYS=('loopback_only','input_mounted','signed_runtime_installed','node_available','libraries_unpacked_without_hooks','frontend_build','backend_compile','guest_local_home_responded','still_no_external_route','input_media_unchanged','guest_process_stopped')


def utc_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def portable_result(result,isolation,run_id,started_at):
    """Select fixed fields only. No raw logs, source, paths, commands or key values."""
    checks={key:result.get('checks',{}).get(key) for key in APPLICATION_KEYS}
    for key in ('input_media_unchanged','guest_process_stopped'):checks[key]=result.get(key)
    return {'format':'reversium-sandbox-result','version':1,'profile':'tudela-offline-build-start-v1',
            'tool_version':__version__,'run_id':run_id,'started_at':started_at,'finished_at':utc_now(),
            'archive_sha256':result['delivery']['source_archive_sha256'],
            'tested_input_sha256':result['delivery']['sanitized_archive_sha256'],
            'omitted_member_count':len(result['delivery']['omitted_sensitive_or_generated_members']),
            'accelerator':result['accelerator'],'runtime_versions':result.get('runtime_versions',[]),
            'isolation_checks':{key:isolation.get('checks',{}).get(key) for key in ISOLATION_KEYS},'checks':checks}
