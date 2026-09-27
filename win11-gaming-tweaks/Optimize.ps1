# Windows 11 gaming / low-latency optimization pack
# Target: Ryzen 7 9800X3D + ASUS ROG + GTX 1080 Ti
# All changes are recorded in .\backup\state.json and can be reverted with Restore.ps1

#Requires -RunAsAdministrator
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$BackupDir = Join-Path $PSScriptRoot 'backup'
$StateFile = Join-Path $BackupDir 'state.json'
$LogFile   = Join-Path $BackupDir ("log_{0:yyyyMMdd_HHmmss}.txt" -f (Get-Date))
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

function Log($msg, $color = 'Gray') {
    Write-Host $msg -ForegroundColor $color
    Add-Content -Path $LogFile -Value $msg -Encoding UTF8
}
function Section($title) { Log ''; Log "=== $title ===" 'Cyan' }

function Ask($question) {
    do { $a = (Read-Host "$question [y/n]").Trim().ToLower() } while ($a -notin @('y','n','д','н'))
    return ($a -in @('y','д'))
}

# ---------------------------------------------------------------- state / backup
# The first run records original values. Later runs only add values that were not
# recorded yet, so Restore.ps1 always goes back to the ORIGINAL system state.
$State = [ordered]@{
    Created      = (Get-Date).ToString('s')
    Registry     = New-Object System.Collections.ArrayList
    Services     = New-Object System.Collections.ArrayList
    Tasks        = New-Object System.Collections.ArrayList
    NetAdapter   = New-Object System.Collections.ArrayList
    PowerPrev    = $null
    PowerNew     = $null
    DynamicTick  = $null
    Hypervisor   = $null
    LastAccess   = $null
    Hibernate    = $null
}
if (Test-Path $StateFile) {
    $old = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($k in @('Registry','Services','Tasks','NetAdapter')) {
        if ($old.$k) { foreach ($i in $old.$k) { [void]$State[$k].Add($i) } }
    }
    foreach ($k in @('Created','PowerPrev','PowerNew','DynamicTick','Hypervisor','LastAccess','Hibernate')) {
        if ($null -ne $old.$k) { $State[$k] = $old.$k }
    }
}
function Save-State { $State | ConvertTo-Json -Depth 6 | Set-Content -Path $StateFile -Encoding UTF8 }

function Set-Reg {
    param([string]$Path, [string]$Name, $Value, [string]$Type = 'DWord')
    try {
        $recorded = $State.Registry | Where-Object { $_.Path -eq $Path -and $_.Name -eq $Name }
        if (-not $recorded) {
            $entry = [ordered]@{ Path = $Path; Name = $Name; Existed = $false; Type = $null; Value = $null }
            if (Test-Path $Path) {
                $item = Get-Item -Path $Path -ErrorAction Stop
                if ($item.GetValueNames() -contains $Name) {
                    $entry.Existed = $true
                    $entry.Type    = $item.GetValueKind($Name).ToString()
                    $entry.Value   = $item.GetValue($Name, $null, 'DoNotExpandEnvironmentNames')
                }
            }
            [void]$State.Registry.Add([pscustomobject]$entry)
        }
        if (-not (Test-Path $Path)) { New-Item -Path $Path -Force -ErrorAction Stop | Out-Null }
        New-ItemProperty -Path $Path -Name $Name -Value $Value -PropertyType $Type -Force -ErrorAction Stop | Out-Null
    } catch {
        Log "  ! $Path\$Name : $($_.Exception.Message)" 'DarkYellow'
    }
}

function Set-Svc {
    # Start: 2 = Automatic, 3 = Manual, 4 = Disabled
    param([string]$Name, [int]$Start)
    $path = "HKLM:\SYSTEM\CurrentControlSet\Services\$Name"
    if (-not (Test-Path $path)) { return }
    try {
        $cur = (Get-ItemProperty -Path $path -Name Start -ErrorAction Stop).Start
        if (-not ($State.Services | Where-Object { $_.Name -eq $Name })) {
            [void]$State.Services.Add([pscustomobject]@{ Name = $Name; Start = $cur })
        }
        Set-ItemProperty -Path $path -Name Start -Value $Start -Type DWord -ErrorAction Stop
        if ($Start -eq 4) { Stop-Service -Name $Name -Force -ErrorAction SilentlyContinue }
        Log "  $Name -> $(@{2='Auto';3='Manual';4='Disabled'}[$Start])"
    } catch {
        Log "  ! $Name : $($_.Exception.Message)" 'DarkYellow'
    }
}

function Disable-Task([string]$Full) {
    $taskPath = ($Full.Substring(0, $Full.LastIndexOf('\') + 1))
    $taskName = ($Full.Substring($Full.LastIndexOf('\') + 1))
    try {
        $t = Get-ScheduledTask -TaskPath $taskPath -TaskName $taskName -ErrorAction Stop
        if ($t.State -ne 'Disabled') {
            Disable-ScheduledTask -TaskPath $taskPath -TaskName $taskName | Out-Null
            if (-not ($State.Tasks | Where-Object { $_ -eq $Full })) { [void]$State.Tasks.Add($Full) }
            Log "  $Full"
        }
    } catch { }
}

# ---------------------------------------------------------------- questions
Clear-Host
Log 'Windows 11 Gaming Low-Latency Pack  (9800X3D + ROG + GTX 1080 Ti)' 'Green'
Log 'Все изменения сохраняются в папку backup и откатываются через 2_RESTORE.bat' 'Green'
Log ''
Log 'Ответь на несколько вопросов (y = да, n = нет):' 'Yellow'
$OptXbox      = Ask '1) Отключить Xbox-службы? (НЕ отключай, если играешь через Game Pass / Xbox app / Microsoft Store игры)'
$OptPrint     = Ask '2) Отключить печать (Print Spooler)? (нет принтера = y)'
$OptBluetooth = Ask '3) Отключить Bluetooth? (есть BT-наушники/геймпад = n)'
$OptSearch    = Ask '4) Отключить индексирование поиска Windows Search? (поиск файлов в Пуске станет медленнее)'
$OptVBS       = Ask '5) Отключить VBS / Memory Integrity / Hyper-V? (+5-10% FPS; сломает WSL2/Hyper-V/Android-эмулятор и игры с античитом, требующим VBS, например FACEIT)'
$OptAsus      = Ask '6) Перевести службы ASUS Armoury Crate / LightingService в ручной запуск? (RGB/вентиляторы из Armoury Crate могут перестать управляться до его запуска)'
Log ''

# ---------------------------------------------------------------- restore point
Section 'Точка восстановления'
try {
    Enable-ComputerRestore -Drive "$env:SystemDrive\" -ErrorAction SilentlyContinue
    Set-Reg 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore' 'SystemRestorePointCreationFrequency' 0
    Checkpoint-Computer -Description 'Before Gaming Low-Latency Pack' -RestorePointType MODIFY_SETTINGS -ErrorAction Stop
    Log '  Создана' 'Green'
} catch { Log "  ! Не удалось создать точку восстановления: $($_.Exception.Message)" 'DarkYellow' }
Save-State

# ---------------------------------------------------------------- power plan
Section 'План электропитания (Ultimate Performance)'
try {
    $prev = ([regex]'[0-9a-fA-F-]{36}').Match((powercfg /getactivescheme)).Value
    $existing = @(powercfg /list | Where-Object { $_ -match 'Gaming Low Latency' })
    if ($existing) {
        $guid = ([regex]'[0-9a-fA-F-]{36}').Match($existing[0]).Value
    } else {
        $guid = ([regex]'[0-9a-fA-F-]{36}').Match((powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61)).Value
        powercfg -changename $guid 'Gaming Low Latency' 'Ultimate Performance + no USB/PCIe power saving' | Out-Null
    }
    if (-not $State.PowerPrev -and $prev -ne $guid) { $State.PowerPrev = $prev }
    $State.PowerNew = $guid
    $settings = @(
        @('2a737441-1930-4402-8d77-b2bebba308a3', '48e6b7a6-50f5-4782-a5d4-53bb8f07e226', 0),   # USB selective suspend: off
        @('SUB_PCIEXPRESS', 'ASPM', 0),                                                         # PCIe link state power mgmt: off
        @('SUB_PROCESSOR', 'PROCTHROTTLEMIN', 100),                                             # min CPU state 100%
        @('SUB_PROCESSOR', 'PROCTHROTTLEMAX', 100),
        @('SUB_PROCESSOR', 'CPMINCORES', 100),                                                  # no core parking
        @('SUB_PROCESSOR', 'PERFBOOSTMODE', 2),                                                 # aggressive boost
        @('SUB_DISK', 'DISKIDLE', 0)                                                            # never turn off disks
    )
    foreach ($s in $settings) { powercfg -setacvalueindex $guid $s[0] $s[1] $s[2] 2>$null | Out-Null }
    powercfg -setactive $guid
    Log "  Активен план 'Gaming Low Latency' ($guid)" 'Green'
} catch { Log "  ! $($_.Exception.Message)" 'DarkYellow' }

Set-Reg 'HKLM:\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling' 'PowerThrottlingOff' 1
Log '  Power Throttling: off'

# Hibernation off (also disables Fast Startup, which keeps drivers/timers in a stale state)
try {
    if ($null -eq $State.Hibernate) {
        $State.Hibernate = [bool]((Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Power' -Name HibernateEnabled -ErrorAction SilentlyContinue).HibernateEnabled)
    }
    powercfg -h off
    Log '  Гибернация и быстрый запуск: off'
} catch { }
Save-State

# ---------------------------------------------------------------- GPU / games
Section 'GPU и игровые настройки Windows'
Set-Reg 'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers' 'HwSchMode' 2                 # HAGS on (Pascal supported)
Log '  Hardware-accelerated GPU scheduling: on'

Set-Reg 'HKCU:\Software\Microsoft\GameBar' 'AutoGameModeEnabled' 1
Set-Reg 'HKCU:\Software\Microsoft\GameBar' 'AllowAutoGameMode' 1
Log '  Game Mode: on'

Set-Reg 'HKCU:\System\GameConfigStore' 'GameDVR_Enabled' 0
Set-Reg 'HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR' 'AppCaptureEnabled' 0
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR' 'AllowGameDVR' 0
Set-Reg 'HKCU:\Software\Microsoft\GameBar' 'UseNexusForGameBarEnabled' 0
Log '  Game DVR / фоновая запись: off'

Set-Reg 'HKCU:\Software\Microsoft\DirectX\UserGpuPreferences' 'DirectXUserGlobalSettings' 'SwapEffectUpgradeEnable=1;' 'String'
Log '  Оптимизация оконных игр (flip model): on'

# MMCSS: give games priority, stop network throttling
$mm = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile'
Set-Reg $mm 'NetworkThrottlingIndex' 0xffffffff
Set-Reg $mm 'SystemResponsiveness' 10
Set-Reg "$mm\Tasks\Games" 'GPU Priority' 8
Set-Reg "$mm\Tasks\Games" 'Priority' 6
Set-Reg "$mm\Tasks\Games" 'Scheduling Category' 'High' 'String'
Set-Reg "$mm\Tasks\Games" 'SFIO Priority' 'High' 'String'
Log '  MMCSS: приоритет игр High, NetworkThrottling off'

Set-Reg 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' 'Win32PrioritySeparation' 0x26
Log '  Планировщик: приоритет активного окна (0x26)'

Set-Reg 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\kernel' 'GlobalTimerResolutionRequests' 1
Log '  Глобальное разрешение таймера для игр: on'

# MSI (message signaled interrupts) for the NVIDIA GPU -> lower DPC/ISR latency
try {
    $gpus = Get-PnpDevice -Class Display -PresentOnly -ErrorAction Stop | Where-Object { $_.FriendlyName -match 'NVIDIA' }
    foreach ($g in $gpus) {
        $p = "HKLM:\SYSTEM\CurrentControlSet\Enum\$($g.InstanceId)\Device Parameters\Interrupt Management\MessageSignaledInterruptProperties"
        Set-Reg $p 'MSISupported' 1
        Log "  MSI mode: $($g.FriendlyName)"
    }
} catch { Log "  ! MSI mode: $($_.Exception.Message)" 'DarkYellow' }
Save-State

# ---------------------------------------------------------------- input
Section 'Мышь и клавиатура'
Set-Reg 'HKCU:\Control Panel\Mouse' 'MouseSpeed' '0' 'String'
Set-Reg 'HKCU:\Control Panel\Mouse' 'MouseThreshold1' '0' 'String'
Set-Reg 'HKCU:\Control Panel\Mouse' 'MouseThreshold2' '0' 'String'
Log '  Акселерация мыши (Enhance pointer precision): off'
Set-Reg 'HKCU:\Control Panel\Accessibility\StickyKeys' 'Flags' '506' 'String'
Set-Reg 'HKCU:\Control Panel\Accessibility\ToggleKeys' 'Flags' '58' 'String'
Set-Reg 'HKCU:\Control Panel\Accessibility\Keyboard Response' 'Flags' '122' 'String'
Log '  Залипание клавиш (5x Shift) и фильтрация ввода: off'

# ---------------------------------------------------------------- network
Section 'Сеть'
try {
    $ifs = Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces'
    foreach ($i in $ifs) {
        $props = Get-ItemProperty $i.PSPath
        if ($props.DhcpIPAddress -or ($props.IPAddress -and $props.IPAddress -ne '0.0.0.0')) {
            $p = $i.PSPath -replace '^Microsoft.PowerShell.Core\\Registry::HKEY_LOCAL_MACHINE', 'HKLM:'
            Set-Reg $p 'TcpAckFrequency' 1
            Set-Reg $p 'TCPNoDelay' 1
            Set-Reg $p 'TcpDelAckTicks' 0
        }
    }
    Log '  Nagle / delayed ACK: off'
} catch { Log "  ! $($_.Exception.Message)" 'DarkYellow' }

# NIC power saving features (Intel I226 / Realtek 2.5G on ROG boards)
$nicKeys = @('*EEE', 'EEE', 'AdvancedEEE', 'EEELinkAdvertisement', 'EnableGreenEthernet', 'GreenEthernet',
             'PowerSavingMode', 'ULPMode', 'EnableSavePowerNow', 'EnablePowerManagement', 'ReduceSpeedOnPowerDown',
             '*SelectiveSuspend', 'AutoPowerSaveModeEnabled')
try {
    foreach ($a in (Get-NetAdapter -Physical -ErrorAction Stop | Where-Object { $_.Status -eq 'Up' })) {
        foreach ($p in (Get-NetAdapterAdvancedProperty -Name $a.Name -ErrorAction SilentlyContinue | Where-Object { $nicKeys -contains $_.RegistryKeyword })) {
            $old = [string]($p.RegistryValue | Select-Object -First 1)
            if ($old -ne '0') {
                if (-not ($State.NetAdapter | Where-Object { $_.Adapter -eq $a.Name -and $_.Keyword -eq $p.RegistryKeyword })) {
                    [void]$State.NetAdapter.Add([pscustomobject]@{ Adapter = $a.Name; Keyword = $p.RegistryKeyword; Value = $old })
                }
                try {
                    Set-NetAdapterAdvancedProperty -Name $a.Name -RegistryKeyword $p.RegistryKeyword -RegistryValue '0' -NoRestart -ErrorAction Stop
                    Log "  $($a.Name): $($p.DisplayName) -> off"
                } catch { }
            }
        }
    }
} catch { }
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization' 'DODownloadMode' 0
Log '  Delivery Optimization (раздача обновлений другим ПК): off'
Save-State

# ---------------------------------------------------------------- system latency
Section 'Системные таймеры и файловая система'
try {
    bcdedit /deletevalue useplatformclock 2>$null | Out-Null         # HPET forced off (default)
    if ($null -eq $State.DynamicTick) {
        $State.DynamicTick = [bool]((bcdedit /enum '{current}') -match 'disabledynamictick\s+Yes')
    }
    bcdedit /set disabledynamictick yes | Out-Null
    Log '  useplatformclock: default, disabledynamictick: yes'
} catch { Log "  ! bcdedit: $($_.Exception.Message)" 'DarkYellow' }

try {
    if ($null -eq $State.LastAccess) {
        $State.LastAccess = [int]([regex]'=\s*(\d)').Match((fsutil behavior query disablelastaccess)).Groups[1].Value
    }
    fsutil behavior set disablelastaccess 1 | Out-Null
    Log '  NTFS last access timestamp: off'
} catch { }
Save-State

# ---------------------------------------------------------------- VBS
if ($OptVBS) {
    Section 'VBS / Memory Integrity / Hyper-V'
    Set-Reg 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard' 'EnableVirtualizationBasedSecurity' 0
    Set-Reg 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity' 'Enabled' 0
    Set-Reg 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa' 'LsaCfgFlags' 0
    try {
        if ($null -eq $State.Hypervisor) {
            $m = [regex]::Match(((bcdedit /enum '{current}') -join "`n"), 'hypervisorlaunchtype\s+(\w+)')
            $State.Hypervisor = if ($m.Success) { $m.Groups[1].Value } else { 'None' }
        }
        bcdedit /set hypervisorlaunchtype off | Out-Null
    } catch { }
    Log '  VBS / HVCI / Hyper-V: off (после перезагрузки проверь msinfo32 -> "Virtualization-based security: Not enabled")'
    Save-State
}

# ---------------------------------------------------------------- services
Section 'Службы'
$svcDisable = @(
    'DiagTrack',            # Connected User Experiences and Telemetry
    'dmwappushservice',     # WAP push (telemetry)
    'WerSvc',               # Windows Error Reporting
    'wercplsupport',        # Problem reports control panel
    'PcaSvc',               # Program Compatibility Assistant
    'SysMain',              # Superfetch (useless on NVMe, causes background disk/CPU)
    'MapsBroker',           # Downloaded Maps Manager
    'lfsvc',                # Geolocation
    'RemoteRegistry',       # Remote Registry
    'RemoteAccess',         # Routing and Remote Access
    'Fax',
    'RetailDemo',
    'WMPNetworkSvc',        # WMP network sharing
    'TrkWks',               # Distributed Link Tracking Client
    'wisvc',                # Windows Insider
    'WpcMonSvc',            # Parental Controls
    'PhoneSvc',             # Phone service
    'SEMgrSvc',             # Payments and NFC
    'diagnosticshub.standardcollector.service',
    'NvTelemetryContainer'  # old NVIDIA telemetry (if present)
)
$svcManual = @(
    'edgeupdate', 'edgeupdatem',
    'WdiServiceHost', 'WdiSystemHost',  # diagnostics - start only on demand
    'MicrosoftEdgeElevationService'
)
if ($OptXbox)      { $svcDisable += @('XblAuthManager', 'XblGameSave', 'XboxNetApiSvc', 'XboxGipSvc', 'GamingServices', 'GamingServicesNet') }
if ($OptPrint)     { $svcDisable += @('Spooler', 'PrintNotify') }
if ($OptBluetooth) { $svcDisable += @('bthserv', 'BTAGService', 'BthAvctpSvc') }
if ($OptSearch)    { $svcDisable += 'WSearch' }
if ($OptAsus)      { $svcManual += @('ArmouryCrateService', 'AsusCertService', 'LightingService', 'ROG Live Service',
                                     'asComSvc', 'AsusUpdateCheck', 'ArmouryCrateControlInterface', 'AsusAppService', 'asus', 'asusm') }

foreach ($s in $svcDisable) { Set-Svc $s 4 }
foreach ($s in $svcManual)  { Set-Svc $s 3 }
Save-State

# ---------------------------------------------------------------- telemetry / background
Section 'Телеметрия, реклама, фоновые приложения'
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection' 'AllowTelemetry' 0
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection' 'DoNotShowFeedbackNotifications' 1
Set-Reg 'HKCU:\Software\Microsoft\Siuf\Rules' 'NumberOfSIUFInPeriod' 0
Set-Reg 'HKCU:\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo' 'Enabled' 0
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo' 'DisabledByGroupPolicy' 1
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\System' 'EnableActivityFeed' 0
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\System' 'PublishUserActivities' 0
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\System' 'UploadUserActivities' 0
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppCompat' 'AITEnable' 0
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppCompat' 'DisableInventory' 1
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting' 'Disabled' 1
Set-Reg 'HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting' 'Disabled' 1
Log '  Телеметрия, реклама, история активности, отчёты об ошибках: off'

Set-Reg 'HKCU:\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications' 'GlobalUserDisabled' 1
Set-Reg 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Search' 'BackgroundAppGlobalToggle' 0
Log '  Фоновые UWP-приложения: off'

Set-Reg 'HKCU:\Software\Policies\Microsoft\Windows\WindowsCopilot' 'TurnOffWindowsCopilot' 1
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot' 'TurnOffWindowsCopilot' 1
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI' 'DisableAIDataAnalysis' 1
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Dsh' 'AllowNewsAndInterests' 0
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search' 'AllowCortana' 0
Set-Reg 'HKCU:\Software\Policies\Microsoft\Windows\Explorer' 'DisableSearchBoxSuggestions' 1
Log '  Copilot, Recall, виджеты, веб-поиск в Пуске: off'

$cdm = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager'
foreach ($n in @('SilentInstalledAppsEnabled', 'SystemPaneSuggestionsEnabled', 'SoftLandingEnabled',
                 'SubscribedContent-338388Enabled', 'SubscribedContent-338389Enabled', 'SubscribedContent-310093Enabled',
                 'SubscribedContent-353694Enabled', 'SubscribedContent-353696Enabled', 'PreInstalledAppsEnabled',
                 'OemPreInstalledAppsEnabled', 'ContentDeliveryAllowed')) { Set-Reg $cdm $n 0 }
Log '  Советы, реклама и автоустановка приложений: off'

Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' 'StartupBoostEnabled' 0
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' 'BackgroundModeEnabled' 0
Log '  Edge в фоне и Startup Boost: off'

Section 'Задачи планировщика (телеметрия)'
@(
    '\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser',
    '\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser Exp',
    '\Microsoft\Windows\Application Experience\ProgramDataUpdater',
    '\Microsoft\Windows\Application Experience\StartupAppTask',
    '\Microsoft\Windows\Application Experience\PcaPatchDbTask',
    '\Microsoft\Windows\Customer Experience Improvement Program\Consolidator',
    '\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip',
    '\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector',
    '\Microsoft\Windows\Feedback\Siuf\DmClient',
    '\Microsoft\Windows\Feedback\Siuf\DmClientOnScenarioDownload',
    '\Microsoft\Windows\Windows Error Reporting\QueueReporting',
    '\Microsoft\Windows\Maps\MapsUpdateTask',
    '\Microsoft\Windows\Maps\MapsToastTask',
    '\Microsoft\Windows\Autochk\Proxy',
    '\Microsoft\Windows\CloudExperienceHost\CreateObjectTask'
) | ForEach-Object { Disable-Task $_ }
Save-State

# ---------------------------------------------------------------- visuals
Section 'Интерфейс'
Set-Reg 'HKCU:\Control Panel\Desktop' 'MenuShowDelay' '0' 'String'
Set-Reg 'HKCU:\Control Panel\Desktop\WindowMetrics' 'MinAnimate' '0' 'String'
Set-Reg 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' 'TaskbarAnimations' 0
Set-Reg 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize' 'EnableTransparency' 0
Set-Reg 'HKCU:\Software\Microsoft\Windows\DWM' 'EnableAeroPeek' 0
Set-Reg 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' 'ShowTaskViewButton' 0
Set-Reg 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' 'TaskbarDa' 0
Set-Reg 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize' 'StartupDelayInMSec' 0
Log '  Анимации, прозрачность, задержка меню и автозагрузки: off'
Save-State

# ---------------------------------------------------------------- cleanup
Section 'Очистка временных файлов'
foreach ($d in @($env:TEMP, "$env:SystemRoot\Temp")) {
    Get-ChildItem -Path $d -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}
Log '  Готово'

Save-State
Log ''
Log '================================================================' 'Green'
Log ' ГОТОВО. ОБЯЗАТЕЛЬНО ПЕРЕЗАГРУЗИ ПК.' 'Green'
Log " Бэкап исходных настроек: $StateFile" 'Green'
Log ' Откат: 2_RESTORE.bat' 'Green'
Log ' Дальше - ручные шаги из README.md (BIOS, панель NVIDIA, драйверы).' 'Green'
Log '================================================================' 'Green'
if (Ask 'Перезагрузить сейчас?') { Restart-Computer -Force }
