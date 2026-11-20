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
            Directory.CreateDirectory("Assets/RetroMaterials/Workshop");
            AssetDatabase.Refresh();
            foreach (string kind in RetroMaterials.Names)
            {
                string path = "Assets/RetroMaterials/" + kind + ".mat";
                if (AssetDatabase.LoadAssetAtPath<Material>(path) != null) continue;
                var material = new Material(RetroMaterials.Get(kind));
                AssetDatabase.CreateAsset(material, path);
            }
            var shader = Shader.Find("Wizzard/BellwakePaint");
            var timber = Resources.Load<Texture2D>("Bellwake/Textures/HouseEdges");
            string[] edges = { "Tile fascia", "Oak lintel", "Rebated jamb", "Stone threshold" };
            for (int band = 0; band < edges.Length; band++)
                CreateDetail(edges[band], shader, timber, new RectInt(4, band * 32 + 4, 120, 24));

            var goods = Resources.Load<Texture2D>("Bellwake/Textures/YardGoods");
            foreach (var (name, swatch) in new[] {
                ("Crate side", 0), ("Crate lid", 1), ("Coiled rope", 2), ("Folded canvas", 3),
                ("Wicker", 6), ("Cask staves", 20), ("Cask head", 21), ("Bound pages", 24)
            })
            {
                int cell = swatch % 16;
                int x = swatch / 16 * 256 + cell % 4 * 64;
                CreateDetail(name, shader, goods, new RectInt(x + 2, cell / 4 * 64 + 2, 60, 60));
            }
            AssetDatabase.SaveAssets();
        }

        static void CreateDetail(string name, Shader shader, Texture2D sheet, RectInt pixels)
        {
            string path = "Assets/RetroMaterials/Workshop/" + name + ".mat";
            if (AssetDatabase.LoadAssetAtPath<Material>(path) != null) return;
            if (shader == null || sheet == null)
                throw new System.InvalidOperationException("Missing workshop artwork for " + name);

            // Unity UVs start at the bottom. The painted rectangles are measured
            // from the top and have extruded borders for mip filtering.
            var material = new Material(shader) {
                name = name,
                mainTexture = sheet,
                mainTextureScale = new Vector2((pixels.width - 1f) / sheet.width,
                                               (pixels.height - 1f) / sheet.height),
                mainTextureOffset = new Vector2((pixels.x + 0.5f) / sheet.width,
                                                1f - (pixels.yMax - 0.5f) / sheet.height)
            };
            AssetDatabase.CreateAsset(material, path);
        }
    }
}
