// Compile with Assets/Editor/QuestApk.cs and System.IO.Compression.
using System;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Threading.Tasks;
using Wizzard.Editor;

static class QuestApkCheck
{
    static void Entry(ZipArchive apk, string name, byte[] bytes)
    {
        using (var stream=apk.CreateEntry(name).Open()) stream.Write(bytes,0,bytes.Length);
    }

    static string Fixture(string folder, string id, string defect="")
    {
        string file=Path.Combine(folder,id+".apk");
        var header=new byte[64];
        Array.Copy(new byte[] { 0x7f,69,76,70,2,1,1 },header,7);
        header[16]=3;header[18]=183;
        using (var stream=File.Create(file))
        using (var apk=new ZipArchive(stream,ZipArchiveMode.Create))
        {
            Entry(apk,"AndroidManifest.xml",new byte[] { 1 });
            Entry(apk,"assets/bin/Data/boot.config",System.Text.Encoding.UTF8.GetBytes(id));
            foreach (var name in new[] { "libunity.so","libil2cpp.so","libUnityOpenXR.so","libopenxr_loader.so" })
            {
                if (defect=="missing" && name=="libil2cpp.so") continue;
                var content=(byte[])header.Clone();
                if (defect=="x86" && name=="libopenxr_loader.so") content[18]=62;
                if (defect=="truncated" && name=="libUnityOpenXR.so") Array.Resize(ref content,8);
                Entry(apk,"lib/arm64-v8a/"+name,content);
            }
            if (defect=="launcher") Entry(apk,"assets/index.html",new byte[] { 1 });
        }
        return file;
    }

    static void Main()
    {
        string root=Path.Combine(Path.GetTempPath(),"Bellwake-Publish-"+Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            string first=Fixture(root,"first"), next=Fixture(root,"next");
            string output=Path.Combine(root,"Wizzard-Bellwake-Quest.apk");
            QuestApk.Publish(first,output);
            if (!File.ReadAllBytes(output).SequenceEqual(File.ReadAllBytes(first))) throw new Exception("First build");
            QuestApk.Publish(next,output);
            var good=File.ReadAllBytes(next);
            foreach (var defect in new[] { "missing","x86","truncated","launcher" })
            {
                try { QuestApk.Publish(Fixture(root,defect,defect),output); }
                catch (InvalidDataException)
                {
                    if (File.ReadAllBytes(output).SequenceEqual(good)) continue;
                }
                throw new Exception("Failed to preserve the previous APK for "+defect);
            }
            File.Delete(output);
            var candidates=Enumerable.Range(0,6).Select(i=>Fixture(root,"parallel-"+i)).ToArray();
            Parallel.ForEach(candidates,file=>QuestApk.Publish(file,output));
            var last=File.ReadAllBytes(output);
            if (!candidates.Any(file=>File.ReadAllBytes(file).SequenceEqual(last)) ||
                Directory.GetFiles(root,"*.tmp").Length!=0) throw new Exception("Incomplete concurrent publication");
            Console.WriteLine("PASS first install, replacement, four invalid APKs and competing native builds");
        }
        finally { Directory.Delete(root,true); }
    }
}
