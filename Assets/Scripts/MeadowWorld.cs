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
        static readonly float villageHeight = BaseHeight(MossbellVillage.MapLocation.x, MossbellVillage.MapLocation.y);
        readonly MeadowGroundMesh surface = new MeadowGroundMesh();

        public static float Height(float x, float z)
        {
            float dx = x - MossbellVillage.MapLocation.x, dz = z - MossbellVillage.MapLocation.y;
            float squared = dx * dx + dz * dz;
            if (squared <= 48 * 48) return villageHeight;
            float terrain = BaseHeight(x, z);
            if (squared >= 72 * 72) return terrain;
            float blend = 1 - Mathf.SmoothStep(0, 1, Mathf.InverseLerp(48, 72, Mathf.Sqrt(squared)));
            return Mathf.Lerp(terrain, villageHeight, blend);
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
            public readonly float x, z, treeX, treeZ;
            public Landmark(int index, float x, float z, float treeX, float treeZ)
            {
                this.index=index; this.x=x; this.z=z; this.treeX=treeX; this.treeZ=treeZ;
            }
        }
        public readonly Dictionary<string, Material> LandmarkPaints = new Dictionary<string, Material>();
        Mesh distantGround;
        void OnDestroy()
        {
            if (distantGround != null) Destroy(distantGround);
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
            distantGround = MeadowBackdrop.Create(transform, grass);
            var random = new System.Random(197);
            for (int grove=0; grove<16; grove++)
            {
                float centreX=(float)random.NextDouble()*1470-735;
                float centreZ=(float)random.NextDouble()*1470-735;
                var centre = new Vector2(centreX,centreZ);
                if (centre.magnitude<39 || Vector2.Distance(centre,MossbellVillage.MapLocation)<94) continue;
                float bearing=(float)random.NextDouble()*Mathf.PI*2;
                for (int spot=0;spot<3;spot++)
                {
                    int index=grove*3+spot;
                    float angle=bearing+spot*Mathf.PI*2/3+(float)random.NextDouble()*.25f;
                    float radius=3.6f+(float)random.NextDouble()*1.7f;
                    float x=centreX+Mathf.Cos(angle)*radius, z=centreZ+Mathf.Sin(angle)*radius;
                    float treeAngle=angle+(.44f+.18f*(index%3))*(spot==1?-1:1);
                    float treeX=x+Mathf.Cos(treeAngle)*4.2f, treeZ=z+Mathf.Sin(treeAngle)*4.2f;
                    int tile=TileAt(x,z);
                    if (landmarks[tile]==null) landmarks[tile]=new List<Landmark>();
                    landmarks[tile].Add(new Landmark(index,x,z,treeX,treeZ));
                }
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
            int next = window.Next(Mathf.Clamp(position.x,-Size/2,Size/2), Mathf.Clamp(position.z,-Size/2,Size/2), Release, MeadowTileWindow.ReleasesPerFrame);
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
                MeadowTrees.Create(mark.index,chunk.transform,new Vector3(mark.treeX,Height(mark.treeX,mark.treeZ),mark.treeZ));
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
            surface.Fill(cx, cz);
            // Mesh setters copy the buffers. The next tile can reuse the same staging memory.
            var mesh = new Mesh
            {
                name = $"Meadow chunk {cx},{cz}", vertices = surface.Vertices,
                normals = surface.Normals, uv = surface.UV, triangles = MeadowGroundMesh.Triangles
            };
            var chunk=new GameObject(mesh.name); chunk.layer=GroundLayer; chunk.transform.SetParent(transform,false);
            chunk.AddComponent<MeshFilter>().sharedMesh=mesh;
            chunk.AddComponent<MeshRenderer>().sharedMaterial=material;
            chunk.AddComponent<MeshCollider>().sharedMesh=mesh;
            return chunk;
        }
    }
}
