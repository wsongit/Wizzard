using UnityEngine;

namespace Wizzard
{
    public static class MeadowTrees
    {
        static readonly GameObject[] models=new GameObject[8];
        static Material[] foliage;
        public static GameObject Create(int index, Transform parent, Vector3 position)
        {
            int variant=index%models.Length;
            if(models[variant]==null) models[variant]=Resources.Load<GameObject>($"Trees/Tree{variant+1:00}");
            if(models[variant]==null) { Debug.LogError($"Missing tree model {variant+1}"); return null; }
            if(foliage==null)
            {
                foliage=new Material[4];
                for(int i=0;i<4;i++)
                {
                    foliage[i]=new Material(RetroMaterials.Get("Leaves"));
                    foliage[i].name=$"Tree foliage shade {i}";
                    float shade=.96f+i*.035f;
                    foliage[i].SetColor("_Color",new Color(shade,shade,shade,1));
                }
            }
            var tree=Object.Instantiate(models[variant],parent);
            tree.name=$"Climbable tree {variant+1:00}";
            tree.transform.position=position;
            var random=new System.Random(index*179+31);
            tree.transform.localRotation=Quaternion.Euler(0,(float)random.NextDouble()*360,0);
            float scale=.85f+(float)random.NextDouble()*.3f;
            tree.transform.localScale=Vector3.one*scale;
            foreach(var filter in tree.GetComponentsInChildren<MeshFilter>())
            {
                filter.gameObject.layer=MeadowWorld.GroundLayer;
                var renderer=filter.GetComponent<MeshRenderer>();
                if(renderer!=null)
                {
                    var materials=renderer.sharedMaterials;
                    for(int i=0;i<materials.Length;i++)
                        materials[i]=filter.name.StartsWith("Crown")?foliage[i%foliage.Length]:RetroMaterials.Get("Bark");
                    renderer.sharedMaterials=materials;
                }
                var collider=filter.gameObject.AddComponent<MeshCollider>();
                collider.sharedMesh=filter.sharedMesh;
            }
            return tree;
        }
    }
}
