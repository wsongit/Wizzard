// Compile alongside Assets/Scripts/MeadowTileWindow.cs with a C# compiler.
using System;
using System.Collections.Generic;
using Wizzard;

static class MeadowTravelCheck
{
    static void Main()
    {
        var window = new MeadowTileWindow();
        var live = new HashSet<int>();
        int loads = 0, drops = 0, peak = 0, probes = 0;
        Action<int> release = id => { if (!live.Remove(id)) throw new Exception("Double unload"); drops++; };
        Action<float,float> visit = (x,z) =>
        {
            probes++;
            int next;
            while ((next = window.Next(x,z,release)) >= 0)
            {
                if (!live.Add(next)) throw new Exception("Duplicate tile");
                window.Added(next);
                loads++;
            }
            for (int i=0; i<64; i++)
            {
                int tx = i % 8 * 256 - 1024, tz = i / 8 * 256 - 1024;
                float dx = Math.Max(0,Math.Max(tx-x,x-(tx+256)));
                float dz = Math.Max(0,Math.Max(tz-z,z-(tz+256)));
                float square = dx*dx+dz*dz;
                if ((square <= 400*400 && !live.Contains(i)) || (square > 464*464 && live.Contains(i)))
                    throw new Exception("Incorrect visible window at " + x + "," + z);
            }
            peak = Math.Max(peak,live.Count);
        };
        for(int lap=0; lap<3; lap++)
        {
            for(int z=-1024; z<=1024; z+=128)
                for(int x=-1024; x<=1024; x+=32) visit(x,z);
            visit(0,0); visit(240,104); visit(-1024,1024); visit(1024,-1024);
        }
        if (loads - drops != live.Count || peak >= 32 || drops == 0) throw new Exception("Unbounded terrain");
        Console.WriteLine("{0} positions, {1} loads, {2} unloads, peak {3}/64 terrain chunks",probes,loads,drops,peak);
    }
}
