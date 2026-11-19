using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.XR;
using XRUsage = UnityEngine.XR.CommonUsages;

namespace Wizzard
{
    public sealed class BellwakeTrade : MonoBehaviour
    {
        static readonly string[] Grounds={"Bellmarket","RootChoir","Reedwater","Highroad","PaperCourt","DriftFen"};
        static readonly string[] Models={"TollSword","FerryShield","ReedStaff","MarketPear"};
        GorillaPlayer player;
        BellwakeSatchel bag;
        Action save;
        Action<string,string> say;
        Action<TextMesh> face;
        GameObject stall, foe;
        readonly GameObject[] held=new GameObject[4];
        TextMesh board;
        MeshCollider land;
        Vector3 burrow, lastHand;
        int district, shelf, life;
        float nextBite, nextSwing, swingUntil, startledUntil;
        bool buyHeld, cycleHeld, wasNear, hadHand;
        Quaternion shieldRest, creatureRest;
        Transform creaturePart;
        public void Initialize(GorillaPlayer rig, BellwakeSatchel contents, Action write,
            Action<string,string> message, Action<TextMesh> faceLabel)
        {
            player=rig;bag=contents;save=write;say=message;face=faceLabel;
            for(int i=0;i<held.Length;i++)
            {
                held[i]=BellwakeModels.Wayfarer(Models[i],i==1?rig.leftHand:rig.rightHand);
                var t=held[i].transform;
                t.localPosition=i==1?new Vector3(-.04f,.05f,.055f):new Vector3(.02f,.03f,.09f);
                t.localRotation=i==1?Quaternion.Euler(0,15,0):Quaternion.Euler(62,0,0);
            }
            shieldRest=held[1].transform.localRotation;
            ShowGear();
        }
        public void Bind(BellwakeSatchel contents)
        {
            if (bag == contents) return;
            bag=contents; ShowGear();
        }
        void ShowGear()
        {
            held[0].SetActive(bag.sword && bag.equipped==1);
            held[1].SetActive(bag.shield);
            held[2].SetActive(bag.staff && bag.equipped==2);
            held[3].SetActive(bag.pears>0 && bag.equipped==3);
        }
        public void Leave()
        {
            if(stall)Destroy(stall);
            if(foe)Destroy(foe);
            if(board)Destroy(board.gameObject);
            creaturePart=null;stall=null;foe=null;board=null;land=null;wasNear=false;hadHand=false;
        }
        public void Arrive(string room, GameObject world, Vector3 arrival, Transform terrain,
                           Func<Transform,string,TextMesh> label, IEnumerable<Transform> markers)
        {
            Leave();district=Array.IndexOf(Grounds,room);
            if(district<0)return;
            land=terrain.GetComponent<MeshCollider>();
            if(!land)return;
            var avoid=new List<Vector3>{arrival};
            foreach(var marker in markers)
                if(marker.name.StartsWith("A_",StringComparison.Ordinal)||marker.name.StartsWith("Road",StringComparison.Ordinal))
                    avoid.Add(marker.position);
            bool shop=room=="Bellmarket"||room=="Reedwater";
            if(shop && FindSite(arrival,avoid,2.1f,4,out var site))
            {
                stall=BellwakeModels.Wayfarer("Waystall",world.transform);
                stall.transform.position=site;
                stall.transform.rotation=Quaternion.LookRotation(Vector3.ProjectOnPlane(arrival-site,Vector3.up));
                avoid.Add(site);
                var blocker=stall.AddComponent<BoxCollider>();
                blocker.center=new Vector3(0,.41f,0);blocker.size=new Vector3(2.05f,.82f,1.03f);
                stall.layer=MeadowWorld.GroundLayer;
                for(int i=0;i<4;i++)
                {
                    var prop=BellwakeModels.Wayfarer(Models[i],stall.transform).transform;
                    prop.localScale=Vector3.one*(i==3?1:.51f);
                    prop.localPosition=new Vector3((i-1.5f)*.31f,.843f,.01f);
                    if(i!=3) prop.localRotation=Quaternion.Euler(85,0,0);
                    float bottom=float.PositiveInfinity;
                    foreach(var part in prop.GetComponentsInChildren<Renderer>())
                        bottom=Mathf.Min(bottom,part.bounds.min.y);
                    prop.position+=Vector3.up*(site.y+.82f-bottom);
                }
                board=label(stall.transform,""); board.transform.position=site+Vector3.up*1.36f;
                board.gameObject.SetActive(true);UpdateBoard(false);
            }
            if((bag.cleared&(1<<district))!=0 || !FindSite(arrival,avoid,.52f,8,out burrow))return;
            foe=BellwakeModels.Wayfarer(district%2==0?"RillBeetle":"MireSkipper",world.transform);
            string movingPart=district%2==0?"Shell":"Broad jaw";
            foreach(var part in foe.GetComponentsInChildren<Transform>())
                if(part.name==movingPart){creaturePart=part;creatureRest=part.localRotation;break;}
            foe.transform.position=burrow;life=district%2==0?2:3;
            nextBite=Time.time+2;
        }
        bool Floor(Vector3 p,out Vector3 position)
        {
            var b=land.bounds;
            if(land.Raycast(new Ray(new Vector3(p.x,b.max.y+1,p.z),Vector3.down),out var hit,b.size.y+2)
                && hit.normal.y>.9f){position=hit.point;return true;}
            position=default;return false;
        }
        bool FindSite(Vector3 origin,List<Vector3> avoid,float width,int start,out Vector3 site)
        {
            // Check the corners and centre against the final imported floor. Four inset feet bridge small changes in grade.
            for(int ring=0;ring<5;ring++)
            for(int i=0;i<20;i++)
            {
                float angle=(i+.25f*ring)*Mathf.PI/10;
                var proposed=origin+new Vector3(Mathf.Cos(angle),0,Mathf.Sin(angle))*(start+ring*1.4f);
                if(!Floor(proposed,out site))continue;
                bool clear=true;
                foreach(var marker in avoid) if(Vector3.Distance(marker,site)<width+2.3f){clear=false;break;}
                if(!clear)continue;
                foreach(int x in Signs)
                foreach(int z in Signs)
                {
                    if(!Floor(site+new Vector3(x,0,z)*width,out var edge) || Mathf.Abs(edge.y-site.y)>.21f)clear=false;
                }
                if(!clear)continue;
                foreach(var hit in Physics.OverlapBox(site+Vector3.up*1.14f,new Vector3(width,.85f,width),
                    Quaternion.identity,player.surfaces,QueryTriggerInteraction.Ignore))
                    if(hit!=land){clear=false;break;}
                if(clear)return true;
            }
            site=default;return false;
        }
        static readonly int[] Signs={-1,1};
        void UpdateBoard(bool near)
        {
            board.text=near?BellwakeSatchel.Goods[shelf]+"   "+BellwakeSatchel.Prices[shelf]+" marks\nY / R: browse    B / F: buy\nPurse: "+bag.coins:
                (district==0?"Tavi’s provisions":"Lockside exchange");
        }
        static bool Down(XRNode hand,InputFeatureUsage<bool> control)
        {
            return InputDevices.GetDeviceAtXRNode(hand).TryGetFeatureValue(control,out var down)&&down;
        }
        void Update()
        {
            if(!player || bag==null)return;
            bool b=Down(XRNode.RightHand,XRUsage.secondaryButton);
            bool y=Down(XRNode.LeftHand,XRUsage.secondaryButton);
            var k=Keyboard.current;
            bool use=(b&&!buyHeld)||(k!=null&&k.fKey.wasPressedThisFrame);
            bool next=(y&&!cycleHeld)||(k!=null&&k.rKey.wasPressedThisFrame);
            buyHeld=b;cycleHeld=y;
            if(player.MovementLocked){hadHand=false;return;}
            bool tracked=player.PalmTracked(1);
            Vector3 hand=player.rightHand.position;
            bool stroke=tracked && hadHand && (hand-lastHand).magnitude/Mathf.Max(.001f,Time.deltaTime)>1.65f;
            lastHand=hand;hadHand=tracked;
            bool raised=Down(XRNode.LeftHand,XRUsage.gripButton)||(k!=null&&k.leftShiftKey.isPressed);
            if(bag.shield)held[1].transform.localRotation=shieldRest*Quaternion.Euler(raised?-45:0,0,0);
            bool near=stall && Vector3.Distance(player.head.position,stall.transform.position+Vector3.up)<2.8f;
            if(board){face(board);if(near!=wasNear)UpdateBoard(near);}
            wasNear=near;
            if(near)
            {
                if(next){shelf=(shelf+1)%4;UpdateBoard(true);}
                if(use){string result=bag.Buy(shelf);ShowGear();save();UpdateBoard(true);say("Provisions",result+"   "+bag.coins+" marks left.");}
            }
            else if(next)
            {
                bag.Cycle();ShowGear();save();
                say("Satchel",new[]{"Empty palm","Toll sword","Reed staff","Honey pear"}[bag.equipped]+".   "+bag.coins+" marks • "+bag.hearts+"/3 hearts • "+bag.pears+" pears.");
            }
            else if(use && bag.equipped==3)
            {
                bool healed=bag.Eat();ShowGear();save();say("Honey pear",healed?"One heart restored.":"Your hearts are full.");
            }
            bool strike=!near && (bag.equipped==1||bag.equipped==2) && (use||stroke) && Time.time>=nextSwing;
            if(strike){swingUntil=Time.time+.28f;nextSwing=Time.time+.52f;}
            if(bag.equipped==1||bag.equipped==2)
                held[bag.equipped==1?0:2].transform.localRotation=Quaternion.Euler(62,0,Mathf.Sin(Mathf.Clamp01((swingUntil-Time.time)/.28f)*Mathf.PI)*55);
            if(!foe)return;
            var t=foe.transform;
            Vector3 body=player.head.position;
            body.y=player.transform.position.y;
            Vector3 toward=Vector3.ProjectOnPlane(body-t.position,Vector3.up);
            float range=toward.magnitude;
            if(strike && range<(bag.equipped==2?2.35f:1.65f) && Mathf.Abs(t.position.y-body.y)<1.45f &&
                Vector3.Dot(Vector3.ProjectOnPlane(player.head.forward,Vector3.up).normalized,toward.normalized)<-.12f &&
                !Physics.Linecast(hand,t.position+Vector3.up*.20f,player.surfaces,QueryTriggerInteraction.Ignore))
            {
                startledUntil=Time.time+.55f;
                if(--life<=0){int old=bag.coins;bag.Reward(district);save();Destroy(foe);foe=null;
                    say("Ferry marks","Recovered "+(bag.coins-old)+" marks. Your purse holds "+bag.coins+".");return;}
            }
            Vector3 target=range<5.5f && Vector3.Distance(body,burrow)<8?body:
                burrow+new Vector3(Mathf.Cos(Time.time*.56f),0,Mathf.Sin(Time.time*.56f))*.82f;
            if(Time.time<startledUntil)target=t.position-toward.normalized;
            Vector3 delta=Vector3.ProjectOnPlane(target-t.position,Vector3.up);
            if(delta.sqrMagnitude>.015f)
            {
                Vector3 dir=delta.normalized;
                float step=Mathf.Min(delta.magnitude,Time.deltaTime*(district%2==0?.75f:1.15f));
                if(Floor(t.position+dir*step,out var at) && Mathf.Abs(at.y-t.position.y)<.24f &&
                    !Physics.SphereCast(t.position+Vector3.up*.28f,.20f,dir,out _,step+.09f,player.surfaces,QueryTriggerInteraction.Ignore))
                    t.position=at;
                t.rotation=Quaternion.LookRotation(dir);
                if(creaturePart)creaturePart.localRotation=creatureRest*Quaternion.Euler(Mathf.Sin(Time.time*10)*6,0,0);
            }
            if(range>.78f || Mathf.Abs(body.y-t.position.y)>1.2f || Time.time<nextBite || Time.time<startledUntil)return;
            if(Physics.Linecast(t.position+Vector3.up*.25f,body+Vector3.up*.55f,player.surfaces,QueryTriggerInteraction.Ignore))return;
            nextBite=Time.time+2.4f;
            if(raised && bag.shield){startledUntil=Time.time+.9f;say("Ferry shield","The shell rings against the boss.");return;}
            if(--bag.hearts<=0){bag.hearts=3;t.position=burrow;player.ResetPlayer();nextBite=Time.time+4;say("Bellrunner","Pip brings you back to the trail.");}
            else say("Shell bite",bag.hearts+"/3 hearts. A pear restores one. Hold left grip or Shift to guard with a shield.");
            save();
        }
    }
}
