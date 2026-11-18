using UnityEngine;
using UnityEngine.XR;

namespace Wizzard
{
    public sealed class MeadowBootstrap : MonoBehaviour
    {
        void Start()
        {
            QualitySettings.vSyncCount=0; Application.targetFrameRate=Application.platform==RuntimePlatform.Android?72:90;
            QualitySettings.shadowDistance=0; QualitySettings.antiAliasing=2;
            RenderSettings.fog=true; RenderSettings.fogMode=FogMode.Linear;
            RenderSettings.fogColor=new Color(.66f,.78f,.75f);
            RenderSettings.fogStartDistance=180; RenderSettings.fogEndDistance=850;
            RenderSettings.ambientLight=new Color(.65f,.69f,.52f);
            var sun=new GameObject("Afternoon sun").AddComponent<Light>();
            sun.type=LightType.Directional; sun.intensity=1.1f;
            sun.transform.rotation=Quaternion.Euler(48,-30,0);
            var rig=new GameObject("Gorilla XR Origin");
            rig.transform.position=new Vector3(0,MeadowWorld.Height(0,0)+.2f,0);
            var motor=rig.AddComponent<CharacterController>();
            motor.radius=.22f; motor.height=1.65f; motor.center=new Vector3(0,.825f,0);
            motor.skinWidth=.02f; motor.stepOffset=.15f; motor.slopeLimit=55;
            var head=new GameObject("Tracked Head"); head.tag="MainCamera";
            head.transform.SetParent(rig.transform,false); head.transform.localPosition=Vector3.up*1.65f;
            var camera=head.AddComponent<Camera>(); camera.nearClipPlane=.06f; camera.farClipPlane=1200;
            camera.clearFlags=CameraClearFlags.SolidColor; camera.backgroundColor=new Color(.56f,.74f,.83f);
            head.AddComponent<AudioListener>();
            var fur=RetroMaterials.Get("Fur");
            var skin=RetroMaterials.Get("Skin");
            var body=Instantiate(Resources.Load<GameObject>("GorillaTorso"),rig.transform);
            body.name="Blender gorilla torso";
            foreach(var renderer in body.GetComponentsInChildren<Renderer>())
            {
                var materials=renderer.sharedMaterials;
                for(int i=0;i<materials.Length;i++) materials[i]=materials[i]!=null && materials[i].name.Contains("muzzle")?skin:fur;
                renderer.sharedMaterials=materials;
            }
            var left=BellwakeModels.Create("LeftPalm",rig.transform);
            var right=BellwakeModels.Create("RightPalm",rig.transform);
            var player=rig.AddComponent<GorillaPlayer>();
            player.head=head.transform; player.body=body.transform; player.leftHand=left.transform; player.rightHand=right.transform;
            gameObject.AddComponent<BellwakeCampaign>().Initialize(player);
            // Match controller and headset coordinates to the physical floor.
            var systems=new System.Collections.Generic.List<XRInputSubsystem>();
            SubsystemManager.GetInstances(systems);
            foreach(var system in systems) system.TrySetTrackingOriginMode(TrackingOriginModeFlags.Floor);
        }
    }
}
