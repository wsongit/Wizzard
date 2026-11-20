using System.IO;
using UnityEditor;
using UnityEngine;

namespace Wizzard.Editor
{
    public static class RetroMaterialLibrary
    {
        [MenuItem("Wizzard/Create retro material library")]
        public static void Create()
        {
            Directory.CreateDirectory("Assets/RetroMaterials");
            AssetDatabase.Refresh();
            foreach (string kind in RetroMaterials.Names)
            {
                string path = "Assets/RetroMaterials/" + kind + ".mat";
                if (AssetDatabase.LoadAssetAtPath<Material>(path) != null) continue;
                var material = new Material(RetroMaterials.Get(kind));
                AssetDatabase.CreateAsset(material, path);
            }
            AssetDatabase.SaveAssets();
        }
    }
}
