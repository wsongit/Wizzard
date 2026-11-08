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
            float distance=Vector2.Distance(new Vector2(x,z),MossbellVillage.MapLocation);
            float blend=1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(48,72,distance));
            return Mathf.Lerp(BaseHeight(x,z),BaseHeight(MossbellVillage.MapLocation.x,MossbellVillage.MapLocation.y),blend);
        }
        static float BaseHeight(float x,float z)
        {
            float edge = Mathf.Max(Mathf.Abs(x), Mathf.Abs(z));
            float hills = 5f * Mathf.Sin(x * .012f) * Mathf.Cos(z * .009f)
                        + 2.5f * Mathf.Sin(x * .027f + z * .018f)
                        + 7f * Mathf.Exp(-((x-115)*(x-115)+(z-95)*(z-95))/18000f);
            return hills + Mathf.SmoothStep(0, 100, Mathf.InverseLerp(840, 1024, edge));
        }
        public static Texture2D GrassTexture()
        {
            return RetroMaterials.Get("Grass").mainTexture as Texture2D;
        }
        void Awake()
        {
            var material=RetroMaterials.Get("Grass");
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
            var stone = RetroMaterials.Get("Stone");
            var random = new System.Random(197);
            for(int i=0;i<48;i++)
            {
                float x=(float)random.NextDouble()*1500-750, z=(float)random.NextDouble()*1500-750;
                if(new Vector2(x,z).magnitude<25 || Vector2.Distance(new Vector2(x,z),MossbellVillage.MapLocation)<80) continue;
                float h=Height(x,z);
                var rock=GameObject.CreatePrimitive(PrimitiveType.Cube); rock.name="Climbable stone";
                rock.layer=GroundLayer; rock.transform.SetParent(transform);
                rock.transform.position=new Vector3(x,h+1.4f,z);
                rock.transform.localScale=new Vector3(4,3,4);
                rock.transform.rotation=Quaternion.Euler(0,i*37,8);
                rock.GetComponent<Renderer>().sharedMaterial=stone;
                MeadowTrees.Create(i,transform,new Vector3(x+9,Height(x+9,z),z));
            }
        }
    }
}
