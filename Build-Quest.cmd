@echo off
setlocal
cd /d "%~dp0"
if not defined UNITY_EDITOR set "UNITY_EDITOR=%ProgramFiles%\Unity\Hub\Editor\2022.3.20f1\Editor\Unity.exe"
if not exist "%UNITY_EDITOR%" (
  echo Install Unity 2022.3.20f1 with Android Build Support or set UNITY_EDITOR to its Unity.exe.
  exit /b 1
)
if not exist Builds mkdir Builds
"%UNITY_EDITOR%" -batchmode -nographics -quit -projectPath "%CD%" -buildTarget Android -executeMethod Wizzard.Editor.VRProjectSetup.BuildQuest -logFile "%CD%\Builds\Quest-build.log"
if errorlevel 1 (
  type "%CD%\Builds\Quest-build.log"
  exit /b 1
)
if not exist "%CD%\Wizzard-Bellwake-Quest.apk" exit /b 1
echo Native Unity APK ready at "%CD%\Wizzard-Bellwake-Quest.apk"
