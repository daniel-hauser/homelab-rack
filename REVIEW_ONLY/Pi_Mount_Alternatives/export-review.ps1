# SPDX-License-Identifier: MIT

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$source = Join-Path $root 'homelab_rack.scad'
$openScad = (Get-Command openscad -ErrorAction SilentlyContinue).Source

if (-not $openScad) {
    $candidates = @(
        "$env:ProgramFiles\OpenSCAD\openscad.exe",
        "${env:ProgramFiles(x86)}\OpenSCAD\openscad.exe",
        "$env:LOCALAPPDATA\Programs\OpenSCAD\openscad.exe"
    )
    $openScad = $candidates |
        Where-Object { Test-Path $_ } |
        Select-Object -First 1
}

if (-not $openScad) {
    throw 'OpenSCAD was not found.'
}

$exports = @(
    @{
        Part = 'pi_mount_review_magnetic_stl'
        File = 'A_Magnetic_Cradle_Review.stl'
        Type = 'stl'
    },
    @{
        Part = 'pi_mount_review_mechanical_stl'
        File = 'B_Through_Floor_M2.5_Review.stl'
        Type = 'stl'
    },
    @{
        Part = 'pi_mount_review_magnetic_cutaway'
        File = 'A_Magnetic_Cradle_Cutaway.png'
        Type = 'png'
    },
    @{
        Part = 'pi_mount_review_magnetic_underside'
        File = 'A_Magnetic_Cradle_Underside.png'
        Type = 'png'
    },
    @{
        Part = 'pi_mount_review_mechanical_cutaway'
        File = 'B_Through_Floor_M2.5_Cutaway.png'
        Type = 'png'
    },
    @{
        Part = 'pi_mount_review_mechanical_underside'
        File = 'B_Through_Floor_M2.5_Underside.png'
        Type = 'png'
    }
)

foreach ($export in $exports) {
    $target = Join-Path $PSScriptRoot $export.File
    $arguments = @(
        '-o', $target,
        '-D', "part=`"$($export.Part)`""
    )
    if ($export.Type -eq 'png') {
        $arguments += @(
            '--imgsize=1600,1000',
            '--autocenter',
            '--colorscheme', 'Tomorrow'
        )
        if ($export.File -like '*Cutaway.png') {
            $arguments += @(
                '--camera=0,0,0,60,0,25,350',
                '--projection=o'
            )
        } else {
            $arguments += '--viewall'
        }
    }
    $arguments += $source

    & $openScad @arguments 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "OpenSCAD failed while exporting $($export.Part)."
    }
    Write-Host "Generated $target"
}
