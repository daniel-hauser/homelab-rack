# SPDX-License-Identifier: MIT

[CmdletBinding()]
param(
    [ValidateSet('Verify', 'Generate')]
    [string]$Mode = 'Verify'
)

$ErrorActionPreference = 'Stop'

$openScad = (Get-Command openscad -ErrorAction SilentlyContinue).Source
if (-not $openScad) {
    $candidates = @(
        "$env:ProgramFiles\OpenSCAD\openscad.exe",
        "${env:ProgramFiles(x86)}\OpenSCAD\openscad.exe",
        "$env:LOCALAPPDATA\Programs\OpenSCAD\openscad.exe"
    )
    $openScad = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}

if (-not $openScad) {
    throw 'OpenSCAD was not found. Install OpenSCAD 2021.01, then rerun this script.'
}

$version = (& $openScad --version 2>&1 | Out-String).Trim()
if ($version -notmatch '2021\.01') {
    throw "This release is pinned to OpenSCAD 2021.01; found: $version"
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $root 'homelab_rack.scad'
$work = Join-Path $root 'out\release-work'
$renders = Join-Path $root 'renders'
$viewerModels = Join-Path $root 'viewer\public\models'
New-Item -ItemType Directory -Force -Path $work, $renders, $viewerModels | Out-Null

$artifacts = @(
    @{ Part = 'ucg_left'; Target = 'PRINT_THESE\STLs\01_UCG_Ultra.stl'; Viewer = '01_UCG_Ultra.stl' },
    @{ Part = 'usw_left'; Target = 'PRINT_THESE\STLs\02_USW_Ultra_Left.stl'; Viewer = '02_USW_Ultra_Left.stl' },
    @{ Part = 'usw_right'; Target = 'PRINT_THESE\STLs\03_USW_Ultra_Right.stl'; Viewer = '03_USW_Ultra_Right.stl' },
    @{ Part = 'dual_pi_left'; Target = 'PRINT_THESE\STLs\04_Dual_Pi_Chassis.stl'; Viewer = '04_Dual_Pi_Chassis.stl' },
    @{ Part = 'pi_cartridge_1'; Target = 'PRINT_THESE\STLs\05_Pi_Drawer_1.stl'; Viewer = '05_Pi_Drawer_1.stl' },
    @{ Part = 'pi_cartridge_2'; Target = 'PRINT_THESE\STLs\06_Pi_Drawer_2.stl'; Viewer = '06_Pi_Drawer_2.stl' },
    @{ Part = 'vent_cartridge'; Target = 'PRINT_THESE\STLs\07_Vent_Insert.stl'; Viewer = '07_Vent_Insert.stl' },
    @{ Part = 'uk_ultra_top'; Target = 'PRINT_THESE\STLs\08_UK_Ultra_Top.stl'; Viewer = '08_UK_Ultra_Top.stl' },
    @{ Part = 'desk_spine_4u'; Target = 'PRINT_THESE\STLs\09_Rear_Spine_A.stl'; Viewer = '09_Rear_Spine_A.stl' },
    @{ Part = 'desk_spine_4u'; Target = 'PRINT_THESE\STLs\10_Rear_Spine_B.stl'; Viewer = '10_Rear_Spine_B.stl' },
    @{ Part = 'bay_fit_test'; Target = 'PRINT_THESE\TEST_FIRST\01_Bay_Fit_Test.stl' },
    @{ Part = 'desk_spine_4u'; Target = 'PRINT_THESE\TEST_FIRST\02_Rear_Spine_A.stl' },
    @{ Part = 'desk_spine_4u'; Target = 'PRINT_THESE\TEST_FIRST\03_Rear_Spine_B.stl' },
    @{ Part = 'desktop_feet_set'; Target = 'PRINT_THESE\TEST_FIRST\04_Desktop_Feet_Set.stl' },
    @{ Part = 'fit_test'; Target = 'PRINT_THESE\TEST_FIRST\05_Magnet_Keystone_Peg_Test.stl' },
    @{ Part = 'vent_cartridge'; Target = 'PRINT_THESE\TEST_FIRST\06_Vent_Insert.stl' },
    @{ Part = 'magnet_polarity_key'; Target = 'PRINT_THESE\TEST_FIRST\07_Magnet_Polarity_Key.stl' },
    @{ Part = 'rack_ear_fit_test'; Target = 'PRINT_THESE\TEST_FIRST\08_Rack_Ear_Test.stl' },
    @{ Part = 'side_tower_male_test'; Target = 'PRINT_THESE\TEST_FIRST\09_Seam_Tower_Male_Test.stl' },
    @{ Part = 'side_tower_socket_test'; Target = 'PRINT_THESE\TEST_FIRST\10_Seam_Tower_Female_Test.stl' }
)

function Export-Part([string]$Part) {
    $output = Join-Path $work "$Part.stl"
    if (-not (Test-Path $output)) {
        & $openScad -o $output -D "part=`"$Part`"" $source 2>&1 | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "OpenSCAD failed while exporting $Part."
        }
    }
    return $output
}

function Sync-Or-Verify([string]$Generated, [string]$RelativeTarget) {
    $target = Join-Path $root $RelativeTarget
    if ($Mode -eq 'Generate') {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        Copy-Item -Force $Generated $target
        Write-Host "Generated $RelativeTarget"
        return
    }

    if (-not (Test-Path $target)) {
        throw "Missing release artifact: $RelativeTarget"
    }
    $generatedHash = (Get-FileHash $Generated -Algorithm SHA256).Hash
    $targetHash = (Get-FileHash $target -Algorithm SHA256).Hash
    if ([IO.Path]::GetExtension($target) -ieq '.stl') {
        $script = @'
import sys
import trimesh
mesh = trimesh.load_mesh(sys.argv[1], process=False)
if isinstance(mesh, trimesh.Scene):
    mesh = mesh.to_geometry()
print(mesh.identifier_hash)
'@
        $generatedGeometry = ($script | python - $Generated).Trim()
        $targetGeometry = ($script | python - $target).Trim()
        if ($LASTEXITCODE -ne 0 -or $generatedGeometry -ne $targetGeometry) {
            throw "Geometry mismatch for $RelativeTarget"
        }
        Write-Host "Verified geometry for $RelativeTarget (tracked SHA-256 $targetHash)"
        return
    }
    if ($generatedHash -ne $targetHash) {
        throw "Hash mismatch for $RelativeTarget`nGenerated: $generatedHash`nTracked:   $targetHash"
    }
    Write-Host "Verified $RelativeTarget ($targetHash)"
}

foreach ($artifact in $artifacts) {
    $generated = Export-Part $artifact.Part
    Sync-Or-Verify $generated $artifact.Target
    if ($artifact.Viewer) {
        Sync-Or-Verify $generated (Join-Path 'viewer\public\models' $artifact.Viewer)
    }
}

$installedFeet = Export-Part 'installed_desktop_feet'
Sync-Or-Verify $installedFeet 'viewer\public\models\desktop_feet_installed.stl'

$previews = @(
    @{ Part = 'desk_preview'; File = 'desk_preview_final.png' },
    @{ Part = 'rack_preview'; File = 'rack_preview_final.png' },
    @{ Part = 'side_join_preview'; File = 'side_join_preview.png' },
    @{ Part = 'modular_bay_preview'; File = 'modular_bay_preview_final.png' }
)

foreach ($preview in $previews) {
    $generated = Join-Path $work $preview.File
    & $openScad `
        -o $generated `
        '--imgsize=1600,1000' `
        '--viewall' `
        '--autocenter' `
        --colorscheme Tomorrow `
        -D "part=`"$($preview.Part)`"" `
        $source 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "OpenSCAD failed while rendering $($preview.Part)."
    }
    Sync-Or-Verify $generated (Join-Path 'renders' $preview.File)
}

Sync-Or-Verify `
    (Join-Path $root 'slicer\release\estimate.json') `
    'viewer\public\estimate.json'

Write-Host "$Mode completed for 20 release STLs, 11 viewer meshes, 4 canonical renders, and viewer estimates."
