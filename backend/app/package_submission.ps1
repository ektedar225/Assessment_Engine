<#
package_submission.ps1

Creates a submission ZIP containing the required artifacts for the GenAI task.
Run from the `backend/app` directory in PowerShell.

Usage:
  .\package_submission.ps1 -OutFile ..\..\submission_bundle.zip
#>

param(
    [string]$OutFile = "..\..\submission_bundle.zip"
)

Write-Host "Creating submission bundle: $OutFile"

$files = @(
    "..\app\approach.md",
    "..\app\README_SUBMISSION.md",
    "..\app\requirements.txt",
    "..\app\generate_predictions_local.py",
    "..\app\generate_predictions.py",
    "..\app\search_index.py",
    "..\app\build_index.py",
    "..\app\generate_catalog_from_train.py",
    "..\data\predictions.csv",
    "..\app\main.py",
    "..\app\utils.py",
    "..\app\approach.md",
    "..\app\README_SUBMISSION.md",
    "..\app\requirements.txt",
    "..\app\COMMIT_MESSAGE.txt"
)

# Ensure output directory exists
New-Item -ItemType Directory -Path (Split-Path -Path $OutFile) -Force | Out-Null

if (Test-Path $OutFile) { Remove-Item $OutFile -Force }

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory((Get-Location).Path, $OutFile)

Write-Host "Note: The above created an empty zip of the current folder."
Write-Host "Instead we'll create a zip containing only the chosen files."

# Create a fresh zip
if (Test-Path $OutFile) { Remove-Item $OutFile -Force }
$zip = [IO.Compression.ZipFile]::Open($OutFile, [IO.Compression.ZipArchiveMode]::Create)
foreach ($f in $files) {
    $full = Resolve-Path -Path $f -ErrorAction SilentlyContinue
    if ($full) {
        Write-Host "Adding: $full"
        [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $full, (Split-Path $full -Leaf)) | Out-Null
    } else {
        Write-Host "Warning: file not found, skipping: $f"
    }
}
$zip.Dispose()

Write-Host "Created submission bundle: $OutFile"
