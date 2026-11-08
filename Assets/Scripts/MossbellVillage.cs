using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;
using UnityEngine.InputSystem;

namespace Wizzard
{
    public sealed class MossbellVillage : MonoBehaviour
    {
        public const string VillageName="Mossbell Village";
        public static readonly Vector2 MapLocation=new Vector2(240,140);
        GorillaPlayer player;
        GameObject meadow, village;
        Material curtain;
        TextMesh title;
        Vector3 gate, arrival, exit;
        bool inside, busy;
        float cooldown;
        public void Initialize(GorillaPlayer rig,GameObject world)
        {
            player=rig; meadow=world;
            gate=new Vector3(MapLocation.x,MeadowWorld.Height(MapLocation.x,MapLocation.y),MapLocation.y-36);
            CreateMountain();
            // Camera-attached geometry renders in both eyes. Text is in front of the curtain.
            var quad=GameObject.CreatePrimitive(PrimitiveType.Quad); quad.name="Village fade curtain";
            Destroy(quad.GetComponent<Collider>()); quad.transform.SetParent(player.head,false);
            quad.transform.localPosition=new Vector3(0,0,.8f); quad.transform.localScale=Vector3.one*20;
            curtain=new Material(Shader.Find("Wizzard/VillageFade"));curtain.color=Color.clear;
            quad.GetComponent<Renderer>().sharedMaterial=curtain;
            var label=new GameObject("Village transition title"); label.transform.SetParent(player.head,false);
            label.transform.localPosition=new Vector3(0,0,.5f);
            title=label.AddComponent<TextMesh>();title.anchor=TextAnchor.MiddleCenter;title.alignment=TextAlignment.Center;
            title.font=Resources.GetBuiltinResource<Font>("Arial.ttf");
            var titleMaterial=new Material(Shader.Find("Wizzard/VillageTitle"));
            title.GetComponent<Renderer>().sharedMaterial=titleMaterial;
            title.fontSize=64;title.characterSize=.05f;title.color=Color.white;label.SetActive(false);
        }
        void Update()
        {
            if(player==null || busy || Time.unscaledTime<cooldown) return;
            if(!inside && !XRSettings.isDeviceActive && Keyboard.current!=null && Keyboard.current.vKey.wasPressedThisFrame)
                player.Teleport(gate+Vector3.back*10,Quaternion.identity);
            Vector3 p=player.head.position;
            Vector3 target=inside?exit:gate;
            if(Mathf.Abs(p.x-target.x)<3 && Mathf.Abs(p.z-target.z)<2 && Mathf.Abs(p.y-target.y)<5)
                StartCoroutine(Transition(!inside));
        }
        IEnumerator Transition(bool entering)
        {
            busy=true;
            bool completed=false;
            try
            {
            player.MovementLocked=true;
            yield return Fade(0,1,.65f);
            title.text=entering?"Entering\n"+VillageName:"Returning to\nThe Long Meadow";
            title.font.RequestCharactersInTexture(title.text,title.fontSize,FontStyle.Normal);
            title.GetComponent<Renderer>().sharedMaterial.mainTexture=title.font.material.mainTexture;
            title.gameObject.SetActive(true);
            title.transform.localScale=Vector3.one;
            // Fit the title to a comfortable, camera-relative rectangle in either eye.
            yield return null;
            var titleBounds=title.GetComponent<Renderer>().localBounds;
            title.transform.localScale=Vector3.one*Mathf.Min(.65f/Mathf.Max(.001f,titleBounds.size.x),.15f/Mathf.Max(.001f,titleBounds.size.y));
            // The expensive instantiate/import work only occurs after a fully black frame.
            yield return null;
            if(entering && village==null) BuildInterior();
            yield return null;
            if(entering)
            {
                village.SetActive(true); meadow.SetActive(false);
                Vector3 direction=arrival-exit;direction.y=0;
                player.Teleport(arrival,Quaternion.LookRotation(direction));
            }
            else
            {
                meadow.SetActive(true);village.SetActive(false);
                player.Teleport(gate+Vector3.back*9,Quaternion.Euler(0,180,0));
            }
            inside=entering;Physics.SyncTransforms();
            yield return new WaitForSecondsRealtime(1.2f);
            title.gameObject.SetActive(false);
            yield return Fade(1,0,.8f);
            completed=true;
            }
            finally
            {
                if(!completed)
                {
                    inside=false;meadow.SetActive(true);if(village!=null) village.SetActive(false);
                    player.Teleport(gate+Vector3.back*9,Quaternion.identity);
                }
                curtain.color=Color.clear;title.gameObject.SetActive(false);
                player.MovementLocked=false;cooldown=Time.unscaledTime+1;busy=false;
            }
        }
        IEnumerator Fade(float from,float to,float duration)
        {
            float elapsed=0;
            while(elapsed<duration)
            {
                elapsed+=Time.unscaledDeltaTime;
                curtain.color=new Color(0,0,0,Mathf.Lerp(from,to,Mathf.Clamp01(elapsed/duration)));
                yield return null;
            }
            curtain.color=new Color(0,0,0,to);
        }
        void BuildInterior()
        {
            village=Instantiate(Resources.Load<GameObject>("Village/Mossbell")); village.name=VillageName;
            var invisible=new Material(Shader.Find("Wizzard/VillageFade"));invisible.color=Color.clear;
            bool hasArrival=false,hasExit=false;
            foreach(var filter in village.GetComponentsInChildren<MeshFilter>())
            {
                filter.gameObject.layer=MeadowWorld.GroundLayer;
                var renderer=filter.GetComponent<MeshRenderer>();var materials=renderer.sharedMaterials;
                var triangles=new List<int>();
                for(int slot=0;slot<materials.Length;slot++)
                {
                    string source=materials[slot]!=null?materials[slot].name:"";
                    bool marker=source.StartsWith("Arrival") || source.StartsWith("Exit");
                    var indices=filter.sharedMesh.GetTriangles(slot);
                    if(marker)
                    {
                        var vertices=filter.sharedMesh.vertices;
                        var bounds=new Bounds(filter.transform.TransformPoint(vertices[indices[0]]),Vector3.zero);
                        foreach(int index in indices) bounds.Encapsulate(filter.transform.TransformPoint(vertices[index]));
                        if(source.StartsWith("Arrival")) { arrival=bounds.center;hasArrival=true; }
                        else { exit=bounds.center;hasExit=true; }
                        materials[slot]=invisible;
                    }
                    else
                    {
                        foreach(string kind in RetroMaterials.Names)
                            if(source.StartsWith(kind)) { materials[slot]=RetroMaterials.Get(kind);break; }
                        triangles.AddRange(indices);
                    }
                }
                renderer.sharedMaterials=materials;
                if(triangles.Count>0)
                {
                    var collision=Instantiate(filter.sharedMesh);collision.subMeshCount=1;collision.triangles=triangles.ToArray();
                    filter.gameObject.AddComponent<MeshCollider>().sharedMesh=collision;
                }
            }
            if(!hasArrival || !hasExit) throw new System.InvalidOperationException("Village marker materials were not imported. Enable material import for Mossbell.obj.");
            // Keep Blender/import coordinate conversion out of arrival/exit calculations.
            MeadowTrees.Create(2,village.transform,new Vector3(-46,0,-25));
            MeadowTrees.Create(4,village.transform,new Vector3(46,0,-15));
            MeadowTrees.Create(1,village.transform,new Vector3(-12,2.05f,38));
            village.SetActive(false);
        }
        void CreateMountain()
        {
            var mountain=new GameObject("Mossbell mountain entrance");mountain.transform.SetParent(meadow.transform);
            mountain.transform.position=new Vector3(MapLocation.x,gate.y,MapLocation.y);
            var vertices=new List<Vector3>();var triangles=new List<int>();
            // Horseshoe mountain: an open southern approach, steep outer slopes and a rocky summit.
            const int segments=30;
            for(int i=0;i<=segments;i++)
            {
                float a=Mathf.Lerp(-65,245,i/(float)segments)*Mathf.Deg2Rad;
                for(int ring=0;ring<3;ring++)
                {
                    float radius=ring==0?46:ring==1?27:15;
                    float height=ring==0?0:ring==1?20+Mathf.Sin(a*5)*3:10;
                    vertices.Add(new Vector3(Mathf.Cos(a)*radius,height,Mathf.Sin(a)*radius));
                }
            }
            for(int i=0;i<segments;i++) for(int r=0;r<2;r++)
            {int k=i*3+r;triangles.AddRange(new[]{k,k+1,k+3,k+1,k+4,k+3});}
            var mesh=new Mesh {vertices=vertices.ToArray(),triangles=triangles.ToArray()};mesh.RecalculateNormals();
            mountain.layer=MeadowWorld.GroundLayer;
            mountain.AddComponent<MeshFilter>().sharedMesh=mesh;mountain.AddComponent<MeshRenderer>().sharedMaterial=RetroMaterials.Get("Stone");
            mountain.AddComponent<MeshCollider>().sharedMesh=mesh;
            for(int sign=-1;sign<=1;sign+=2) Block(mountain.transform,new Vector3(sign*4,2.5f,-36),new Vector3(2,5,3),"Gate pier","Stone");
            Block(mountain.transform,new Vector3(0,5,-36),new Vector3(10,1,3),"Gate lintel","Wood");
            var signObject=new GameObject("Mossbell entrance sign");signObject.transform.SetParent(mountain.transform,false);signObject.transform.localPosition=new Vector3(0,4,-37.6f);
            var text=signObject.AddComponent<TextMesh>();text.text=VillageName;text.anchor=TextAnchor.MiddleCenter;text.fontSize=48;text.characterSize=.09f;text.color=Color.white;
        }
        static void Block(Transform parent,Vector3 pos,Vector3 scale,string name,string kind)
        {
            var obj=GameObject.CreatePrimitive(PrimitiveType.Cube);obj.name=name;obj.layer=MeadowWorld.GroundLayer;
            obj.transform.SetParent(parent,false);obj.transform.localPosition=pos;obj.transform.localScale=scale;
            obj.GetComponent<Renderer>().sharedMaterial=RetroMaterials.Get(kind);
        }
    }
}
