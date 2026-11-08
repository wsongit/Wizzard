using System.Collections.Generic;
using UnityEngine;

namespace Wizzard
{
    // Independent palettes: a shared retro finish does not force props to use grass.
    public static class RetroMaterials
    {
        public static readonly string[] Names={"Grass","Bark","Stone","Leaves","Fur","Skin","HousePlaster","RoofTiles","Wood"};
        static readonly Dictionary<string,Material> cache=new Dictionary<string,Material>();
        static readonly Color[] dark={new Color(.09f,.13f,.035f),new Color(.12f,.10f,.055f),new Color(.18f,.19f,.13f),new Color(.18f,.36f,.065f),new Color(.19f,.10f,.045f),new Color(.35f,.23f,.12f),new Color(.40f,.36f,.25f),new Color(.19f,.105f,.075f),new Color(.18f,.105f,.045f)};
        static readonly Color[] light={new Color(.43f,.45f,.14f),new Color(.39f,.36f,.23f),new Color(.49f,.48f,.34f),new Color(.40f,.62f,.14f),new Color(.43f,.27f,.13f),new Color(.65f,.47f,.25f),new Color(.73f,.67f,.47f),new Color(.49f,.27f,.16f),new Color(.48f,.32f,.14f)};
        static float Noise(float x,float y,int seed)
        {
            // Periodic waves give seamless broad mottling instead of independent pixel confetti.
            return Mathf.Sin(x*6.283185f+seed)*Mathf.Cos(y*12.56637f-seed)*.25f+
                Mathf.Sin((x+y)*25.13274f+seed)*.15f+Mathf.Cos((x*3-y*2)*6.283185f)*.1f;
        }
        static float Cell(int x,int y)
        {
            unchecked
            {
                uint hash=(uint)((x&7)*374761393+(y&7)*668265263);
                hash=(hash^(hash>>13))*1274126177u;
                return (hash^(hash>>16))/4294967295f;
            }
        }
        static float SoftMottle(float u,float v)
        {
            float x=u*8, y=v*8;
            int ix=Mathf.FloorToInt(x), iy=Mathf.FloorToInt(y);
            float sx=Mathf.SmoothStep(0,1,x-ix), sy=Mathf.SmoothStep(0,1,y-iy);
            return Mathf.Lerp(Mathf.Lerp(Cell(ix,iy),Cell(ix+1,iy),sx),
                Mathf.Lerp(Cell(ix,iy+1),Cell(ix+1,iy+1),sx),sy);
        }
        public static Texture2D Texture(string kind)
        {
            int id=System.Array.IndexOf(Names,kind); if(id<0) id=0;
            var tex=new Texture2D(64,64,TextureFormat.RGB24,true) {name=kind+"64",filterMode=FilterMode.Bilinear,wrapMode=TextureWrapMode.Repeat,anisoLevel=0};
            var rng=new System.Random(197+id);
            for(int y=0;y<64;y++) for(int x=0;x<64;x++)
            {
                float u=x/64f,v=y/64f;
                float t=.5f+Noise(u,v,id)+(float)(rng.NextDouble()-.5)*.22f;
                if(kind=="Leaves") t=.4f+SoftMottle(u,v)*.25f;
                if(kind=="Bark") t=.35f+SoftMottle(u,v)*.3f+.04f*Mathf.Sin(u*100.53096f+Mathf.Sin(v*6.283185f));
                if(kind=="Wood" || kind=="Fur") t+=.18f*Mathf.Sin(u*100.53096f+Mathf.Sin(v*6.283185f));
                if(kind=="RoofTiles" && (y%16<2 || (x+(y/16%2)*8)%16<2)) t=.06f;
                tex.SetPixel(x,y,Color.Lerp(dark[id],light[id],Mathf.Round(Mathf.Clamp01(t)*15)/15));
            }
            tex.Apply(); return tex;
        }
        public static Material Get(string kind)
        {
            if(cache.TryGetValue(kind,out var existing) && existing!=null) return existing;
            var material=new Material(Shader.Find("Wizzard/RetroGrass")) {name="Retro "+kind,mainTexture=Texture(kind)};
            material.SetFloat("_TileScale",kind=="Grass"?.25f:kind=="Leaves"?.35f:kind=="Bark"?.65f:1f);
            cache[kind]=material; return material;
        }
    }
}
