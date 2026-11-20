using System;
using System.IO;
using System.IO.Compression;

namespace Wizzard.Editor
{
    internal static class QuestApk
    {
        static ZipArchiveEntry Required(ZipArchive apk, string name)
        {
            var entry=apk.GetEntry(name);
            if (entry==null || entry.Length==0)
                throw new InvalidDataException("Native Quest player missing "+name);
            return entry;
        }

        static void Validate(Stream input)
        {
            using (var apk=new ZipArchive(input,ZipArchiveMode.Read,true))
            {
                Required(apk,"AndroidManifest.xml");
                Required(apk,"assets/bin/Data/boot.config");
                foreach (string library in new[] { "libunity.so","libil2cpp.so","libUnityOpenXR.so","libopenxr_loader.so" })
                {
                    var entry=Required(apk,"lib/arm64-v8a/"+library);
                    using (var reader=new BinaryReader(entry.Open()))
                    {
                        var header=reader.ReadBytes(20);
                        if (header.Length<20 || header[0]!=0x7f || header[1]!='E' || header[2]!='L' ||
                            header[3]!='F' || header[4]!=2 || header[5]!=1 || header[6]!=1 ||
                            header[16]!=3 || header[17]!=0 || header[18]!=183 || header[19]!=0)
                            throw new InvalidDataException("Expected an ARM64 ELF shared library at "+entry.FullName);
                    }
                }
                if (apk.GetEntry("assets/index.html")!=null)
                    throw new InvalidDataException("Unexpected web launcher in native Quest build");
            }
        }

        internal static void Publish(string source, string destination)
        {
            string final=Path.GetFullPath(destination);
            string temporary=final+"."+Guid.NewGuid().ToString("N")+".tmp";
            try
            {
                using (var input=File.OpenRead(source))
                {
                    Validate(input);
                    input.Position=0;
                    using (var output=new FileStream(temporary,FileMode.CreateNew,FileAccess.Write,FileShare.None))
                    {
                        input.CopyTo(output);
                        output.Flush(true);
                    }
                }
                if (File.Exists(final)) File.Replace(temporary,final,null);
                else
                {
                    try { File.Move(temporary,final); }
                    catch (IOException) when (File.Exists(final)) { File.Replace(temporary,final,null); }
                }
            }
            finally
            {
                if (File.Exists(temporary)) File.Delete(temporary);
            }
        }
    }
}
