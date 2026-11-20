using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Wizzard
{
    // Pivots and trails are authored in the Blender set, so the animation also tolerates FBX axis conversion.
    public sealed class BellwakeMarketLife : MonoBehaviour
    {
        sealed class Hen
        {
            public Transform body, head, left, right, far;
            public Renderer[] nearRenderers;
            public Renderer farRenderer;
            public Vector3 origin, end, headAxis, leftAxis, rightAxis;
            public Quaternion facing, headRest, leftRest, rightRest;
            public float time, period, legHeight;
        }
        readonly Hen[] birds=new Hen[2];
        Transform mill, listener;
        Quaternion millRest;
        Vector3 axle;
        BellwakeDaylight clock;
        AudioSource bearing, yard, dusk;
        float phase, nextHen, nextTurn;

        public static bool IsMovingPart(string name)
        {
            return name=="MillSails" || name.StartsWith("MarshHen",System.StringComparison.Ordinal)
                || name.StartsWith("ReedHen",System.StringComparison.Ordinal);
        }
        public void Initialize(Dictionary<string,Transform> nodes,BellwakeDaylight daylight,Transform head)
        {
            clock=daylight;listener=head;
            mill=nodes["MillSails"];axle=(nodes["MillAxis"].position-mill.position).normalized;millRest=mill.rotation;
            birds[0]=BindBird(nodes,"MarshHen",0,15);
            birds[1]=BindBird(nodes,"ReedHen",7.7f,19);
            bearing=Voice(mill,.15f,10,48);
            yard=Voice(birds[0].body,.20f,1.8f,13);
            dusk=Voice(nodes["ReedHenTrail"],0,3,20);
            dusk.loop=true;
            StartCoroutine(LoadVoices());
            nextHen=Time.time+2.8f;
        }
        static AudioSource Voice(Transform source,float volume,float near,float far)
        {
            var voice=source.gameObject.AddComponent<AudioSource>();
            voice.playOnAwake=false;voice.spatialBlend=1;voice.dopplerLevel=0;
            voice.minDistance=near;voice.maxDistance=far;voice.volume=volume;
            voice.rolloffMode=AudioRolloffMode.Linear;
            return voice;
        }
        IEnumerator LoadVoices()
        {
            var wheelClip=Resources.LoadAsync<AudioClip>("Bellwake/Audio/MillBearing");
            var henClip=Resources.LoadAsync<AudioClip>("Bellwake/Audio/YardHen");
            var duskClip=Resources.LoadAsync<AudioClip>("Bellwake/Audio/YardDusk");
            yield return wheelClip;bearing.clip=wheelClip.asset as AudioClip;
            yield return henClip;yard.clip=henClip.asset as AudioClip;
            yield return duskClip;dusk.clip=duskClip.asset as AudioClip;
        }
        static Hen BindBird(Dictionary<string,Transform> nodes,string prefix,float at,float period)
        {
            var bird=new Hen { body=nodes[prefix],head=nodes[prefix+"Head"],left=nodes[prefix+"Left"],
                right=nodes[prefix+"Right"],far=nodes[prefix+"Far"],end=nodes[prefix+"Trail"].position,time=at,period=period };
            bird.origin=bird.body.position;bird.facing=bird.body.rotation;
            bird.legHeight=bird.left.position.y-bird.origin.y;
            Vector3 right=Vector3.Cross(Vector3.up,bird.end-bird.origin).normalized;
            foreach(var part in new[]{bird.head,bird.left,bird.right})part.SetParent(bird.body,true);
            bird.nearRenderers=bird.body.GetComponentsInChildren<Renderer>();
            bird.farRenderer=bird.far.GetComponent<Renderer>();
            bird.farRenderer.enabled=false;
            bird.headAxis=Quaternion.Inverse(bird.head.rotation)*right;
            bird.leftAxis=Quaternion.Inverse(bird.left.rotation)*right;
            bird.rightAxis=Quaternion.Inverse(bird.right.rotation)*right;
            bird.headRest=bird.head.localRotation;bird.leftRest=bird.left.localRotation;bird.rightRest=bird.right.localRotation;
            return bird;
        }
        // Rest at either end of the trail to peck and turn before walking back.
        static void Animate(Hen bird,float dt,Vector3 listenerPosition)
        {
            bird.time=Mathf.Repeat(bird.time+dt,bird.period);
            float t=bird.time/bird.period;
            float along=Mathf.SmoothStep(0,1,Mathf.InverseLerp(.13f,.40f,t))
                       -Mathf.SmoothStep(0,1,Mathf.InverseLerp(.64f,.91f,t));
            float turn=180*(Mathf.SmoothStep(0,1,Mathf.InverseLerp(.46f,.61f,t))
                         +Mathf.SmoothStep(0,1,Mathf.InverseLerp(.92f,1,t)));
            var position=Vector3.Lerp(bird.origin,bird.end,along);
            var rotation=Quaternion.AngleAxis(turn,Vector3.up)*bird.facing;
            float limit=bird.farRenderer.enabled ? 12 : 14;
            bool distant=(position-listenerPosition).sqrMagnitude>limit*limit;
            if(distant!=bird.farRenderer.enabled)
            {
                bird.farRenderer.enabled=distant;
                foreach(var part in bird.nearRenderers) part.enabled=!distant;
            }
            if(distant)
            {
                bird.body.SetPositionAndRotation(position,rotation);
                bird.far.SetPositionAndRotation(position,rotation);
                return;
            }
            float walk=(t>.13f && t<.40f) ? (t-.13f)/.27f : (t>.64f && t<.91f) ? (t-.64f)/.27f : 0;
            float gait=Mathf.Sin(walk*8*Mathf.PI)*Mathf.Sin(walk*Mathf.PI);
            float peck=walk>0 ? 3*Mathf.Sin(walk*16*Mathf.PI) : 30*Mathf.Pow(Mathf.Max(0,Mathf.Cos(t*14*Mathf.PI)),4);
            // The forward toe extends 0.62 shank lengths from the hip. Keep that toe on the turf during a stride.
            float angle=Mathf.Abs(24*gait)*Mathf.Deg2Rad;
            float lift=bird.legHeight*(1.025f*(Mathf.Cos(angle)-1)+.62f*Mathf.Sin(angle));
            bird.body.SetPositionAndRotation(position+Vector3.up*lift,rotation);
            bird.head.localRotation=bird.headRest*Quaternion.AngleAxis(peck,bird.headAxis);
            bird.left.localRotation=bird.leftRest*Quaternion.AngleAxis(24*gait,bird.leftAxis);
            bird.right.localRotation=bird.rightRest*Quaternion.AngleAxis(-24*gait,bird.rightAxis);
        }
        void Update()
        {
            phase=Mathf.Repeat(phase+Time.deltaTime*13,360);
            mill.rotation=Quaternion.AngleAxis(phase,axle)*millRest;
            float night=clock.Night;
            foreach(var bird in birds)Animate(bird,Time.deltaTime*Mathf.Lerp(1,.08f,night),listener.position);
            float now=Time.time;
            if(now>=nextTurn)
            {
                if(bearing.clip && (listener.position-mill.position).sqrMagnitude<48*48)bearing.Play();
                nextTurn=now+360f/(4*13f);
            }
            if(now>=nextHen)
            {
                float distance=(listener.position-yard.transform.position).sqrMagnitude;
                if(yard.clip && night<.45f && distance<13*13){yard.pitch=.94f+.14f*Mathf.Sin(now*.89f);yard.Play();}
                nextHen=now+5+3*Mathf.Abs(Mathf.Sin(now*1.26f));
            }
            bool audible=dusk.clip && night>.15f && (listener.position-dusk.transform.position).sqrMagnitude<20*20;
            if(audible){dusk.volume=.065f*night;if(!dusk.isPlaying)dusk.Play();}
            else if(dusk.isPlaying)dusk.Stop();
        }
    }
}
