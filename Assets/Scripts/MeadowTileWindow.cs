using System;

namespace Wizzard
{
    // Tile ownership in world metres. A retention band avoids repeated rebuilds at a boundary.
    public sealed class MeadowTileWindow
    {
        public const int Across = 8, Width = 256, Count = Across * Across;
        public const float Visible = 400, Retain = 464;
        readonly bool[] loaded = new bool[Count];

        public int Next(float x, float z, Action<int> release)
        {
            int nearest = -1;
            float best = float.MaxValue;
            for (int i = 0; i < Count; i++)
            {
                float dx = Math.Max(0, Math.Abs(x - Centre(i % Across)) - Width * .5f);
                float dz = Math.Max(0, Math.Abs(z - Centre(i / Across)) - Width * .5f);
                float distance = dx * dx + dz * dz;
                if (loaded[i] && distance > Retain * Retain)
                {
                    release(i);
                    loaded[i] = false;
                }
                if (!loaded[i] && distance <= Visible * Visible && distance < best)
                {
                    nearest = i;
                    best = distance;
                }
            }
            return nearest;
        }

        static float Centre(int index) { return (index + .5f - Across * .5f) * Width; }
        public void Added(int i) { loaded[i] = true; }
        public void Removed(int i) { loaded[i] = false; }
    }
}
