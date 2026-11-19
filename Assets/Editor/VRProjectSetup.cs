using System;
using System.Linq;
using System.IO;
using System.IO.Compression;
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
                UnityEditor.XR.OpenXR.Features.FeatureHelpers.RefreshFeatures(group);
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
                    if (group == BuildTargetGroup.Android)
                    {
                        var features = openXR.GetFeatures<UnityEngine.XR.OpenXR.Features.OpenXRFeature>();
                        foreach (string required in new[] { "MetaQuestFeature", "OculusTouchControllerProfile" })
                            if (!features.Any(f => f != null && f.enabled && f.GetType().Name == required))
                                throw new InvalidOperationException("Missing Android OpenXR feature " + required);
                    }
                    EditorUtility.SetDirty(openXR);
                }
                else throw new InvalidOperationException("Missing OpenXR settings for " + group);
                EditorUtility.SetDirty(settings); EditorUtility.SetDirty(settings.Manager);
            }
            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android,ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion=AndroidSdkVersions.AndroidApiLevel29;
            PlayerSettings.Android.targetSdkVersion=AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android,"com.wizzard.longmeadow");
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android,false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,new[]{UnityEngine.Rendering.GraphicsDeviceType.OpenGLES3});
            PlayerSettings.bakeCollisionMeshes=true;
            PlayerSettings.colorSpace=ColorSpace.Linear;
            var playerSettings=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
            var input=playerSettings.FindProperty("activeInputHandler");
            if(input!=null) { input.intValue=1; playerSettings.ApplyModifiedPropertiesWithoutUndo(); }
            var tags=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
            tags.FindProperty("layers").GetArrayElementAtIndex(MeadowWorld.GroundLayer).stringValue="Climbable";
            tags.ApplyModifiedPropertiesWithoutUndo();
            RetroMaterialLibrary.Create();
            PlayerSettings.companyName="Wizzard"; PlayerSettings.productName="Wizzard Bellwake";
            EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene("Assets/Scenes/Meadow.unity",true)};
            EditorUtility.SetDirty(targets);
            AssetDatabase.SaveAssets(); Debug.Log("Wizzard: Quest ARM64 and PC OpenXR configured. Open Meadow and press Play.");
        }
        [MenuItem("Wizzard/Play Bellwake")]
        public static void PlayBellwake()
        {
            if(EditorApplication.isPlayingOrWillChangePlaymode) return;
            if(!UnityEditor.SceneManagement.EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            UnityEditor.SceneManagement.EditorSceneManager.OpenScene("Assets/Scenes/Meadow.unity");
            EditorApplication.isPlaying=true;
        }
        [MenuItem("Wizzard/Build Quest APK")]
        public static void BuildQuest()
        {
            if(!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Android,BuildTarget.Android))
                throw new Exception("Install Android Build Support for this Unity Editor.");
            if(EditorUserBuildSettings.activeBuildTarget!=BuildTarget.Android)
                throw new Exception("Switch to Android in File > Build Settings first. Android Build Support, SDK, NDK and OpenJDK are required.");
            ValidateProject();
            Directory.CreateDirectory("Builds");
            const string path = "Builds/Wizzard-Bellwake-Quest.apk";
            var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes=new[]{"Assets/Scenes/Meadow.unity"}, target=BuildTarget.Android,
                locationPathName=path, options=BuildOptions.None });
            if(report.summary.result!=UnityEditor.Build.Reporting.BuildResult.Succeeded)
                throw new Exception("Quest APK build failed: "+report.summary.result);
            using(var input=File.OpenRead(path))
            using(var package=new ZipArchive(input,ZipArchiveMode.Read))
            {
                foreach(string entry in new[]{"lib/arm64-v8a/libunity.so","lib/arm64-v8a/libil2cpp.so",
                                              "assets/bin/Data/boot.config","lib/arm64-v8a/libUnityOpenXR.so",
                                              "lib/arm64-v8a/libopenxr_loader.so"})
                    if(package.GetEntry(entry)==null) throw new InvalidDataException("Native player missing "+entry);
                if(package.GetEntry("assets/index.html")!=null) throw new InvalidDataException("Unexpected web launcher");
            }
            File.Copy(path,"Wizzard-Bellwake-Quest.apk",true);
            Debug.Log("Native Unity Quest build: "+Path.GetFullPath("Wizzard-Bellwake-Quest.apk"));
        }
        [MenuItem("Wizzard/Validate project")]
        public static void ValidateProject()
        {
            Configure();
            BellwakeValidation.Validate();
            var village=Resources.Load<GameObject>("Village/Mossbell");
            if(village==null) throw new Exception("Mossbell village model missing");
            bool arrival=false,exit=false,collision=false;
            foreach(var filter in village.GetComponentsInChildren<MeshFilter>())
                {
                    if(!filter.sharedMesh.isReadable) throw new Exception("Reimport Mossbell.obj: village meshes must be readable on device");
                    if(filter.sharedMesh.uv.Length!=filter.sharedMesh.vertexCount) throw new Exception("Village metric UVs missing");
                }
            foreach(var renderer in village.GetComponentsInChildren<MeshRenderer>())
                foreach(var material in renderer.sharedMaterials)
                    if(material!=null) { arrival|=material.name.StartsWith("Arrival");exit|=material.name.StartsWith("Exit");collision|=material.name.StartsWith("Collision"); }
            if(!collision) throw new Exception("Village collision material missing");
            if(!arrival || !exit) throw new Exception("Village arrival/exit marker material slots missing");
            if(Shader.Find("Wizzard/VillageFade")==null || Shader.Find("Wizzard/VillageTitle")==null || Shader.Find("Wizzard/VillageSky")==null)
                throw new Exception("Village transition shaders missing");
            foreach(string name in new[]{"HousePlaster","RoofTiles","Masonry","Wood","Grass","Leaves","DirtPath","WindowDark","SailCloth","PathBlend","EarthCliff","Mountain"})
            {
                var texture=Resources.Load<Texture2D>("VillageTextures/"+name);
                if(texture==null || texture.width!=64 || texture.height!=64)
                    throw new Exception("Missing or incorrectly sized village texture: "+name);
            }
            if(Shader.Find("Wizzard/VillageSurface")==null) throw new Exception("Village UV shader missing");
            if(Shader.Find("Wizzard/RetroGrass")==null) throw new Exception("Grass shader missing");
            if(Resources.Load<GameObject>("GorillaTorso")==null) throw new Exception("Blender torso missing");
            for(int i=1;i<=8;i++)
                if(Resources.Load<GameObject>($"Trees/Tree{i:00}")==null) throw new Exception($"Tree model {i} missing");
            if(float.IsNaN(MeadowWorld.Height(0,0))) throw new Exception("Invalid terrain height");
            Debug.Log("Wizzard project asset/configuration checks passed; headset play testing is still required.");
        }
    }
}
