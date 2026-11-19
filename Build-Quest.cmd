@echo off
setlocal
cd /d "%~dp0"
if not defined UNITY_EDITOR set "UNITY_EDITOR=%ProgramFiles%\Unity\Hub\Editor\2022.3.20f1\Editor\Unity.exe"
if not exist "%UNITY_EDITOR%" (
  echo Install Unity 2022.3.20f1 with Android Build Support or set UNITY_EDITOR to its Unity.exe.
  exit /b 1
)
set "BUILD_METHOD=BuildQuest"
set "APK_NAME=Wizzard-Bellwake-Quest.apk"
if /i "%~1"=="profile" (
  set "BUILD_METHOD=BuildQuestProfile"
  set "APK_NAME=Wizzard-Bellwake-Quest-Profile.apk"
)
if not exist Builds mkdir Builds
"%UNITY_EDITOR%" -batchmode -nographics -quit -projectPath "%CD%" -buildTarget Android -executeMethod Wizzard.Editor.VRProjectSetup.%BUILD_METHOD% -logFile "%CD%\Builds\Quest-build.log"
if errorlevel 1 (
  echo Unity build failed. Full log: "%CD%\Builds\Quest-build.log"
  if exist "Builds\Quest-build.log" powershell -NoProfile -Command "$log='Builds/Quest-build.log'; $xr=Select-String -LiteralPath $log -Pattern 'OpenXRProjectValidation[.:]LogBuildValidationIssues' -Context 8,0; $xr | Where-Object { $_.Context.PreContext -match 'Debug[.:]LogError' } | ForEach-Object { $_.Context.PreContext } | Where-Object { $_ -match '\S' -and $_ -notmatch '^\s*(at |UnityEngine[.:]|UnityEditor[.:]|\(Filename:|0x)' } | Select-Object -Unique; Select-String -LiteralPath $log -Pattern 'OpenXR validation failed|error (CS|BC)[0-9]+|shader error|[A-Za-z]*Exception:|^Error:|^FAILURE:|^What went wrong|No valid Unity Editor license|Aborting batchmode' | Select-Object -First 10 | ForEach-Object { $_.Line }"
  exit /b 1
)
if not exist "%CD%\%APK_NAME%" exit /b 1
echo Native Unity APK ready at "%CD%\%APK_NAME%"
