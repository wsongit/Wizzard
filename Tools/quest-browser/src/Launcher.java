package com.wizzard.bellwake.webxr;

import android.app.*;
import android.content.*;
import android.net.Uri;
import android.os.*;
import android.widget.*;

public class Launcher extends Activity {
    private TextView status;
    private Button play;
    private boolean first;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(40,40,40,40);
        TextView title = new TextView(this);
        title.setText("Wizzard Bellwake");
        title.setTextSize(28);
        layout.addView(title);
        status = new TextView(this);
        status.setText("Open the adventure in Meta Quest Browser, then select Enter VR.");
        layout.addView(status);
        play = new Button(this);
        play.setText("Open Bellwake");
        play.setOnClickListener(v -> open());
        layout.addView(play);
        Button stop = new Button(this);
        stop.setText("Stop game host");
        stop.setOnClickListener(v -> {
            stopService(new Intent(this, GameHost.class));
            status.setText("Game host stopped. Open Bellwake to resume.");
        });
        layout.addView(stop);
        setContentView(layout);
        first = state == null;
    }
    @Override public void onResume() {
        super.onResume();
        if (first) { first = false; open(); }
    }
    private void open() {
        play.setEnabled(false);
        status.setText("Opening the game stored on this headset…");
        Intent host = new Intent(this, GameHost.class);
        host.putExtra("ready", new ResultReceiver(new Handler(getMainLooper())) {
            @Override protected void onReceiveResult(int result, Bundle data) {
                if (isFinishing() || isDestroyed()) return;
                play.setEnabled(true);
                if (result != 1) {
                    status.setText("Could not open the local game host. Close any other app using its port and try again.");
                    return;
                }
                try {
                    Intent browser = new Intent(Intent.ACTION_VIEW, Uri.parse(LocalHost.ORIGIN + "/"));
                    browser.setPackage("com.oculus.browser");
                    startActivity(browser);
                    status.setText("Select Enter VR in Meta Quest Browser.");
                } catch (ActivityNotFoundException e) {
                    status.setText("Install or enable Meta Quest Browser, then open Bellwake again.");
                    stopService(new Intent(Launcher.this, GameHost.class));
                }
            }
        });
        startForegroundService(host);
    }
}
