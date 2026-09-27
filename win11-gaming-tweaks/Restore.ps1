# Reverts everything Optimize.ps1 changed, using .\backup\state.json

#Requires -RunAsAdministrator
$ErrorActionPreference = 'Continue'
$StateFile = Join-Path $PSScriptRoot 'backup\state.json'

if (-not (Test-Path $StateFile)) {
    Write-Host "Бэкап не найден: $StateFile" -ForegroundColor Red
    Write-Host 'Используй точку восстановления Windows: rstrui.exe' -ForegroundColor Yellow
    exit 1
}
$State = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Host "Откат изменений от $($State.Created)" -ForegroundColor Green

Write-Host "`n=== Реестр ===" -ForegroundColor Cyan
foreach ($r in $State.Registry) {
    try {
        if ($r.Existed) {
            if (-not (Test-Path $r.Path)) { New-Item -Path $r.Path -Force | Out-Null }
            $v = $r.Value
            switch ($r.Type) {
                'Binary'      { $v = [byte[]]@($r.Value) }
                'MultiString' { $v = [string[]]@($r.Value) }
                'DWord'       { $v = [int]$r.Value }
                'QWord'       { $v = [long]$r.Value }
            }
            New-ItemProperty -Path $r.Path -Name $r.Name -Value $v -PropertyType $r.Type -Force -ErrorAction Stop | Out-Null
        } elseif (Test-Path $r.Path) {
            Remove-ItemProperty -Path $r.Path -Name $r.Name -ErrorAction SilentlyContinue
        }
    } catch { Write-Host "  ! $($r.Path)\$($r.Name): $($_.Exception.Message)" -ForegroundColor DarkYellow }
}
Write-Host "  Восстановлено значений: $(@($State.Registry).Count)"

Write-Host "`n=== Службы ===" -ForegroundColor Cyan
foreach ($s in $State.Services) {
    try {
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\$($s.Name)" -Name Start -Value ([int]$s.Start) -Type DWord -ErrorAction Stop
        Write-Host "  $($s.Name) -> Start=$($s.Start)"
    } catch { Write-Host "  ! $($s.Name): $($_.Exception.Message)" -ForegroundColor DarkYellow }
}

Write-Host "`n=== Задачи планировщика ===" -ForegroundColor Cyan
foreach ($t in $State.Tasks) {
    $path = $t.Substring(0, $t.LastIndexOf('\') + 1)
    $name = $t.Substring($t.LastIndexOf('\') + 1)
    Enable-ScheduledTask -TaskPath $path -TaskName $name -ErrorAction SilentlyContinue | Out-Null
    Write-Host "  $t"
}

Write-Host "`n=== Сетевой адаптер ===" -ForegroundColor Cyan
foreach ($n in $State.NetAdapter) {
    try {
        Set-NetAdapterAdvancedProperty -Name $n.Adapter -RegistryKeyword $n.Keyword -RegistryValue $n.Value -NoRestart -ErrorAction Stop
        Write-Host "  $($n.Adapter): $($n.Keyword) = $($n.Value)"
    } catch { }
}

Write-Host "`n=== Электропитание / загрузчик / NTFS ===" -ForegroundColor Cyan
if ($State.PowerPrev) {
    powercfg -setactive $State.PowerPrev
    Write-Host "  Активен прежний план $($State.PowerPrev)"
    if ($State.PowerNew) { powercfg -delete $State.PowerNew 2>$null | Out-Null }
}
if ($State.Hibernate -eq $true) { powercfg -h on; Write-Host '  Гибернация: on' }
if ($State.DynamicTick -eq $false) { bcdedit /deletevalue disabledynamictick | Out-Null; Write-Host '  disabledynamictick: default' }
if ($State.Hypervisor) {
    if ($State.Hypervisor -eq 'None') { bcdedit /deletevalue hypervisorlaunchtype | Out-Null }
    else { bcdedit /set hypervisorlaunchtype $State.Hypervisor | Out-Null }
    Write-Host "  hypervisorlaunchtype: $($State.Hypervisor)"
}
if ($null -ne $State.LastAccess) { fsutil behavior set disablelastaccess $State.LastAccess | Out-Null; Write-Host "  disablelastaccess: $($State.LastAccess)" }

Rename-Item -Path $StateFile -NewName ("state_restored_{0:yyyyMMdd_HHmmss}.json" -f (Get-Date))

Write-Host "`nГОТОВО. Перезагрузи ПК." -ForegroundColor Green
$a = Read-Host 'Перезагрузить сейчас? [y/n]'
if ($a -in @('y', 'д')) { Restart-Computer -Force }
