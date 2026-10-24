# Деплой витрины на сервер. Запуск из корня проекта в PowerShell:
#   .\deploy\deploy.ps1
# Нужны: Node.js (npm) и OpenSSH-клиент (есть в Windows 10/11).

$ErrorActionPreference = 'Stop'

$Server = 'mylab@myfreelab.ru'
$Target = '/var/www/myfreelab.ru'
$Tmp    = '~/site-upload'

Write-Host '1/4  Сборка проекта...' -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { throw 'Сборка не удалась' }

Write-Host '2/4  Готовлю временную папку на сервере...' -ForegroundColor Cyan
ssh $Server "rm -rf $Tmp && mkdir -p $Tmp"
if ($LASTEXITCODE -ne 0) { throw 'Не удалось подключиться к серверу' }

Write-Host '3/4  Загружаю файлы...' -ForegroundColor Cyan
scp -r -q .\dist\* "${Server}:$Tmp/"
if ($LASTEXITCODE -ne 0) { throw 'Не удалось загрузить файлы' }

Write-Host '4/4  Публикую...' -ForegroundColor Cyan
# rsync --delete убирает старые файлы сборки, которых больше нет в dist
ssh $Server "rsync -a --delete $Tmp/ $Target/ && rm -rf $Tmp"
if ($LASTEXITCODE -ne 0) { throw 'Не удалось опубликовать' }

Write-Host 'Готово: https://myfreelab.ru' -ForegroundColor Green
