using UnityEngine;

namespace Wizzard
{
    // Sampling one extra vertex on each side gives both owners of a seam the same slope.
    internal sealed class MeadowGroundMesh
    {
        const int Cells = MeadowWorld.Resolution;
        const int Side = Cells + 1;
        const int PaddedSide = Side + 2;
        const float Spacing = (float)MeadowWorld.ChunkSize / Cells;

        readonly float[] heights = new float[PaddedSide * PaddedSide];
        internal readonly Vector3[] Vertices = new Vector3[Side * Side];
        internal readonly Vector3[] Normals = new Vector3[Side * Side];
        internal readonly Vector2[] UV = new Vector2[Side * Side];
        internal static readonly int[] Triangles = MakeTriangles();

        internal void Fill(int column, int row)
        {
            float left = column * MeadowWorld.ChunkSize - MeadowWorld.Size / 2;
            float front = row * MeadowWorld.ChunkSize - MeadowWorld.Size / 2;
            for (int z = 0; z < PaddedSide; z++)
                for (int x = 0; x < PaddedSide; x++)
                    heights[z * PaddedSide + x] = MeadowWorld.Height(left + (x - 1) * Spacing, front + (z - 1) * Spacing);

            for (int z = 0; z < Side; z++)
            {
                for (int x = 0; x < Side; x++)
                {
                    int i = z * Side + x, h = (z + 1) * PaddedSide + x + 1;
                    float px = left + x * Spacing, pz = front + z * Spacing;
                    Vertices[i] = new Vector3(px, heights[h], pz);
                    UV[i] = new Vector2(px / 8f, pz / 8f);
                    Normals[i] = new Vector3(heights[h - 1] - heights[h + 1], 2 * Spacing,
                                             heights[h - PaddedSide] - heights[h + PaddedSide]).normalized;
                }
            }
        }

        static int[] MakeTriangles()
        {
            var triangles = new int[Cells * Cells * 6];
            int i = 0;
            for (int z = 0; z < Cells; z++)
            {
                for (int x = 0; x < Cells; x++)
                {
                    int v = z * Side + x;
                    triangles[i++] = v;
                    triangles[i++] = v + Side;
                    triangles[i++] = v + 1;
                    triangles[i++] = v + 1;
                    triangles[i++] = v + Side;
                    triangles[i++] = v + Side + 1;
                }
            }
            return triangles;
        }
    }
}
