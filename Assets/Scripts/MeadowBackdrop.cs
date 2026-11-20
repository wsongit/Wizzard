using System.Collections.Generic;
using UnityEngine;

namespace Wizzard
{
    // The fine grass tiles stream. The distant watershed and its enclosing bluffs
    // stay with the meadow so a long view or a turn during a tile upload sees earth.
    internal static class MeadowBackdrop
    {
        const int Across = 64;
        const int Half = MeadowWorld.Size / 2;
        const int Spacing = MeadowWorld.Size / Across;

        internal static Mesh Create(Transform parent, Material grass)
        {
            var vertices = new List<Vector3>();
            var uv = new List<Vector2>();
            var fields = new List<int>();
            var bluffs = new List<int>();
            int Add(float x, float y, float z)
            {
                int i = vertices.Count;
                vertices.Add(new Vector3(x,y,z));
                uv.Add(new Vector2(x/8f,z/8f));
                return i;
            }
            void Quad(List<int> indices, int a, int b, int c, int d)
            {
                indices.Add(a); indices.Add(b); indices.Add(c);
                indices.Add(a); indices.Add(c); indices.Add(d);
            }

            for (int row=0;row<=Across;row++)
            {
                for (int col=0;col<=Across;col++)
                {
                    int x = col*Spacing-Half, z = row*Spacing-Half;
                    // A conservative height offset keeps the coarse surface entirely
                    // underneath the fine triangles, including where the village is levelled.
                    int a = Add(x,MeadowWorld.Height(x,z)-8,z);
                    if (row == 0 || col == 0) continue;
                    // The outer hills turn at |x| == |z|. Follow that fold in all
                    // four quadrants so a diagonal cannot bridge above the grass.
                    bool opposite = (x-Spacing/2 < 0) != (z-Spacing/2 < 0);
                    if (opposite) Quad(fields, a-Across-1, a-Across-2, a-1, a);
                    else Quad(fields, a-Across-2, a-1, a, a-Across-1);
                }
            }

            const int edgeSteps = MeadowWorld.Resolution * MeadowTileWindow.Across;
            const int loop = 4 * edgeSteps;
            int edgeStart = vertices.Count;
            for (int band=0;band<5;band++)
            {
                for (int i=0;i<loop;i++)
                {
                    int side=i/edgeSteps;
                    float along=(i%edgeSteps)*((float)MeadowWorld.Size/edgeSteps)-Half;
                    float x=side==0?along:side==1?Half:side==2?-along:-Half;
                    float z=side==0?-Half:side==1?along:side==2?Half:-along;
                    float angle=Mathf.Atan2(z,x);
                    float ground=MeadowWorld.Height(x,z);
                    float ridge=34+14*Mathf.Sin(angle*3+.4f)+9*Mathf.Cos(angle*7);
                    float extent=band==0?0:band==1?2:band==2?32:band==3?108:300;
                    float level=band==0?ground-.02f:band==1?ground+ridge*.61f:
                                band==2?ground+ridge:band==3?ground+ridge*.31f:ground+ridge*1.7f;
                    float scale=1+extent/Half;
                    Add(x*scale,level,z*scale);
                    if (band>0)
                    {
                        int a=edgeStart+(band-1)*loop+i, b=edgeStart+(band-1)*loop+(i+1)%loop;
                        Quad(band==3?fields:bluffs,a,b,b+loop,a+loop);
                    }
                }
            }
            var mesh=new Mesh { name="Long Meadow distant land and surrounding bluffs" };
            mesh.SetVertices(vertices);
            mesh.SetUVs(0,uv);
            mesh.subMeshCount=2;
            mesh.SetTriangles(fields,0);
            mesh.SetTriangles(bluffs,1);
            mesh.RecalculateNormals();
            var scenery=new GameObject("Distant valley");
            scenery.transform.SetParent(parent,false);
            scenery.AddComponent<MeshFilter>().sharedMesh=mesh;
            scenery.AddComponent<MeshRenderer>().sharedMaterials=new[]{grass,RetroMaterials.Get("EarthCliff")};
            // The inward faces follow the foot of the bluff. A player can push on
            // the rock without stepping through the edge of the final grass tile.
            for (int side=0;side<4;side++)
            {
                bool eastWest=side<2;
                float coordinate=(side%2==0?-1:1)*(Half+1f);
                var wall=new GameObject("Meadow escarpment");
                wall.layer=MeadowWorld.GroundLayer;
                wall.transform.SetParent(scenery.transform,false);
                var collider=wall.AddComponent<BoxCollider>();
                collider.center=eastWest?new Vector3(coordinate,240,0):new Vector3(0,240,coordinate);
                collider.size=eastWest?new Vector3(2,540,MeadowWorld.Size+4):new Vector3(MeadowWorld.Size+4,540,2);
            }
            return mesh;
        }
    }
}
