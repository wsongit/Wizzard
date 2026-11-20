package com.wizzard.bellwake.webxr;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;

final class LocalHost implements Closeable {
    static final int PORT = 38761;
    static final String ORIGIN = "http://127.0.0.1:" + PORT;
    interface Files {
        InputStream open(String name) throws IOException;
        long size(String name) throws IOException;
    }
    private final Files files;
    private final ServerSocket socket;
    private final ThreadPoolExecutor workers = new ThreadPoolExecutor(4, 4, 0, TimeUnit.SECONDS, new ArrayBlockingQueue<Runnable>(32));
    LocalHost(Files files) throws IOException {
        this.files = files;
        socket = new ServerSocket();
        socket.setReuseAddress(true);
        try { socket.bind(new InetSocketAddress(InetAddress.getByName("127.0.0.1"), PORT)); }
        catch (IOException e) { socket.close(); throw e; }
        new Thread(() -> {
            while (!socket.isClosed()) {
                try {
                    Socket client = socket.accept();
                    try { workers.execute(() -> serve(client)); }
                    catch (RejectedExecutionException e) { client.close(); }
                } catch (IOException e) { break; }
            }
        }, "Bellwake loopback").start();
    }
    public void close() {
        try { socket.close(); } catch (IOException ignored) {}
        workers.shutdown();
    }
    private static String line(InputStream input) throws IOException {
        StringBuilder text = new StringBuilder();
        while (text.length() < 8192) {
            int c = input.read();
            if (c < 0) throw new EOFException();
            if (c == 10) return text.toString();
            if (c != 13) text.append((char)c);
        }
        throw new IOException("Header too long");
    }
    private static void headers(OutputStream out,String status,long length,String other) throws IOException {
        out.write(("HTTP/1.1 " + status + "\r\nConnection: close\r\nContent-Length: " + length + "\r\n" + other + "\r\n").getBytes(StandardCharsets.US_ASCII));
    }
    private void serve(Socket client) {
        try (Socket connection=client; InputStream input = new BufferedInputStream(connection.getInputStream()); OutputStream out=connection.getOutputStream()) {
            connection.setSoTimeout(7000);
            String[] request=line(input).split(" ");
            if(request.length!=3 || !("GET".equals(request[0]) || "HEAD".equals(request[0]))) { headers(out,"405 Method Not Allowed",0,"Allow: GET, HEAD\r\n"); return; }
            Map<String,String> h=new HashMap<>();
            for (int i=0;;i++) {
                String header=line(input);
                if(header.isEmpty()) break;
                int split=header.indexOf(':');
                if(i>=60 || split<1) { headers(out,"400 Bad Request",0,""); return; }
                h.put(header.substring(0,split).toLowerCase(Locale.ROOT),header.substring(split+1).trim());
            }
            if(!("127.0.0.1:"+PORT).equals(h.get("host"))) { headers(out,"403 Forbidden",0,""); return; }
            String path=request[1].split("[?]",2)[0];
            String name;
            if(path.equals("/") || path.equals("/index.html")) name="index.html";
            else if(path.matches("/assets/[a-zA-Z0-9_-]+-[0-9a-f]{12}\\.(ogg|jpg|png|json|glb\\.gz|bvh\\.gz)")) name=path.substring(1);
            else { headers(out,"404 Not Found",0,""); return; }
            long total;
            try { total=files.size(name); } catch(IOException e) { headers(out,"404 Not Found",0,""); return; }
            String type=name.endsWith(".html")?"text/html; charset=utf-8":name.endsWith(".ogg")?"audio/ogg":name.endsWith(".jpg")?"image/jpeg":name.endsWith(".png")?"image/png":name.endsWith(".json")?"application/json":"application/octet-stream";
            long start=0, end=total-1;
            String range=h.get("range");
            if(range!=null) {
                try {
                    if(!range.matches("bytes=[0-9]*-[0-9]*")) throw new IllegalArgumentException();
                    String[] vals=range.substring(6).split("-",-1);
                    if(vals[0].isEmpty()) start=Math.max(0,total-Long.parseLong(vals[1]));
                    else {
                        start=Long.parseLong(vals[0]);
                        if(!vals[1].isEmpty()) end=Math.min(end,Long.parseLong(vals[1]));
                    }
                    if(start>end) throw new IllegalArgumentException();
                } catch(IllegalArgumentException e) { headers(out,"416 Range Not Satisfiable",0,"Content-Range: bytes */"+total+"\r\n"); return; }
            }
            long length=end-start+1;
            headers(out,range==null?"200 OK":"206 Partial Content",length,
              "Content-Type: "+type+"\r\nAccept-Ranges: bytes\r\nCache-Control: "+(name.equals("index.html")?"no-cache":"max-age=31536000, immutable")+"\r\n"+(range==null?"":"Content-Range: bytes "+start+"-"+end+"/"+total+"\r\n"));
            if(request[0].equals("HEAD")) return;
            try(InputStream file=files.open(name)) {
                while(start>0) {
                    long n=file.skip(start);
                    if(n==0) { if(file.read()<0) throw new EOFException(); n=1; }
                    start-=n;
                }
                byte[] buf=new byte[32768];
                while(length>0) {
                    int n=file.read(buf,0,(int)Math.min(length,buf.length));
                    if(n<0) throw new EOFException();
                    out.write(buf,0,n); length-=n;
                }
            }
        } catch(IOException ignored) { /* The browser may cancel a room or media request. */ }
    }
}
