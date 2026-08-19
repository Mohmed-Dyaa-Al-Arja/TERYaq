$ErrorActionPreference = "Stop"

Write-Host "=== Teryaq Backend + Model Cleanup ===" -ForegroundColor Cyan

# Run this script from the extracted update-package folder,
# NOT from D:\Teryaq itself.
$projectRoot = "D:\Teryaq"

if (-not (Test-Path ".\backend")) {
    throw "The update package is incomplete. Extract the ZIP and run this script from its root folder."
}

if (-not (Test-Path "$projectRoot\backend")) {
    throw "Project folder D:\Teryaq was not found."
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = "..\Teryaq_before_model_update_$stamp"

Write-Host "Creating backup: $backup" -ForegroundColor Yellow
Copy-Item "." $backup -Recurse -Force -Exclude "__pycache__"
Write-Host "Backup created." -ForegroundColor Green

# Remove Python caches
Get-ChildItem "." -Directory -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq "__pycache__" } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Get-ChildItem "." -File -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -eq ".pyc" } |
    Remove-Item -Force -ErrorAction SilentlyContinue

# Remove old vehicle-specific backend files
$removeFiles = @(
    ".\backend\controllers\compare_controller.py",
    ".\backend\controllers\image_controller.py",
    ".\backend\memory\comparison_memory.py",
    ".\backend\memory\vehicle_memory.py",
    ".\backend\routes\compare_routes.py",
    ".\backend\routes\image_routes.py",
    ".\backend\services\compare_service.py",
    ".\backend\services\search_service.py",
    ".\backend\services\vehicle_service.py",
    ".\frontend\api\compare_api.py",
    ".\frontend\api\vehicle_api.py",
    ".\frontend\img\car_dark_page1.png",
    ".\frontend\img\car_light_page1.png"
)

foreach ($file in $removeFiles) {
    if (Test-Path -LiteralPath $file) {
        Remove-Item -LiteralPath $file -Force
        Write-Host "Removed $file" -ForegroundColor DarkYellow
    }
}

# Remove duplicate "(2)" copies inside backend only.
Get-ChildItem ".\backend" -File -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match " \(2\)\." } |
    Remove-Item -Force -ErrorAction SilentlyContinue

# Remove old ranking folder if it is still present.
if (Test-Path ".\backend\ranking") {
    Remove-Item ".\backend\ranking" -Recurse -Force
}

# Remove the accidental literal folder.
$literalWrongFolder = ".\backend\{controllers,services,memory,rag,ranking,routes}"
if (Test-Path -LiteralPath $literalWrongFolder) {
    Remove-Item -LiteralPath $literalWrongFolder -Force
}

# Remove the old vehicle Qwen package.
if (Test-Path ".\models\qwen") {
    Remove-Item ".\models\qwen" -Recurse -Force
    Write-Host "Removed old models\qwen vehicle package." -ForegroundColor DarkYellow
}

# Remove old model demo.
if (Test-Path ".\models\demo.py") {
    Remove-Item ".\models\demo.py" -Force
}

# Copy the new backend files from this update package.
Write-Host "Copying new backend files..." -ForegroundColor Yellow
Copy-Item ".\backend\embedding" "$projectRoot\backend\embedding" -Recurse -Force
Copy-Item ".\backend\llm" "$projectRoot\backend\llm" -Recurse -Force
Copy-Item ".\backend\ingestion" "$projectRoot\backend\ingestion" -Recurse -Force
Copy-Item ".\backend\rag" "$projectRoot\backend\rag" -Recurse -Force
Copy-Item ".\backend\safety" "$projectRoot\backend\safety" -Recurse -Force
Copy-Item ".\backend\config" "$projectRoot\backend\config" -Recurse -Force
Copy-Item ".\backend\multimodal" "$projectRoot\backend\multimodal" -Recurse -Force
Copy-Item ".\backend\requirements.txt" "$projectRoot\backend\requirements.txt" -Force

if (-not (Test-Path "$projectRoot\.env.example")) {
    Copy-Item ".\.env.example" "$projectRoot\.env.example" -Force
}

# Create persistent vector-store directory.
New-Item -ItemType Directory -Force -Path "$projectRoot\processed\vectorstore" | Out-Null

Write-Host ""
Write-Host "DONE." -ForegroundColor Green
Write-Host "Old vehicle model layer removed." -ForegroundColor Green
Write-Host "New backend/llm and backend/embedding installed." -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: your existing .env was NOT modified." -ForegroundColor Yellow
Write-Host "Set GROQ_API_KEY in .env if needed." -ForegroundColor Yellow
Write-Host ""
Write-Host "Next: run the ingestion/indexing test before connecting the frontend." -ForegroundColor Cyan
