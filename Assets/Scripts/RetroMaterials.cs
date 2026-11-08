using System.Collections.Generic;
using UnityEngine;

namespace Wizzard
{
    // Independent palettes: a shared retro finish does not force props to use grass.
    public static class RetroMaterials
    {
        public static readonly string[] Names={"Grass","Bark","Stone","Leaves","Fur","Skin","HousePlaster","RoofTiles","Wood","Masonry","RoofSlate","EarthCliff","Brick","DirtPath","WindowLight","Feathers","Comb","SailCloth"};
        static readonly Dictionary<string,Material> cache=new Dictionary<string,Material>();
        static readonly Color[] dark={new Color(.09f,.13f,.035f),new Color(.12f,.10f,.055f),new Color(.18f,.19f,.13f),new Color(.12f,.32f,.035f),new Color(.19f,.10f,.045f),new Color(.35f,.23f,.12f),new Color(.40f,.36f,.25f),new Color(.19f,.105f,.075f),new Color(.18f,.105f,.045f),new Color(.20f,.22f,.16f),new Color(.12f,.14f,.22f),new Color(.24f,.20f,.12f),new Color(.25f,.10f,.065f),new Color(.27f,.18f,.085f),new Color(.7f,.3f,.015f),new Color(.55f,.53f,.42f),new Color(.42f,.035f,.015f),new Color(.4f,.34f,.21f)};
        static readonly Color[] light={new Color(.43f,.45f,.14f),new Color(.39f,.36f,.23f),new Color(.49f,.48f,.34f),new Color(.42f,.67f,.15f),new Color(.43f,.27f,.13f),new Color(.65f,.47f,.25f),new Color(.73f,.67f,.47f),new Color(.49f,.27f,.16f),new Color(.48f,.32f,.14f),new Color(.54f,.55f,.40f),new Color(.34f,.36f,.46f),new Color(.61f,.52f,.32f),new Color(.57f,.29f,.18f),new Color(.57f,.44f,.23f),new Color(1,.75f,.12f),new Color(.9f,.87f,.73f),new Color(.75f,.1f,.025f),new Color(.79f,.71f,.5f)};
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
            var artwork=Resources.Load<Texture2D>("VillageTextures/"+kind);
            if(artwork!=null) return artwork;
            int id=System.Array.IndexOf(Names,kind); if(id<0) id=0;
            var tex=new Texture2D(64,64,TextureFormat.RGB24,true) {name=kind+"64",filterMode=FilterMode.Bilinear,wrapMode=TextureWrapMode.Repeat,anisoLevel=0};
            var rng=new System.Random(197+id);
            for(int y=0;y<64;y++) for(int x=0;x<64;x++)
            {
                float u=x/64f,v=y/64f;
                float t=.5f+Noise(u,v,id)+(float)(rng.NextDouble()-.5)*.22f;
                // Irregular patches at two scales restore visible texture without wave bands.
                if(kind=="Leaves") t=.1f+.7f*SoftMottle(u,v)
                    +.18f*SoftMottle(u*2+.31f,v*2+.17f)+(float)(rng.NextDouble()-.5)*.04f;
                if(kind=="Bark") t=.4f+SoftMottle(u,v)*.2f;
                if(kind=="Wood" || kind=="Fur") t+=.18f*Mathf.Sin(u*100.53096f+Mathf.Sin(v*6.283185f));
                if((kind=="RoofTiles" || kind=="RoofSlate") && (y%16<2 || (x+(y/16%2)*8)%16<2)) t=.06f;
                if(kind=="Masonry" || kind=="Brick")
                {
                    int row=y/12, column=(x+(row%2)*8)/16;
                    t=.3f+Cell(column,row)*.5f+(float)(rng.NextDouble()-.5)*.12f;
                    if(y%12<2 || (x+(row%2)*8)%16<2) t=.04f;
                }
                if(kind=="EarthCliff") t=.35f+.5f*SoftMottle(u,v)+(float)(rng.NextDouble()-.5)*.18f;
                tex.SetPixel(x,y,Color.Lerp(dark[id],light[id],(kind=="Leaves" || kind=="Bark")?t:Mathf.Round(Mathf.Clamp01(t)*15)/15));
            }
            tex.Apply(); return tex;
        }
        public static Material Get(string kind)
        {
            if(cache.TryGetValue(kind,out var existing) && existing!=null) return existing;
            var material=new Material(Shader.Find("Wizzard/RetroGrass")) {name="Retro "+kind,mainTexture=Texture(kind)};
            material.SetFloat("_TileScale",kind=="Grass" || kind=="EarthCliff" || kind=="RoofTiles"?.25f:kind=="HousePlaster" || kind=="DirtPath"?.2f:kind=="Leaves"?.45f:kind=="Bark"?.65f:.5f);
            material.SetFloat("_ShadeStrength",kind=="WindowLight"?0:kind=="Leaves"?.22f:.35f);
            cache[kind]=material; return material;
        }
    }
}
