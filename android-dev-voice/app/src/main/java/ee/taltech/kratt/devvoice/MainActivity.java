package ee.taltech.kratt.devvoice;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.view.Gravity;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends Activity implements TextToSpeech.OnInitListener {
    private EditText commandText;
    private TextView logView;
    private TextView partialView;
    private Button listenButton;
    private CheckBox autoDispatchBox;
    private boolean listening = false;
    private TextToSpeech tts;
    private final BroadcastReceiver statusReceiver = new DevVoiceStatusReceiver(this);
    private boolean ttsReady = false;

    private static final String TERMUX_PACKAGE = "com.termux";
    private static final String TERMUX_RUN_COMMAND_PERMISSION = "com.termux.permission.RUN_COMMAND";
    private static final String RUN_COMMAND_ACTION = "com.termux.RUN_COMMAND";
    private static final String EXTRA_PATH = "com.termux.RUN_COMMAND_PATH";
    private static final String EXTRA_ARGUMENTS = "com.termux.RUN_COMMAND_ARGUMENTS";
    private static final String EXTRA_WORKDIR = "com.termux.RUN_COMMAND_WORKDIR";
    private static final String EXTRA_BACKGROUND = "com.termux.RUN_COMMAND_BACKGROUND";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        tts = new TextToSpeech(this, this);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(32, 32, 32, 32);
        root.setGravity(Gravity.CENTER_HORIZONTAL);

        TextView title = new TextView(this);
        title.setText("Kratt Dev Voice MVP");
        title.setTextSize(24);
        title.setGravity(Gravity.CENTER_HORIZONTAL);
        root.addView(title, new LinearLayout.LayoutParams(-1, -2));

        TextView hint = new TextView(this);
        hint.setText("Bridge mode: käivita Termuxis `kratt dev-voice bridge`.\n\nForeground dictation kasutab notification + partial wakelock'i, et Android ei tapaks mikrofoni kuulamist taustal. Auto-dispatch on vaikimisi väljas: lõplik transcript pannakse tekstikasti ja saad ise bridge'i.");
        hint.setPadding(0, 24, 0, 24);
        root.addView(hint, new LinearLayout.LayoutParams(-1, -2));

        commandText = new EditText(this);
        commandText.setSingleLine(false);
        commandText.setMinLines(3);
        commandText.setText("test Android appist");
        root.addView(commandText, new LinearLayout.LayoutParams(-1, -2));

        Button bridgeButton = new Button(this);
        bridgeButton.setText("Send to localhost bridge");
        bridgeButton.setOnClickListener(v -> sendToBridge(commandText.getText().toString(), true));
        root.addView(bridgeButton, new LinearLayout.LayoutParams(-1, -2));

        listenButton = new Button(this);
        listenButton.setText("Start foreground dictation");
        listenButton.setOnClickListener(v -> toggleDictationService());
        root.addView(listenButton, new LinearLayout.LayoutParams(-1, -2));

        partialView = new TextView(this);
        partialView.setText("partial: —");
        partialView.setPadding(0, 12, 0, 12);
        root.addView(partialView, new LinearLayout.LayoutParams(-1, -2));

        autoDispatchBox = new CheckBox(this);
        autoDispatchBox.setText("Auto-dispatch final transcript to bridge while foreground service listens");
        autoDispatchBox.setChecked(false);
        root.addView(autoDispatchBox, new LinearLayout.LayoutParams(-1, -2));

        Button speakButton = new Button(this);
        speakButton.setText("Speak current text");
        speakButton.setOnClickListener(v -> speak(commandText.getText().toString()));
        root.addView(speakButton, new LinearLayout.LayoutParams(-1, -2));

        Button sendButton = new Button(this);
        sendButton.setText("Send to Termux RUN_COMMAND");
        sendButton.setOnClickListener(v -> sendToTermux(commandText.getText().toString()));
        root.addView(sendButton, new LinearLayout.LayoutParams(-1, -2));

        Button smokeButton = new Button(this);
        smokeButton.setText("Smoke: kratt dev-voice dry-run");
        smokeButton.setOnClickListener(v -> sendDryRun(commandText.getText().toString()));
        root.addView(smokeButton, new LinearLayout.LayoutParams(-1, -2));

        Button openTermuxButton = new Button(this);
        openTermuxButton.setText("Open Termux");
        openTermuxButton.setOnClickListener(v -> openTermux());
        root.addView(openTermuxButton, new LinearLayout.LayoutParams(-1, -2));

        logView = new TextView(this);
        logView.setText("Log:\n");
        ScrollView scroll = new ScrollView(this);
        scroll.addView(logView);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));

        setContentView(root);
        ensurePermissions();
        startSpeechApiService();
    }

    @Override
    protected void onStart() {
        super.onStart();
        IntentFilter filter = new IntentFilter(DevVoiceService.ACTION_STATUS);
        if (Build.VERSION.SDK_INT >= 33) {
            registerReceiver(statusReceiver, filter, Context.RECEIVER_NOT_EXPORTED);
        } else {
            registerReceiver(statusReceiver, filter);
        }
    }

    @Override
    protected void onStop() {
        try {
            unregisterReceiver(statusReceiver);
        } catch (Exception ignored) {}
        super.onStop();
    }

    @Override
    protected void onDestroy() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
            tts = null;
        }
        super.onDestroy();
    }

    @Override
    public void onInit(int status) {
        ttsReady = status == TextToSpeech.SUCCESS;
        if (ttsReady && tts != null) {
            int et = tts.setLanguage(new Locale("et", "EE"));
            if (et == TextToSpeech.LANG_MISSING_DATA || et == TextToSpeech.LANG_NOT_SUPPORTED) {
                tts.setLanguage(Locale.US);
            }
        }
    }

    private void ensurePermissions() {
        if (Build.VERSION.SDK_INT >= 23
                && checkSelfPermission(TERMUX_RUN_COMMAND_PERMISSION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{TERMUX_RUN_COMMAND_PERMISSION}, 42);
        }
        if (Build.VERSION.SDK_INT >= 23
                && checkSelfPermission(android.Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{android.Manifest.permission.RECORD_AUDIO}, 43);
        }
    }

    private void startSpeechApiService() {
        Intent intent = new Intent(this, DevVoiceService.class);
        intent.setAction(DevVoiceService.ACTION_START_API);
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(intent);
        else startService(intent);
        appendLog("speech API requested on http://127.0.0.1:8766/speak");
    }

    private void toggleDictationService() {
        ensurePermissions();
        if (Build.VERSION.SDK_INT >= 23
                && checkSelfPermission(android.Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            Toast.makeText(this, "RECORD_AUDIO permission puudub", Toast.LENGTH_LONG).show();
            return;
        }
        Intent intent = new Intent(this, DevVoiceService.class);
        if (listening) {
            intent.setAction(DevVoiceService.ACTION_STOP);
            startService(intent);
            listening = false;
            listenButton.setText("Start foreground dictation");
            appendLog("stop requested");
        } else {
            intent.setAction(DevVoiceService.ACTION_START);
            intent.putExtra(DevVoiceService.EXTRA_AUTO_DISPATCH, autoDispatchBox.isChecked());
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(intent);
            else startService(intent);
            listening = true;
            listenButton.setText("Stop foreground dictation");
            partialView.setText("partial: loading model...");
            appendLog("foreground dictation requested");
        }
    }

    void handleServiceStatus(Intent intent) {
        String kind = intent.getStringExtra(DevVoiceService.EXTRA_KIND);
        String text = intent.getStringExtra(DevVoiceService.EXTRA_TEXT);
        if (kind == null) kind = "log";
        if (text == null) text = "";
        if ("partial".equals(kind)) {
            partialView.setText("partial: " + text);
        } else if ("final".equals(kind)) {
            commandText.setText(text);
            partialView.setText("partial: —");
            appendLog("final: " + text);
        } else if ("stopped".equals(kind)) {
            listening = false;
            listenButton.setText("Start foreground dictation");
            partialView.setText("partial: —");
            appendLog("foreground dictation stopped");
        } else if ("error".equals(kind)) {
            appendLog("service error: " + text);
            Toast.makeText(MainActivity.this, text, Toast.LENGTH_LONG).show();
        } else {
            appendLog(text);
        }
    }

    private void sendDryRun(String text) {
        runTermuxCommand(new String[]{"dev-voice", "send", "--dry-run", text});
    }

    private void sendToBridge(String text, boolean speakResult) {
        if (text == null || text.trim().isEmpty()) {
            Toast.makeText(this, "Tekst puudub", Toast.LENGTH_SHORT).show();
            return;
        }
        appendLog("bridge send: " + text);
        new Thread(() -> {
            try {
                byte[] body = text.getBytes(StandardCharsets.UTF_8);
                URL url = new URL("http://127.0.0.1:8765/dispatch");
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setConnectTimeout(2000);
                conn.setReadTimeout(5000);
                conn.setDoOutput(true);
                conn.setRequestProperty("Content-Type", "text/plain; charset=utf-8");
                conn.setFixedLengthStreamingMode(body.length);
                try (OutputStream os = conn.getOutputStream()) {
                    os.write(body);
                }
                int code = conn.getResponseCode();
                conn.disconnect();
                runOnUiThread(() -> {
                    appendLog("bridge response: HTTP " + code);
                    Toast.makeText(this, "Bridge HTTP " + code, Toast.LENGTH_SHORT).show();
                    if (speakResult) speak(code >= 200 && code < 300 ? "Saadetud" : "Saatmine ebaõnnestus");
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    appendLog("bridge error: " + e.getClass().getSimpleName() + ": " + e.getMessage());
                    Toast.makeText(this, "Bridge error: " + e.getMessage(), Toast.LENGTH_LONG).show();
                    if (speakResult) speak("Bridge ei vasta");
                });
            }
        }).start();
    }

    private void sendToTermux(String text) {
        if (text == null || text.trim().isEmpty()) {
            Toast.makeText(this, "Tekst puudub", Toast.LENGTH_SHORT).show();
            return;
        }
        runTermuxCommand(new String[]{"dev-voice", "send", text});
    }

    private void runTermuxCommand(String[] args) {
        Intent intent = new Intent(RUN_COMMAND_ACTION);
        intent.setClassName(TERMUX_PACKAGE, "com.termux.app.RunCommandService");
        intent.putExtra(EXTRA_PATH, "/data/data/com.termux/files/home/kratt/cli/kratt");
        intent.putExtra(EXTRA_ARGUMENTS, args);
        intent.putExtra(EXTRA_WORKDIR, "/data/data/com.termux/files/home/kratt");
        intent.putExtra(EXTRA_BACKGROUND, false);

        try {
            startService(intent);
            appendLog("sent: kratt " + join(args));
            Toast.makeText(this, "Saadetud Termuxisse", Toast.LENGTH_SHORT).show();
            speak("Saadetud");
        } catch (SecurityException e) {
            appendLog("security error: " + e.getMessage());
            Toast.makeText(this, "Termux RUN_COMMAND permission puudu", Toast.LENGTH_LONG).show();
            speak("Õigus puudub");
        } catch (Exception e) {
            appendLog("error: " + e.getMessage());
            Toast.makeText(this, "Saatmine ebaõnnestus", Toast.LENGTH_LONG).show();
            speak("Saatmine ebaõnnestus");
        }
    }

    private void openTermux() {
        Intent launch = getPackageManager().getLaunchIntentForPackage(TERMUX_PACKAGE);
        if (launch != null) {
            startActivity(launch);
            return;
        }
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=com.termux")));
        } catch (ActivityNotFoundException ignored) {
            Toast.makeText(this, "Termux appi ei leitud", Toast.LENGTH_LONG).show();
        }
    }

    private void speak(String text) {
        if (!ttsReady || tts == null || text == null || text.trim().isEmpty()) return;
        if (Build.VERSION.SDK_INT >= 21) {
            Bundle params = new Bundle();
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, params, "kratt-dev-voice-ui-" + System.nanoTime());
        } else {
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null);
        }
    }

    private void appendLog(String message) {
        String ts = new SimpleDateFormat("HH:mm:ss", Locale.ROOT).format(new Date());
        logView.append(ts + "  " + message + "\n");
    }

    private static String join(String[] values) {
        StringBuilder out = new StringBuilder();
        for (String value : values) {
            if (out.length() > 0) out.append(' ');
            out.append(value);
        }
        return out.toString();
    }
}
