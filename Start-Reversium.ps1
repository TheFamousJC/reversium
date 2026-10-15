param([int]$Port = 0)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskPython = Get-Command python -ErrorAction SilentlyContinue
$taskBundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $taskBundled) {
    & $taskBundled -m reversium --port $Port
} elseif ($taskPython) {
    & $taskPython.Source -m reversium --port $Port
} else {
    throw 'Install Python 3.10 or newer, then run python -m reversium.'
}
