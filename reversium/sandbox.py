"""Preparation only: no subprocess, package installation, VM boot or ZIP execution."""
import json
import platform
import shutil
from pathlib import Path


def capabilities():
    system=platform.system()
    edition='unknown'
    if system=='Windows':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion') as key:
                edition=winreg.QueryValueEx(key,'EditionID')[0]
        except OSError:
            pass
    display_edition='Home' if edition.startswith('Core') else edition
    windows=bool(shutil.which('WindowsSandbox.exe'))
    qemu=bool(shutil.which('qemu-system-x86_64'))
    return {'system':system,'edition':edition,'windows_sandbox_executable':windows,'qemu_executable':qemu,
            'execution_enabled':False,'summary':f'Host: {system} ({display_edition}). Windows Sandbox executable: {"found" if windows else "not found"}; QEMU executable: {"found" if qemu else "not found"}. Preparation only; guest boot and isolation are untested.'}


def prepare(destination):
    output=Path(destination)
    output.mkdir(parents=True,exist_ok=False)
    status=capabilities()
    (output/'host-check.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    # Blank guest: no mappings, credentials, startup commands or archive input.
    xml='<Configuration>\n'+''.join('  <'+key+'>Disable</'+key+'>\n' for key in ('Networking','ClipboardRedirection','AudioInput','VideoInput','PrinterRedirection','vGPU'))+'  <MemoryInMB>2048</MemoryInMB>\n</Configuration>\n'
    (output/'blank-offline.wsb').write_text(xml,encoding='utf-8')
    argv=['qemu-system-x86_64','-nodefaults','-machine','q35','-accel','tcg','-m','2048','-smp','2','-nic','none','-monitor','none','-serial','none','-vga','std','-drive','file=<TRUSTED_LINUX_ISO>,format=raw,media=cdrom,readonly=on','-boot','d','-snapshot','-no-reboot']
    (output/'qemu-arguments-DRAFT.json').write_text(json.dumps({'status':'untested preparation template; not executable as-is','argv':argv,'missing':['QEMU executable','Trusted bootable Linux ISO and verified provenance','Boot, network-isolation and teardown tests','Reviewed runtime/dependency provisioning','Separate read-only ZIP input design']},indent=2),encoding='utf-8')
    (output/'README.txt').write_text('Reversium sandbox preparation only\n'+status['summary']+'\n\nNo VM was started; no ZIP copied or executed. blank-offline.wsb prepares a blank guest only on a compatible Windows installation. QEMU arguments are an untested draft requiring a trusted Linux ISO, not a ready application runner. No networking, clipboard sharing, host mappings, startup commands or live credentials are included.\n\nDo not add broad host shares, network access or credentials. Do not run unknown scripts. First validate blank-guest boot, absence of network devices and termination. Offline guests may lack all dependencies. No timeout supervisor or automated teardown has been implemented. No isolation system guarantees zero risk.\n',encoding='utf-8')
    return status
