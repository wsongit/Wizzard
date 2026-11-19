// Compile with MeadowGroundMesh.cs against Wizzard.dll and the Unity 2022.3 managed assemblies.
using System;
using System.Diagnostics;
using UnityEngine;
using Wizzard;

static class MeadowSurfaceCheck
{
    const int Cells = MeadowWorld.Resolution, Side = Cells + 1;
    static float OriginalHills(float x,float z)
    {
        float edge = Mathf.Max(Mathf.Abs(x),Mathf.Abs(z));
        float hills = 5f*Mathf.Sin(x*.012f)*Mathf.Cos(z*.009f) + 2.5f*Mathf.Sin(x*.027f+z*.018f)
                    + 7f*Mathf.Exp(-((x-115)*(x-115)+(z-95)*(z-95))/18000f);
        return hills+Mathf.SmoothStep(0,100,Mathf.InverseLerp(840,1024,edge));
    }
    static float OriginalHeight(float x,float z)
    {
        Vector2 village=MossbellVillage.MapLocation;
        float blend=1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(48,72,Vector2.Distance(new Vector2(x,z),village)));
        return Mathf.Lerp(OriginalHills(x,z),OriginalHills(village.x,village.y),blend);
    }
    static void Seam(MeadowGroundMesh a,int i,MeadowGroundMesh b,int j)
    {
        if (!a.Vertices[i].Equals(b.Vertices[j]) || !a.Normals[i].Equals(b.Normals[j]) || !a.UV[i].Equals(b.UV[j]))
            throw new Exception("Position, lighting or paint changed at a tile boundary");
    }
    static void Main()
    {
        var a=new MeadowGroundMesh();
        var b=new MeadowGroundMesh();
        int seams=0,samples=0;
        float largest=0;
        int[] triangles=MeadowGroundMesh.Triangles;
        for(int z=0;z<8;z++) for(int x=0;x<8;x++)
        {
            a.Fill(x,z);
            for(int k=0;k<a.Vertices.Length;k++)
            {
                var v=a.Vertices[k];
                largest=Math.Max(largest,Math.Abs(v.y-OriginalHeight(v.x,v.z)));
                if (Math.Abs(a.Normals[k].magnitude-1)>.00001f || a.Normals[k].y<=0)
                    throw new Exception("Invalid slope normal");
                samples++;
            }
            if(x<7)
            {
                b.Fill(x+1,z);
                for(int i=0;i<Side;i++){Seam(a,i*Side+Cells,b,i*Side);seams++;}
            }
            if(z<7)
            {
                b.Fill(x,z+1);
                for(int i=0;i<Side;i++){Seam(a,Cells*Side+i,b,i);seams++;}
            }
        }
        if (largest>.00001f || triangles.Length!=6*Cells*Cells) throw new Exception("Ground shape changed");
        for(int i=0;i<triangles.Length;i+=3)
        {
            var up=Vector3.Cross(a.Vertices[triangles[i+1]]-a.Vertices[triangles[i]],a.Vertices[triangles[i+2]]-a.Vertices[triangles[i]]);
            if(up.y<=0)throw new Exception("Inverted collision triangle");
        }
        var watch=new Stopwatch();
        long before=GC.GetAllocatedBytesForCurrentThread();
        watch.Start();
        for(int i=0;i<640;i++) a.Fill(i%8,i/8%8);
        watch.Stop();
        long bytes=GC.GetAllocatedBytesForCurrentThread()-before;
        if(bytes!=0)throw new Exception("Allocated while refilling tile buffers: "+bytes);
        Console.WriteLine("{0} heights, {1} matched seams, maximum height error {2}, 640 refills {3} ms / {4} managed bytes",samples,seams,largest,watch.ElapsedMilliseconds,bytes);
    }
}
