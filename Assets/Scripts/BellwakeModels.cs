using System.Collections.Generic;
using UnityEngine;

namespace Wizzard
{
    public sealed class BellwakeModels : MonoBehaviour
    {
        readonly Dictionary<string, Material> paints = new Dictionary<string, Material>();

        // A rig, opening stage or district owns its models and their shared material instances.
        static Dictionary<string, Material> PaintsFor(Transform parent)
        {
            var owner=parent.GetComponentInParent<BellwakeModels>(true);
            if (!owner) owner=parent.gameObject.AddComponent<BellwakeModels>();
            return owner.paints;
        }

        void OnDestroy()
        {
            foreach (var paint in paints.Values) Destroy(paint);
            paints.Clear();
        }

        public static GameObject Wayfarer(string name, Transform parent)
        {
            return Create("Bellwake/Wayfarer/" + name, parent, PaintsFor(parent));
        }
        public static GameObject Create(string name, Transform parent)
        {
            return Create("Bellwake/Rooms/" + name, parent, PaintsFor(parent));
        }
        static GameObject Create(string path, Transform parent, Dictionary<string, Material> materials)
        {
            var model = Object.Instantiate(Resources.Load<GameObject>(path), parent, false);
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
                        if(key=="MothLamp") paint.SetFloat("_Glow",.86f);
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
            var model = Create("Bellwake/Rooms/" + name, parent, materials);
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
