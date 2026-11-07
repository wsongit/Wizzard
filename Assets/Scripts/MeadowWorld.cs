using UnityEngine;
using UnityEngine.Rendering;

namespace Wizzard
{
    // Original procedural artwork, inspired by the palette and geometry of N64 landscapes.
    public sealed class MeadowWorld : MonoBehaviour
    {
        public const int Size = 2048;
        public const int ChunkSize = 256;
        public const int Resolution = 32;
        public const int GroundLayer = 8;
        public static float Height(float x, float z)
        {
            float edge = Mathf.Max(Mathf.Abs(x), Mathf.Abs(z));
            float hills = 5f * Mathf.Sin(x * .012f) * Mathf.Cos(z * .009f)
                        + 2.5f * Mathf.Sin(x * .027f + z * .018f)
                        + 7f * Mathf.Exp(-((x-115)*(x-115)+(z-95)*(z-95))/18000f);
            return hills + Mathf.SmoothStep(0, 100, Mathf.InverseLerp(840, 1024, edge));
        }
        public static Texture2D GrassTexture()
        {
            var texture = new Texture2D(32, 32, TextureFormat.RGB24, false);
            texture.name = "Original 32px meadow grass";
            texture.filterMode = FilterMode.Point;
            texture.wrapMode = TextureWrapMode.Repeat;
            var random = new System.Random(641997);
            for (int y=0; y<32; y++) for (int x=0; x<32; x++)
            {
                float t=(float)random.NextDouble();
                Color c = t < .13f ? new Color(.26f,.36f,.10f) :
                          t > .84f ? new Color(.53f,.61f,.23f) : new Color(.40f,.51f,.16f);
                texture.SetPixel(x,y,c);
            }
            texture.Apply(); return texture;
        }
        void Awake()
        {
            var material = new Material(Shader.Find("Wizzard/RetroGrass"));
            material.mainTexture = GrassTexture();
            for(int z=0; z<8; z++) for(int x=0; x<8; x++) CreateChunk(x,z,material);
            CreateLandmarks();
        }
        void CreateChunk(int cx, int cz, Material material)
        {
            var vertices = new Vector3[33*33]; var uvs = new Vector2[vertices.Length];
            var tris = new int[32*32*6];
            float ox=cx*ChunkSize-Size/2, oz=cz*ChunkSize-Size/2;
            for(int z=0;z<=Resolution;z++) for(int x=0;x<=Resolution;x++)
            {
                int i=z*33+x; float px=ox+x*8, pz=oz+z*8;
                vertices[i]=new Vector3(px,Height(px,pz),pz); uvs[i]=new Vector2(px/8,pz/8);
            }
            int n=0;
            for(int z=0;z<32;z++) for(int x=0;x<32;x++)
            {
                int i=z*33+x;
                tris[n++]=i; tris[n++]=i+33; tris[n++]=i+1;
                tris[n++]=i+1; tris[n++]=i+33; tris[n++]=i+34;
            }
            var mesh=new Mesh {name=$"Meadow chunk {cx},{cz}", vertices=vertices, uv=uvs, triangles=tris};
            mesh.RecalculateNormals(); mesh.RecalculateBounds();
            var chunk=new GameObject(mesh.name); chunk.layer=GroundLayer; chunk.transform.SetParent(transform,false);
            chunk.AddComponent<MeshFilter>().sharedMesh=mesh;
            chunk.AddComponent<MeshRenderer>().sharedMaterial=material;
            chunk.AddComponent<MeshCollider>().sharedMesh=mesh;
        }
        void CreateLandmarks()
        {
            var stone = new Material(Shader.Find("Standard")) {color=new Color(.44f,.43f,.34f)};
            var bark = new Material(Shader.Find("Standard")) {color=new Color(.29f,.18f,.09f)};
            var leaf = new Material(Shader.Find("Standard")) {color=new Color(.23f,.35f,.11f)};
            var random = new System.Random(197);
            for(int i=0;i<48;i++)
            {
                float x=(float)random.NextDouble()*1500-750, z=(float)random.NextDouble()*1500-750;
                if(new Vector2(x,z).magnitude<25) continue;
                float h=Height(x,z);
                var rock=GameObject.CreatePrimitive(PrimitiveType.Cube); rock.name="Climbable stone";
                rock.layer=GroundLayer; rock.transform.SetParent(transform);
                rock.transform.position=new Vector3(x,h+1.4f,z);
                rock.transform.localScale=new Vector3(4,3,4);
                rock.transform.rotation=Quaternion.Euler(0,i*37,8);
                rock.GetComponent<Renderer>().sharedMaterial=stone;
                var trunk=GameObject.CreatePrimitive(PrimitiveType.Cylinder); trunk.name="Climbable tree";
                trunk.layer=GroundLayer; trunk.transform.SetParent(transform);
                trunk.transform.position=new Vector3(x+9,Height(x+9,z)+3,z);
                trunk.transform.localScale=new Vector3(1.3f,3,1.3f);
                trunk.GetComponent<Renderer>().sharedMaterial=bark;
                var crown=GameObject.CreatePrimitive(PrimitiveType.Sphere); crown.name="Canopy";
                crown.layer=GroundLayer; crown.transform.SetParent(transform);
                crown.transform.position=trunk.transform.position+Vector3.up*4;
                crown.transform.localScale=new Vector3(9,7,9); crown.GetComponent<Renderer>().sharedMaterial=leaf;
            }
        }
    }
}
