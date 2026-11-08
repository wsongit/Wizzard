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
            new GameObject("2048m rolling meadow").AddComponent<MeadowWorld>();
            Physics.SyncTransforms();
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
            var body=Visual("Gorilla torso",rig.transform,new Vector3(.48f,.58f,.28f),fur);
            var torso=Resources.Load<GameObject>("GorillaTorso");
            if(torso!=null) { Destroy(body); body=Instantiate(torso,rig.transform); body.name="Blender gorilla torso"; }
            foreach(var renderer in body.GetComponentsInChildren<Renderer>())
            {
                var materials=renderer.sharedMaterials;
                for(int i=0;i<materials.Length;i++) materials[i]=materials[i]!=null && materials[i].name.Contains("muzzle")?skin:fur;
                renderer.sharedMaterials=materials;
            }
            var left=Visual("Left palm",rig.transform,Vector3.one*.19f,skin);
            var right=Visual("Right palm",rig.transform,Vector3.one*.19f,skin);
            var player=rig.AddComponent<GorillaPlayer>();
            player.head=head.transform; player.body=body.transform; player.leftHand=left.transform; player.rightHand=right.transform;
            gameObject.AddComponent<MossbellVillage>().Initialize(player,GameObject.Find("2048m rolling meadow"));
            // Match controller and headset coordinates to the physical floor.
            var systems=new System.Collections.Generic.List<XRInputSubsystem>();
            SubsystemManager.GetInstances(systems);
            foreach(var system in systems) system.TrySetTrackingOriginMode(TrackingOriginModeFlags.Floor);
        }
        GameObject Visual(string label,Transform parent,Vector3 scale,Material material)
        {
            var obj=GameObject.CreatePrimitive(PrimitiveType.Sphere); obj.name=label;
            obj.transform.SetParent(parent,false); obj.transform.localScale=scale;
            Destroy(obj.GetComponent<Collider>()); obj.GetComponent<Renderer>().sharedMaterial=material;
            return obj;
        }
        void OnGUI()
        {
            if(XRSettings.isDeviceActive) return;
            var player=FindObjectOfType<GorillaPlayer>();
            if(player!=null && player.MovementLocked) return;
            GUI.Box(new Rect(16,16,540,85),"WIZZARD • THE LONG MEADOW\n2 × 2 km • OpenXR • arm-driven movement\nDesktop: WASD / Space • Middle click: look • Esc: release mouse\nV: visit village entrance • Mouse buttons: lower palms. VR: plant palms and push.");
        }
    }
}
