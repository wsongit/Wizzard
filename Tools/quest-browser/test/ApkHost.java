package com.wizzard.bellwake.webxr;
import java.io.*;
import java.util.zip.*;
class ApkHost {
    public static void main(String[] args) throws Exception {
        ZipFile z = new ZipFile(args[0]);
        new LocalHost(new LocalHost.Files() {
            ZipEntry entry(String n) throws IOException {
                ZipEntry e = z.getEntry("assets/" + n);
                if (e == null) throw new FileNotFoundException();
                return e;
            }
            public long size(String n) throws IOException {return entry(n).getSize();}
            public InputStream open(String n) throws IOException {return z.getInputStream(entry(n));}
        });
    }
}
