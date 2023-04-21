$DIR = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$PID_DIR = 'tunnel_pids'

Set-Location $DIR

if ($args.Count -eq 3) {
   $target_vm = $args[0]
   $target_port = $args[1]
   $local_port = $args[2]
} else {
   $target_vm = Read-Host 'Enter Target FABRIC VM (ex: username@1.2.3.4)'
   $target_port = Read-Host 'Enter Target Port Number (ex: 22)'
   $local_port = Read-Host 'Enter Local Port Number (ex: 5555)'
}

# maybe add -fN for background
Start-Process ssh -ArgumentList "-fN -L 127.0.0.1:${local_port}:127.0.0.1:${target_port} -i slice_key -F ssh_config ${target_vm}" -NoNewWindow

$PID = Get-Process ssh | Where-Object {$_.StartTime -gt (Get-Date).AddMinutes(-1)} | Select-Object -ExpandProperty Id

New-Item -ItemType Directory -Force -Path $PID_DIR > $null
$PID | Out-File -FilePath "${PID_DIR}\ssh_tunnel_${target_vm}_${target_port}_${local_port}.pid"


