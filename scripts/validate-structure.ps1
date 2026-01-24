# PowerShell script to validate project structure matches architecture
# Usage: .\scripts\validate-structure.ps1

$Errors = 0

function Check-Dir {
    param([string]$Path)
    if (-not (Test-Path -Path $Path -PathType Container)) {
        Write-Host "❌ Missing directory: $Path" -ForegroundColor Red
        $script:Errors++
    } else {
        Write-Host "✅ Found: $Path" -ForegroundColor Green
    }
}

function Check-File {
    param([string]$Path)
    if (-not (Test-Path -Path $Path -PathType Leaf)) {
        Write-Host "❌ Missing file: $Path" -ForegroundColor Red
        $script:Errors++
    } else {
        Write-Host "✅ Found: $Path" -ForegroundColor Green
    }
}

Write-Host "Validating Project Echo repository structure..." -ForegroundColor Cyan
Write-Host ""

Write-Host "=== Central Repository Structure ===" -ForegroundColor Yellow
Check-Dir "backend"
Check-Dir "backend\src"
Check-Dir "backend\src\routes"
Check-Dir "backend\src\services"
Check-Dir "backend\src\repositories"
Check-Dir "backend\src\models"
Check-Dir "backend\src\schemas"
Check-Dir "backend\src\middleware"
Check-Dir "backend\src\utils"
Check-Dir "backend\tests"
Check-Dir "backend\alembic"

Check-Dir "frontend"
Check-Dir "frontend\src"
Check-Dir "frontend\src\components"
Check-Dir "frontend\src\components\atoms"
Check-Dir "frontend\src\components\molecules"
Check-Dir "frontend\src\components\organisms"
Check-Dir "frontend\src\components\templates"
Check-Dir "frontend\src\pages"
Check-Dir "frontend\src\hooks"
Check-Dir "frontend\src\services"
Check-Dir "frontend\src\stores"
Check-Dir "frontend\src\types"
Check-Dir "frontend\src\utils"
Check-Dir "frontend\src\styles"
Check-Dir "frontend\public"

Check-Dir "shared"
Check-Dir "shared\src"
Check-Dir "shared\src\scraping"
Check-Dir "shared\src\transformation"
Check-Dir "shared\src\publication"
Check-Dir "shared\src\common"

Check-Dir "templates"
Check-Dir "templates\channel-repo-template"
Check-Dir "templates\channel-repo-template\.github\workflows"
Check-Dir "templates\channel-repo-template\config"
Check-Dir "templates\channel-repo-template\scripts"

Check-Dir "docs"
Check-Dir "scripts"
Check-Dir ".github\workflows"

Write-Host ""
Write-Host "=== Required Files ===" -ForegroundColor Yellow
Check-File "README.md"
Check-File ".gitignore"
Check-File ".editorconfig"
Check-File "frontend\package.json"
Check-File "frontend\vite.config.ts"
Check-File "frontend\tsconfig.json"
Check-File "frontend\public\index.html"
Check-File "backend\.env.example"
Check-File "frontend\.env.example"
Check-File "shared\setup.py"
Check-File "templates\channel-repo-template\README.md"
Check-File "templates\channel-repo-template\config\channel.yaml"
Check-File "templates\channel-repo-template\.github\workflows\process-video.yaml"
Check-File "scripts\setup-channel-repo.sh"
Check-File "docs\MULTI-REPO-ARCHITECTURE.md"
Check-File "docs\GIT-WORKFLOW.md"

Write-Host ""
if ($Errors -eq 0) {
    Write-Host "✅ All structure checks passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Found $Errors errors in structure" -ForegroundColor Red
    exit 1
}
