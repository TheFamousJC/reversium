"""Portable, log-free result from the reviewed offline guest profile."""
from datetime import datetime, timezone
from . import __version__

ISOLATION_KEYS=('expected_alpine','loopback_only','no_routes','host_http_unreachable','no_host_filesystems','probe_media_mounted','probe_readable','input_write_rejected','no_windows_mount','input_media_unchanged','host_canary_unchanged','no_host_connection','fresh_guest_no_marker','hard_timeout_stops_process')
APPLICATION_KEYS=('loopback_only','input_mounted','signed_runtime_installed','node_available','libraries_unpacked_without_hooks','frontend_build','backend_compile','guest_local_home_responded','still_no_external_route','input_media_unchanged','guest_process_stopped')

TOUR_KEYS=('services_bootstrap','services_ready','migrations_applied','tour_acceptance','editor_login','reviewer_login','validated_media_upload','tour_published','two_ordered_stops','public_content_http','public_media_bytes','tenant_isolation','role_separation','wrong_password_rejected','test_data_cleanup')


def utc_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def portable_result(result,isolation,run_id,started_at):
    """Select fixed fields only. No raw logs, source, paths, commands or key values."""
    tour=result.get('profile')=='tudela-offline-tour-v1'
    checks={key:result.get('checks',{}).get(key) for key in APPLICATION_KEYS+(TOUR_KEYS if tour else ())}
    for key in ('input_media_unchanged','guest_process_stopped'):checks[key]=result.get(key)
    record={'format':'reversium-sandbox-result','version':2 if tour else 1,'profile':'tudela-offline-tour-v1' if tour else 'tudela-offline-build-start-v1',
            'tool_version':__version__,'run_id':run_id,'started_at':started_at,'finished_at':utc_now(),
            'archive_sha256':result['delivery']['source_archive_sha256'],
            'tested_input_sha256':result['delivery']['sanitized_archive_sha256'],
            'omitted_member_count':len(result['delivery']['omitted_sensitive_or_generated_members']),
            'accelerator':result['accelerator'],'runtime_versions':result.get('runtime_versions',[]),
            'isolation_checks':{key:isolation.get('checks',{}).get(key) for key in ISOLATION_KEYS},'checks':checks}

    if tour:record.update(guest_ram_mib=3072,service_versions={'postgresql':'17.11','auth':'2.197.0','postgrest':'16.4','storage':'1.83.5'})
    return record
