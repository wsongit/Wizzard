using UnityEditor;
using UnityEngine;
namespace Wizzard.Editor
{
    public static class RetroMaterialLibrary
    {
        [MenuItem("Wizzard/Create retro material library")]
        public static void Create()
        {
            System.IO.Directory.CreateDirectory("Assets/RetroMaterials"); AssetDatabase.Refresh();
            foreach(string kind in RetroMaterials.Names)
            {
                string path="Assets/RetroMaterials/"+kind;
                // Preserve any material the user has already customized.
                if(AssetDatabase.LoadAssetAtPath<Material>(path+".mat")!=null) continue;
                var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(path+".asset");
                if(texture==null) { texture=RetroMaterials.Texture(kind); AssetDatabase.CreateAsset(texture,path+".asset"); }
                var material=new Material(RetroMaterials.Get(kind)); material.mainTexture=texture;
                AssetDatabase.CreateAsset(material,path+".mat");
            }
            AssetDatabase.SaveAssets();
        }
    }
}
