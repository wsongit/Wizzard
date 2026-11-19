using UnityEngine;
using System.Collections.Generic;

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
        readonly MeadowTileWindow window = new MeadowTileWindow();
        readonly GameObject[] chunks = new GameObject[MeadowTileWindow.Count];
        readonly List<Landmark>[] landmarks = new List<Landmark>[MeadowTileWindow.Count];
        readonly struct Landmark
        {
            public readonly int index;
            public readonly float x, z;
            public Landmark(int index, float x, float z) { this.index=index; this.x=x; this.z=z; }
        }
        public readonly Dictionary<string, Material> LandmarkPaints = new Dictionary<string, Material>();
        void OnDestroy()
        {
            if (rig != null) rig.Teleporting -= GroundAt;
            foreach (var paint in LandmarkPaints.Values) Destroy(paint);
            LandmarkPaints.Clear();
        }
        GorillaPlayer rig;
        Transform viewer;
        Material grass;
        public void Initialize(GorillaPlayer player)
        {
            rig = player;
            viewer = rig.head;
            rig.Teleporting += GroundAt;
            grass = RetroMaterials.Get("Grass");
            var random = new System.Random(197);
            for (int i=0; i<48; i++)
            {
                float x=(float)random.NextDouble()*1500-750, z=(float)random.NextDouble()*1500-750;
                if(new Vector2(x,z).magnitude<25 || Vector2.Distance(new Vector2(x,z),MossbellVillage.MapLocation)<80) continue;
                int tile = TileAt(x,z);
                if (landmarks[tile] == null) landmarks[tile] = new List<Landmark>();
                landmarks[tile].Add(new Landmark(i,x,z));
            }
        }
        static int TileAt(float x, float z)
        {
            return Mathf.Clamp(Mathf.FloorToInt((x+Size/2)/ChunkSize),0,7)
                + 8*Mathf.Clamp(Mathf.FloorToInt((z+Size/2)/ChunkSize),0,7);
        }
        public void GroundAt(Vector3 position)
        {
            if (!isActiveAndEnabled) return;
            // A capsule or a planted palm can straddle a seam after a teleport.
            for (int dz=-1; dz<=1; dz+=2)
                for (int dx=-1; dx<=1; dx+=2)
                    EnsureChunk(TileAt(position.x+dx, position.z+dz));
        }
        void Update()
        {
            if (viewer == null) return;
            Vector3 position = viewer.position;
            int current = TileAt(position.x, position.z);
            if (chunks[current] == null) { EnsureChunk(current); return; }
            int next = window.Next(Mathf.Clamp(position.x,-Size/2,Size/2), Mathf.Clamp(position.z,-Size/2,Size/2), Release);
            if (next >= 0) EnsureChunk(next);
        }
        void EnsureChunk(int i)
        {
            if (chunks[i] != null) return;
            var chunk = CreateChunk(i % 8, i / 8, grass);
            chunks[i] = chunk;
            window.Added(i);
            if (landmarks[i] == null) return;
            foreach (var mark in landmarks[i])
            {
                var rock=BellwakeModels.Climbable("MeadowOutcrop",chunk.transform,LandmarkPaints);
                rock.transform.position=new Vector3(mark.x,Height(mark.x,mark.z),mark.z);
                rock.transform.rotation=Quaternion.Euler(0,mark.index*37,0);
                rock.transform.localScale=Vector3.one*(.86f+(mark.index%6)*.055f);
                MeadowTrees.Create(mark.index,chunk.transform,new Vector3(mark.x+9,Height(mark.x+9,mark.z),mark.z));
            }
        }
        void Release(int i)
        {
            var chunk = chunks[i];
            if (chunk == null) return;
            chunk.SetActive(false);
            Destroy(chunk.GetComponent<MeshFilter>().sharedMesh);
            Destroy(chunk);
            chunks[i] = null;
            window.Removed(i);
        }
        void OnDisable()
        {
            for (int i=0;i<chunks.Length;i++) Release(i);
            MeadowTrees.Release();
        }
        GameObject CreateChunk(int cx, int cz, Material material)
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
            return chunk;
        }
    }
}
