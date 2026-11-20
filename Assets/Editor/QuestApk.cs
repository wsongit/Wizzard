using System;
using System.IO;
using System.IO.Compression;
using System.Threading;
using System.ComponentModel;
using System.Runtime.InteropServices;

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

        [DllImport("kernel32.dll", CharSet=CharSet.Unicode, ExactSpelling=true, SetLastError=true)]
        static extern bool MoveFileExW(string source, string destination, uint flags);

        static string WindowsPath(string path)
        {
            if (path.StartsWith(@"\\?\", StringComparison.Ordinal)) return path;
            return path.StartsWith(@"\\", StringComparison.Ordinal)
                ? @"\\?\UNC\" + path.Substring(2) : @"\\?\" + path;
        }

        static void Install(string temporary, string final)
        {
            if (Environment.OSVersion.Platform == PlatformID.Win32NT)
            {
                // A same-volume rename does not move the old APK aside. Another publisher
                // or a scanner can hold its name briefly, so retry that operation only.
                string source = WindowsPath(temporary);
                string destination = WindowsPath(final);
                const uint replaceExisting = 1, writeThrough = 8;
                for (int attempt=0; ; attempt++)
                {
                    if (MoveFileExW(source,destination,replaceExisting | writeThrough)) return;
                    int error=Marshal.GetLastWin32Error();
                    bool contention=error==5 || error==32 || error==33;
                    if (!contention || attempt==6)
                        throw new IOException("Could not install the Quest APK at "+final,new Win32Exception(error));
                    Thread.Sleep(10 << attempt);
                }
            }
            if (File.Exists(final)) File.Replace(temporary,final,null);
            else
            {
                try { File.Move(temporary,final); }
                catch (IOException) when (File.Exists(final)) { File.Replace(temporary,final,null); }
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
                Install(temporary,final);
            }
            finally
            {
                if (File.Exists(temporary)) File.Delete(temporary);
            }
        }
    }
}
