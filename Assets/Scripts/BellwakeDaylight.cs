using UnityEngine;

namespace Wizzard
{
    public sealed class BellwakeDaylight : MonoBehaviour
    {
        BellwakeSatchel clock;
        Color daylightFog;
        public Color Horizon => daylightFog;
        float next;
        public void Bind(BellwakeSatchel value) { clock=value; }
        public void SetHorizon(Color color) { daylightFog=color; Apply(); }
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
            float arc=(clock.minutes/1440f-.25f)*2*Mathf.PI;
            float sunHeight=Mathf.Sin(arc);
            float day=Mathf.SmoothStep(0,1,Mathf.InverseLerp(-.25f,.32f,sunHeight));
            float sunset=1-Mathf.Clamp01(Mathf.Abs(sunHeight)*4);
            Shader.SetGlobalFloat("_BellwakeNight",1-day);
            var sun=RenderSettings.sun;
            if(sun!=null)
            {
                sun.transform.rotation=Quaternion.Euler(18+Mathf.Max(0,sunHeight)*48,clock.minutes*.25f-100,0);
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
        void OnDestroy(){Shader.SetGlobalFloat("_BellwakeNight",0);}
    }
}
