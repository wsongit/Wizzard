package com.wizzard.bellwake.webxr;

import android.app.*;
import android.content.Intent;
import android.os.*;
import java.io.*;

public class GameHost extends Service {
    private static final String CHANNEL = "bellwake-game";
    private final java.util.concurrent.ExecutorService lifecycle = java.util.concurrent.Executors.newSingleThreadExecutor();
    private LocalHost server;
    @Override public void onCreate() {
        super.onCreate();
        NotificationManager manager = getSystemService(NotificationManager.class);
        manager.createNotificationChannel(new NotificationChannel(CHANNEL, "Bellwake game host", NotificationManager.IMPORTANCE_LOW));
        PendingIntent panel = PendingIntent.getActivity(this, 0, new Intent(this, Launcher.class), PendingIntent.FLAG_IMMUTABLE);
        PendingIntent stop = PendingIntent.getService(this, 1, new Intent(this, GameHost.class).setAction("stop"), PendingIntent.FLAG_IMMUTABLE);
        startForeground(1, new Notification.Builder(this, CHANNEL).setSmallIcon(android.R.drawable.ic_media_play)
                .setContentTitle("Wizzard Bellwake").setContentText("Game available in Meta Quest Browser")
                .setContentIntent(panel).setOngoing(true).addAction(0,"Stop",stop).build());
    }
    @Override public int onStartCommand(Intent intent, int flags, int id) {
        if (intent != null && "stop".equals(intent.getAction())) { stopSelf(); return START_NOT_STICKY; }
        final ResultReceiver ready = intent == null ? null : intent.getParcelableExtra("ready");
        lifecycle.execute(() -> startHost(ready, id));
        return START_STICKY;
    }
    private void startHost(ResultReceiver ready, int id) {
        int result = 1;
        if (server == null) {
            try {
                server = new LocalHost(new LocalHost.Files() {
                    public InputStream open(String name) throws IOException { return getAssets().open(name); }
                    public long size(String name) throws IOException {
                        try (android.content.res.AssetFileDescriptor f = getAssets().openFd(name)) { return f.getLength(); }
                    }
                });
            } catch (IOException e) { result = 0; }
        }
        if (ready != null) ready.send(result, null);
        if (result == 0) stopSelf(id);
    }
    @Override public IBinder onBind(Intent intent) { return null; }
    @Override public void onDestroy() {
        lifecycle.execute(() -> { if (server != null) server.close(); });
        lifecycle.shutdown();
        stopForeground(STOP_FOREGROUND_REMOVE);
        super.onDestroy();
    }
}
