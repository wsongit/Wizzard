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
            if(key=="VillageGround")
            {
                var groundShader=Shader.Find("Wizzard/VillageGround");
                if(groundShader==null) throw new System.InvalidOperationException("VillageGround shader missing");
                var grass=Resources.Load<Texture2D>("VillageTextures/Grass");
                var dirt=Resources.Load<Texture2D>("VillageTextures/DirtPath");
                var mask=Resources.Load<Texture2D>("VillageMasks/GroundPaths");
                if(grass==null || dirt==null || mask==null)
                    throw new System.InvalidOperationException("Village ground tiles or path coverage mask missing. Pull all project assets.");
                var ground=new Material(groundShader) {name="Village "+key, mainTexture=grass, enableInstancing=true};
                ground.SetTexture("_DirtTex",dirt);
                ground.SetTexture("_PathMask",mask);
                // Mask covers Blender X [-55,60], Y [-46,68]. Model UVs are XY/4,
                // avoiding any dependency on the model importer's axis reflection.
                ground.SetVector("_MaskTransform",new Vector4(4f/115f,4f/114f,55f/115f,46f/114f));
                cache[key]=ground;return ground;
            }
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
