using System.Collections.Generic;
using UnityEngine;

namespace Wizzard
{
    // Independent palettes: a shared retro finish does not force props to use grass.
    public static class RetroMaterials
    {
        public static readonly string[] Names={"Grass","Bark","Stone","Leaves","Fur","Skin","HousePlaster","RoofTiles","Wood","Masonry","RoofSlate","EarthCliff","Brick","DirtPath","WindowLight","Feathers","Comb","SailCloth"};
        static readonly Dictionary<string,Material> cache=new Dictionary<string,Material>();
        public static Texture2D Texture(string kind)
        {
            var village = Resources.Load<Texture2D>("VillageTextures/" + kind);
            if (village != null) return village;
            string shared = kind switch
            {
                "Bark" => "ElderBark",
                "Stone" => "MossRock",
                "Brick" => "HarbourBrick",
                _ => kind
            };
            var artwork = Resources.Load<Texture2D>("Bellwake/Textures/" + shared);
            return artwork != null ? artwork : Resources.Load<Texture2D>("VillageTextures/Grass");
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
