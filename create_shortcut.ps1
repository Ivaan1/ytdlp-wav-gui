# Crea un acceso directo en el menú Inicio (y opcionalmente en el escritorio)
# que abre la app con pythonw.exe, sin ventana de consola.
# Uso: powershell -ExecutionPolicy Bypass -File create_shortcut.ps1 [-Desktop]
param([switch]$Desktop)

$root = $PSScriptRoot
$pythonw = Join-Path $root ".venv\Scripts\pythonw.exe"
if (-not (Test-Path $pythonw)) {
    Write-Error "No se encontró $pythonw. Crea primero el venv (python -m venv .venv)."
    exit 1
}

$targets = @([Environment]::GetFolderPath("Programs"))
if ($Desktop) { $targets += [Environment]::GetFolderPath("Desktop") }

$shell = New-Object -ComObject WScript.Shell
foreach ($dir in $targets) {
    $lnkPath = Join-Path $dir "yt-dlp audio.lnk"
    $lnk = $shell.CreateShortcut($lnkPath)
    $lnk.TargetPath = $pythonw
    $lnk.Arguments = "`"$(Join-Path $root 'main.py')`""
    $lnk.WorkingDirectory = $root
    $lnk.IconLocation = (Join-Path $root "assets\icon.ico") + ",0"
    $lnk.Description = "Descarga audio de YouTube con yt-dlp"
    $lnk.Save()
    Write-Output "Creado: $lnkPath"
}
