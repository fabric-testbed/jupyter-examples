$DIR = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$PID_DIR = 'tunnel_pids'

# Set-Location $DIR

foreach ($pid_file in $args) {
    if (Test-Path $pid_file) {
        Write-Host "kill $pid_file"
        $pid = Get-Content $pid_file
        Stop-Process $pid
        Remove-Item $pid_file
    } else {
        Write-Host "not killing $pid_file"
    }
}

