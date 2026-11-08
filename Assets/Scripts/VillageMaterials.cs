using System.Collections.Generic;
using UnityEngine;

namespace Wizzard
{
    // UVs are authored in Blender in metres; keep meadow's triplanar material separate.
    public static class VillageMaterials
    {
        static readonly Dictionary<string,Material> cache=new Dictionary<string,Material>();
        public static Material Get(string name)
        {
            // Unity's importer may append instance suffixes to a source material name.
            string key=name.Split(' ')[0];
            if(cache.TryGetValue(key,out var existing) && existing!=null) return existing;
            var texture=Resources.Load<Texture2D>("VillageTextures/"+key);
            if(texture==null) throw new System.InvalidOperationException("Village texture missing: "+key);
            var shader=Shader.Find("Wizzard/VillageSurface");
            if(shader==null) throw new System.InvalidOperationException("VillageSurface shader missing");
            var material=new Material(shader) {name="Village "+key, mainTexture=texture};
            material.SetFloat("_CastShadows",key=="PathBlend"?0:1);
            material.SetFloat("_Cutoff",key == "PathBlend" ? 0.5f : 0f);
            material.enableInstancing=true;
            cache[key]=material;return material;
        }
    }
}
