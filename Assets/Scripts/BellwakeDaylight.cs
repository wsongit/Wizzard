using UnityEngine;
using System.Collections.Generic;

namespace Wizzard
{
    public sealed class BellwakeDaylight : MonoBehaviour
    {
        BellwakeSatchel clock;
        Color daylightFog;
        public Color Horizon => daylightFog;
        float next;
        bool outdoor=true;
        [System.Serializable]
        sealed class OutdoorSkies
        {
            public string[] valleys, woods, shores, marshes;
        }
        static HashSet<string> skies;
        public static bool IsOutdoor(Cubemap panorama)
        {
            if (!panorama) return false;
            if (skies==null)
            {
                var config=Resources.Load<TextAsset>("Bellwake/OutdoorSkies");
                var profile=JsonUtility.FromJson<OutdoorSkies>(config.text);
                skies=new HashSet<string>(profile.valleys);
                skies.UnionWith(profile.woods);skies.UnionWith(profile.shores);skies.UnionWith(profile.marshes);
            }
            return skies.Contains(panorama.name);
        }
        public float Night { get; private set; }
        public static void SetPanorama(Material material,Cubemap sky)
        {
            material.SetTexture("_Panorama",sky);
            bool outside=IsOutdoor(sky);
            if(outside)material.EnableKeyword("BELLWAKE_OUTDOOR_SKY");
            else material.DisableKeyword("BELLWAKE_OUTDOOR_SKY");
            // The star chart belongs to the sky material for this journey. Changing districts
            // releases their panoramas without loading the same small chart at each gate.
            if(outside && !material.GetTexture("_Stars"))
                material.SetTexture("_Stars",Resources.Load<Cubemap>("Bellwake/Skies/HillStars"));
        }
        public static Vector3 SetSkyClock(float minutes)
        {
            float arc=(minutes/1440f-.25f)*2*Mathf.PI;
            float cross=Mathf.Cos(arc);
            var solar=new Vector3(.85f*cross,Mathf.Sin(arc),.527f*cross).normalized;
            Shader.SetGlobalVector("_BellwakeSunDir",solar);
            return solar;
        }
        public void Bind(BellwakeSatchel value) { clock=value; }
        public void SetHorizon(Color color,bool outside=true) { daylightFog=color; outdoor=outside; Apply(); }
        void Update()
        {
            if(clock==null || !Application.isFocused)return;
            // A complete day takes 16 active minutes. Keep the clock with this save file.
            clock.minutes=Mathf.Repeat(clock.minutes+Time.deltaTime*1.5f,1440);
            if(Time.time<next)return;
            next=Time.time+.25f;Apply();
        }
        void Apply()
        {
            if(clock==null)return;
            Vector3 solar=SetSkyClock(clock.minutes);
            float sunHeight=solar.y;
            float day=outdoor ? Mathf.SmoothStep(0,1,Mathf.InverseLerp(-.25f,.32f,sunHeight)) : 1;
            float sunset=outdoor ? 1-Mathf.Clamp01(Mathf.Abs(sunHeight)*4) : 0;
            Night=1-day;
            Shader.SetGlobalFloat("_BellwakeNight",Night);
            Shader.SetGlobalFloat("_BellwakeDusk",sunset);
            var sun=RenderSettings.sun;
            if(sun!=null)
            {
                float side=day*2-1;
                Vector3 direct=new Vector3(solar.x*side,Mathf.Max(.24f,Mathf.Abs(sunHeight)),solar.z*side);
                sun.transform.rotation=outdoor ? Quaternion.LookRotation(-direct,Vector3.forward) : Quaternion.Euler(51,-33,0);
                sun.color=Color.Lerp(new Color(.98f,.97f,.87f),new Color(1,.68f,.42f),sunset);
                sun.intensity=Mathf.Lerp(.30f,1.08f,day);
            }
            var glow=Color.Lerp(daylightFog,new Color(.72f,.48f,.39f),sunset*.42f);
            RenderSettings.fogColor=Color.Lerp(new Color(.075f,.11f,.19f),glow,day);
            RenderSettings.ambientLight=Color.Lerp(new Color(.19f,.24f,.34f),new Color(.65f,.69f,.52f),day);
            var view=Camera.main;
            if(view!=null && view.clearFlags==CameraClearFlags.SolidColor)
                view.backgroundColor=RenderSettings.fogColor;
        }
        void OnDestroy(){Shader.SetGlobalFloat("_BellwakeNight",0);Shader.SetGlobalFloat("_BellwakeDusk",0);}
    }
}
