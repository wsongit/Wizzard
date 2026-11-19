// Compile alongside Assets/Scripts/MeadowTileWindow.cs with a C# compiler.
using System;
using System.Collections.Generic;
using Wizzard;

static class MeadowTravelCheck
{
    static void FramePacedTravel()
    {
        var window = new MeadowTileWindow();
        var live = new HashSet<int>();
        int frames=0, loads=0, drops=0, peak=0, busiest=0;
        Func<float,int> axis = v=>Math.Max(0,Math.Min(7,(int)Math.Floor((v+1024)/256)));
        Func<float,float,int> tile = (x,z)=>axis(x)+8*axis(z);
        Action<int> add=i=>{if(live.Add(i)){window.Added(i);loads++;}};
        for(int trip=0;trip<24;trip++)
        {
            float centreX=((trip*3)%7-3)*256, centreZ=((trip*5)%7-3)*256;
            // Teleports prepare the four corner tiles synchronously; subsequent frames stream one addition.
            foreach(int dx in new[]{-1,1}) foreach(int dz in new[]{-1,1}) add(tile(centreX+dx,centreZ+dz));
            for(int frame=0;frame<64;frame++)
            {
                float x=centreX+Math.Min(frame,32)*.09f, z=centreZ-Math.Min(frame,32)*.11f;
                int released=0;
                int next=window.Next(x,z,id=>{
                    if(!live.Remove(id)) throw new Exception("Retired a missing tile");
                    drops++;released++;
                },MeadowTileWindow.ReleasesPerFrame);
                if(next>=0) add(next);
                if(released>MeadowTileWindow.ReleasesPerFrame) throw new Exception("Chunk release burst");
                if(!live.Contains(tile(x,z))) throw new Exception("Ground vanished during travel");
                if(frame==63 && (next>=0 || released!=0)) throw new Exception("Streaming did not settle");
                busiest=Math.Max(busiest,released);
                peak=Math.Max(peak,live.Count);
                frames++;
            }
        }
        if(loads-drops!=live.Count || peak>=32 || busiest!=MeadowTileWindow.ReleasesPerFrame)
            throw new Exception("Unbounded frame-paced tile travel");
        Console.WriteLine("{0} streaming frames, {1} teleports, maximum {2} retirement(s) per frame, peak {3} tiles",frames,24,busiest,peak);
    }
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
        FramePacedTravel();
        Console.WriteLine("{0} positions, {1} loads, {2} unloads, peak {3}/64 terrain chunks",probes,loads,drops,peak);
    }
}
