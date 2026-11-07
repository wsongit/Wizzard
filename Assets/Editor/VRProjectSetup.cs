using System;
using System.Linq;
using UnityEditor;
using UnityEditor.XR.Management;
using UnityEditor.XR.Management.Metadata;
using UnityEngine;
using UnityEngine.XR.Management;
using UnityEngine.XR.OpenXR;

namespace Wizzard.Editor
{
    [InitializeOnLoad]
    public static class VRProjectSetup
    {
        static VRProjectSetup() { EditorApplication.delayCall += EnsureConfigured; }
        static void EnsureConfigured()
        {
            if(EditorApplication.isCompiling || EditorApplication.isPlayingOrWillChangePlaymode) return;
            var existing=XRGeneralSettingsPerBuildTarget.XRGeneralSettingsForBuildTarget(BuildTargetGroup.Standalone);
            var android=XRGeneralSettingsPerBuildTarget.XRGeneralSettingsForBuildTarget(BuildTargetGroup.Android);
            if(existing!=null && existing.Manager!=null && existing.Manager.activeLoaders.Any(l=>l is OpenXRLoader) &&
                android!=null && android.Manager!=null && android.Manager.activeLoaders.Any(l=>l is OpenXRLoader)) return;
            Configure();
        }
        [MenuItem("Wizzard/Configure Quest and PC OpenXR")]
        public static void Configure()
        {
            System.IO.Directory.CreateDirectory("Assets/XR"); AssetDatabase.Refresh();
            if(!EditorBuildSettings.TryGetConfigObject(XRGeneralSettings.k_SettingsKey,out XRGeneralSettingsPerBuildTarget targets))
            {
                targets=ScriptableObject.CreateInstance<XRGeneralSettingsPerBuildTarget>();
                AssetDatabase.CreateAsset(targets,"Assets/XR/XRGeneralSettings.asset");
                EditorBuildSettings.AddConfigObject(XRGeneralSettings.k_SettingsKey,targets,true);
            }
            foreach(var group in new[]{BuildTargetGroup.Standalone,BuildTargetGroup.Android})
            {
                if(!targets.HasSettingsForBuildTarget(group)) targets.CreateDefaultSettingsForBuildTarget(group);
                if(!targets.HasManagerSettingsForBuildTarget(group)) targets.CreateDefaultManagerSettingsForBuildTarget(group);
                var settings=targets.SettingsForBuildTarget(group);
                settings.InitManagerOnStart=true;
                if(!XRPackageMetadataStore.AssignLoader(settings.Manager,"UnityEngine.XR.OpenXR.OpenXRLoader",group))
                    throw new Exception("OpenXR loader could not be assigned for "+group);
                var openXR=OpenXRSettings.GetSettingsForBuildTargetGroup(group);
                if(openXR!=null)
                {
                    openXR.renderMode=OpenXRSettings.RenderMode.SinglePassInstanced;
                    foreach(var feature in openXR.GetFeatures<UnityEngine.XR.OpenXR.Features.OpenXRFeature>())
                    {
                        string type=feature.GetType().Name;
                        if(type=="OculusTouchControllerProfile" || type=="KHRSimpleControllerProfile" ||
                            (group==BuildTargetGroup.Android && type=="MetaQuestFeature") ||
                            (group==BuildTargetGroup.Standalone && (type=="ValveIndexControllerProfile" ||
                             type=="HTCViveControllerProfile" || type=="MicrosoftMotionControllerProfile")))
                            feature.enabled=true;
                    }
                    EditorUtility.SetDirty(openXR);
                }
                EditorUtility.SetDirty(settings); EditorUtility.SetDirty(settings.Manager);
            }
            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android,ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion=AndroidSdkVersions.AndroidApiLevel29;
            PlayerSettings.Android.targetSdkVersion=AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android,"com.wizzard.longmeadow");
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android,false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,new[]{UnityEngine.Rendering.GraphicsDeviceType.OpenGLES3});
            PlayerSettings.colorSpace=ColorSpace.Linear;
            var playerSettings=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
            var input=playerSettings.FindProperty("activeInputHandler");
            if(input!=null) { input.intValue=1; playerSettings.ApplyModifiedPropertiesWithoutUndo(); }
            var tags=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
            tags.FindProperty("layers").GetArrayElementAtIndex(MeadowWorld.GroundLayer).stringValue="Climbable";
            tags.ApplyModifiedPropertiesWithoutUndo();
            RetroMaterialLibrary.Create();
            PlayerSettings.companyName="Wizzard"; PlayerSettings.productName="The Long Meadow";
            EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene("Assets/Scenes/Meadow.unity",true)};
            EditorUtility.SetDirty(targets);
            AssetDatabase.SaveAssets(); Debug.Log("Wizzard: Quest ARM64 and PC OpenXR configured. Open Meadow and press Play.");
        }
        [MenuItem("Wizzard/Build Quest APK")]
        public static void BuildQuest()
        {
            if(EditorUserBuildSettings.activeBuildTarget!=BuildTarget.Android)
                throw new Exception("Switch to Android in File > Build Settings first. Android Build Support, SDK, NDK and OpenJDK are required.");
            ValidateProject();
            System.IO.Directory.CreateDirectory("Builds");
            var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes=new[]{"Assets/Scenes/Meadow.unity"}, target=BuildTarget.Android,
                locationPathName="Builds/LongMeadow-Quest.apk", options=BuildOptions.Development });
            if(report.summary.result!=UnityEditor.Build.Reporting.BuildResult.Succeeded)
                throw new Exception("Quest APK build failed: "+report.summary.result);
        }
        [MenuItem("Wizzard/Validate project")]
        public static void ValidateProject()
        {
            Configure();
            if(Shader.Find("Wizzard/RetroGrass")==null) throw new Exception("Grass shader missing");
            if(Resources.Load<GameObject>("GorillaTorso")==null) throw new Exception("Blender torso missing");
            if(float.IsNaN(MeadowWorld.Height(0,0))) throw new Exception("Invalid terrain height");
            Debug.Log("Wizzard project asset/configuration checks passed; headset play testing is still required.");
        }
    }
}
