using System.Collections.Generic;
using UnityEngine;

namespace Wizzard
{
    public static class BellwakeModels
    {
        static readonly Dictionary<string, Material> avatarPaints = new Dictionary<string, Material>();
        public static GameObject Create(string name, Transform parent)
        {
            return Create(name, parent, avatarPaints);
        }
        static GameObject Create(string name, Transform parent, Dictionary<string, Material> materials)
        {
            var model = Object.Instantiate(Resources.Load<GameObject>("Bellwake/Rooms/" + name), parent, false);
            foreach (var renderer in model.GetComponentsInChildren<MeshRenderer>())
            {
                var slots = renderer.sharedMaterials;
                for (int i = 0; i < slots.Length; i++)
                {
                    string key = slots[i].name;
                    if (!materials.TryGetValue(key, out var paint) || paint == null)
                    {
                        paint = new Material(Shader.Find("Wizzard/BellwakePaint")) {
                            mainTexture = Resources.Load<Texture2D>("Bellwake/Textures/" + key)
                        };
                        materials[key] = paint;
                    }
                    slots[i] = paint;
                }
                renderer.sharedMaterials = slots;
            }
            return model;
        }
        public static GameObject Climbable(string name, Transform parent, Dictionary<string, Material> materials)
        {
            var model = Create(name, parent, materials);
            foreach (var filter in model.GetComponentsInChildren<MeshFilter>())
            {
                filter.gameObject.layer = MeadowWorld.GroundLayer;
                filter.gameObject.AddComponent<MeshCollider>().sharedMesh = filter.sharedMesh;
                if (filter.name == "C_Solids")
                    filter.GetComponent<MeshRenderer>().enabled = false;
            }
            return model;
        }
    }
}
