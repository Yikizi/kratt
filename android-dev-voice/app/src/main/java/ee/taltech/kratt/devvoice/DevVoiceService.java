package ee.taltech.kratt.devvoice;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.IBinder;
import android.os.PowerManager;
import android.speech.tts.TextToSpeech;

import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicBoolean;

import com.k2fsa.sherpa.onnx.FeatureConfig;
import com.k2fsa.sherpa.onnx.OnlineModelConfig;
import com.k2fsa.sherpa.onnx.OnlineRecognizer;
import com.k2fsa.sherpa.onnx.OnlineRecognizerConfig;
import com.k2fsa.sherpa.onnx.OnlineRecognizerResult;
import com.k2fsa.sherpa.onnx.OnlineStream;
import com.k2fsa.sherpa.onnx.OnlineTransducerModelConfig;

public class DevVoiceService extends Service implements TextToSpeech.OnInitListener {
    public static final String ACTION_START = "ee.taltech.kratt.devvoice.START";
    public static final String ACTION_START_API = "ee.taltech.kratt.devvoice.START_API";
    public static final String ACTION_STOP = "ee.taltech.kratt.devvoice.STOP";
    public static final String ACTION_STATUS = "ee.taltech.kratt.devvoice.STATUS";
    public static final String EXTRA_AUTO_DISPATCH = "auto_dispatch";
    public static final String EXTRA_KIND = "kind";
    public static final String EXTRA_TEXT = "text";

    private static final String CHANNEL_ID = "kratt_dev_voice_listening";
    private static final int NOTIFICATION_ID = 1001;
    private static final String BRIDGE_URL = "http://127.0.0.1:8765/dispatch";
    private static final int SPEAK_PORT = 8766;

    private final AtomicBoolean listening = new AtomicBoolean(false);
    private Thread listenThread;
    private Thread speakServerThread;
    private ServerSocket speakServerSocket;
    private OnlineRecognizer recognizer;
    private OnlineStream stream;
    private PowerManager.WakeLock wakeLock;
    private TextToSpeech tts;
    private volatile boolean ttsReady = false;
    private volatile boolean autoDispatch = false;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        tts = new TextToSpeech(this, this);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String action = intent == null ? ACTION_START : intent.getAction();
        if (ACTION_STOP.equals(action)) {
            stopListening();
            stopSpeakServer();
            stopSelf();
            return START_NOT_STICKY;
        }
        if (ACTION_START_API.equals(action)) {
            startForeground(NOTIFICATION_ID, buildNotification("Kõne API valmis: http://127.0.0.1:8766/speak"));
            startSpeakServer();
            return START_STICKY;
        }
        autoDispatch = intent != null && intent.getBooleanExtra(EXTRA_AUTO_DISPATCH, false);
        startForeground(NOTIFICATION_ID, buildNotification("Kuulan..."));
        startSpeakServer();
        startListening();
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        stopListening();
        stopSpeakServer();
        if (tts != null) {
            tts.stop();
            tts.shutdown();
            tts = null;
        }
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
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

    private synchronized void startSpeakServer() {
        if (speakServerThread != null && speakServerThread.isAlive()) return;
        speakServerThread = new Thread(this::runSpeakServer, "kratt-dev-voice-speak-api");
        speakServerThread.start();
    }

    private synchronized void stopSpeakServer() {
        try {
            if (speakServerSocket != null) speakServerSocket.close();
        } catch (Exception ignored) {}
        speakServerSocket = null;
        speakServerThread = null;
    }

    private void runSpeakServer() {
        try (ServerSocket server = new ServerSocket(SPEAK_PORT)) {
            speakServerSocket = server;
            sendStatus("log", "speak API listening on http://127.0.0.1:" + SPEAK_PORT + "/speak");
            while (!server.isClosed()) {
                try (Socket socket = server.accept()) {
                    handleSpeakApiClient(socket);
                } catch (Exception e) {
                    sendStatus("error", "speak API client error: " + e.getClass().getSimpleName() + ": " + e.getMessage());
                }
            }
        } catch (Exception e) {
            sendStatus("error", "speak API error: " + e.getClass().getSimpleName() + ": " + e.getMessage());
        }
    }

    private void handleSpeakApiClient(Socket socket) throws Exception {
        socket.setSoTimeout(5000);
        ByteArrayOutputStream raw = new ByteArrayOutputStream();
        byte[] one = new byte[1];
        byte[] bytes;
        while (socket.getInputStream().read(one) == 1) {
            raw.write(one[0]);
            bytes = raw.toByteArray();
            int n = bytes.length;
            if (n >= 4 && bytes[n - 4] == '\r' && bytes[n - 3] == '\n' && bytes[n - 2] == '\r' && bytes[n - 1] == '\n') {
                break;
            }
        }
        String header = raw.toString("UTF-8");
        String[] lines = header.split("\\r?\\n");
        if (lines.length == 0) return;
        String requestLine = lines[0];
        int contentLength = 0;
        for (String line : lines) {
            String lower = line.toLowerCase(Locale.ROOT);
            if (lower.startsWith("content-length:")) {
                try {
                    contentLength = Integer.parseInt(line.substring(line.indexOf(':') + 1).trim());
                } catch (NumberFormatException ignored) {}
            }
        }
        String[] parts = requestLine.split(" ");
        String method = parts.length > 0 ? parts[0] : "";
        String path = parts.length > 1 ? parts[1] : "";
        if ("GET".equals(method) && "/health".equals(path)) {
            writeHttp(socket, 200, "text/plain; charset=utf-8", "ok\n");
            return;
        }
        if (!"POST".equals(method) || !"/speak".equals(path)) {
            writeHttp(socket, 404, "text/plain; charset=utf-8", "not found\n");
            return;
        }
        byte[] body = new byte[Math.max(contentLength, 0)];
        int read = 0;
        while (read < body.length) {
            int n = socket.getInputStream().read(body, read, body.length - read);
            if (n < 0) break;
            read += n;
        }
        String text = new String(body, 0, read, StandardCharsets.UTF_8).trim();
        if (text.isEmpty()) {
            writeHttp(socket, 400, "text/plain; charset=utf-8", "empty text\n");
            return;
        }
        speak(text);
        sendStatus("log", "speak API: " + text);
        writeHttp(socket, 204, "text/plain; charset=utf-8", "");
    }

    private void writeHttp(Socket socket, int code, String contentType, String body) throws Exception {
        byte[] payload = body.getBytes(StandardCharsets.UTF_8);
        String reason = code == 204 ? "No Content" : code == 200 ? "OK" : code == 400 ? "Bad Request" : "Not Found";
        String head = "HTTP/1.1 " + code + " " + reason + "\r\n"
                + "Content-Type: " + contentType + "\r\n"
                + "Content-Length: " + payload.length + "\r\n"
                + "Connection: close\r\n\r\n";
        OutputStream out = socket.getOutputStream();
        out.write(head.getBytes(StandardCharsets.UTF_8));
        out.write(payload);
        out.flush();
    }

    private void startListening() {
        if (!listening.compareAndSet(false, true)) return;
        acquireWakeLock();
        speak("Kuulan");
        sendStatus("log", "foreground service started; auto-dispatch=" + autoDispatch);
        listenThread = new Thread(this::runDictationLoop, "kratt-dev-voice-service-stt");
        listenThread.start();
    }

    private void stopListening() {
        if (!listening.getAndSet(false)) return;
        sendStatus("log", "foreground service stopping");
        speak("Lõpetan kuulamise");
        releaseWakeLock();
    }

    private void runDictationLoop() {
        final int sampleRate = 16000;
        AudioRecord recorder = null;
        try {
            ensureRecognizer(sampleRate);
            stream = recognizer.createStream("");
            int minBuffer = AudioRecord.getMinBufferSize(
                    sampleRate,
                    AudioFormat.CHANNEL_IN_MONO,
                    AudioFormat.ENCODING_PCM_16BIT
            );
            int bufferSamples = Math.max(sampleRate / 10, minBuffer / 2);
            short[] pcm = new short[bufferSamples];
            float[] samples = new float[bufferSamples];
            recorder = new AudioRecord(
                    MediaRecorder.AudioSource.VOICE_RECOGNITION,
                    sampleRate,
                    AudioFormat.CHANNEL_IN_MONO,
                    AudioFormat.ENCODING_PCM_16BIT,
                    Math.max(minBuffer, bufferSamples * 2)
            );
            recorder.startRecording();
            sendStatus("log", "dictation started in foreground service");
            String last = "";
            while (listening.get()) {
                int n = recorder.read(pcm, 0, pcm.length);
                if (n <= 0) continue;
                if (samples.length != n) samples = new float[n];
                for (int i = 0; i < n; i++) samples[i] = pcm[i] / 32768.0f;
                stream.acceptWaveform(samples, sampleRate);
                while (recognizer.isReady(stream)) recognizer.decode(stream);
                OnlineRecognizerResult result = recognizer.getResult(stream);
                String text = result.getText().trim();
                if (!text.equals(last)) {
                    last = text;
                    String display = text.isEmpty() ? "listening..." : text;
                    sendStatus("partial", display);
                    updateNotification(display);
                }
                if (recognizer.isEndpoint(stream)) {
                    if (!text.isEmpty()) {
                        handleFinalTranscript(text);
                    }
                    recognizer.reset(stream);
                    last = "";
                }
            }
        } catch (Throwable t) {
            sendStatus("error", t.getClass().getSimpleName() + ": " + t.getMessage());
            speak("Viga kuulamisel");
        } finally {
            try {
                if (recorder != null) {
                    recorder.stop();
                    recorder.release();
                }
            } catch (Exception ignored) {}
            releaseWakeLock();
            sendStatus("stopped", "");
            stopForeground(true);
        }
    }

    private void ensureRecognizer(int sampleRate) {
        if (recognizer != null) return;
        FeatureConfig feat = new FeatureConfig();
        feat.setSampleRate(sampleRate);
        feat.setFeatureDim(80);

        OnlineTransducerModelConfig transducer = new OnlineTransducerModelConfig();
        transducer.setEncoder("sherpa/encoder.int8.onnx");
        transducer.setDecoder("sherpa/decoder.int8.onnx");
        transducer.setJoiner("sherpa/joiner.int8.onnx");

        OnlineModelConfig model = new OnlineModelConfig();
        model.setTransducer(transducer);
        model.setTokens("sherpa/tokens.txt");
        model.setNumThreads(2);
        model.setProvider("cpu");

        OnlineRecognizerConfig config = new OnlineRecognizerConfig();
        config.setFeatConfig(feat);
        config.setModelConfig(model);
        config.setEnableEndpoint(true);
        config.setDecodingMethod("greedy_search");
        recognizer = new OnlineRecognizer(getAssets(), config);
    }

    private void handleFinalTranscript(String text) {
        sendStatus("final", text);
        if (autoDispatch) {
            dispatchToBridge(text);
        } else {
            sendStatus("log", "auto-dispatch off; open app and press Send to bridge");
        }
    }

    private void dispatchToBridge(String text) {
        new Thread(() -> {
            try {
                byte[] body = text.getBytes(StandardCharsets.UTF_8);
                URL url = new URL(BRIDGE_URL);
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
                sendStatus("log", "bridge response: HTTP " + code);
                if (code >= 200 && code < 300) speak("Saadetud");
                else speak("Saatmine ebaõnnestus");
            } catch (Exception e) {
                sendStatus("error", "bridge error: " + e.getClass().getSimpleName() + ": " + e.getMessage());
                speak("Bridge ei vasta");
            }
        }, "kratt-dev-voice-bridge-dispatch").start();
    }

    private void sendStatus(String kind, String text) {
        Intent status = new Intent(ACTION_STATUS);
        status.setPackage(getPackageName());
        status.putExtra(EXTRA_KIND, kind);
        status.putExtra(EXTRA_TEXT, text == null ? "" : text);
        sendBroadcast(status);
    }

    private void acquireWakeLock() {
        if (wakeLock != null && wakeLock.isHeld()) return;
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "KrattDevVoice::listen");
        wakeLock.setReferenceCounted(false);
        wakeLock.acquire(60 * 60 * 1000L);
    }

    private void releaseWakeLock() {
        try {
            if (wakeLock != null && wakeLock.isHeld()) wakeLock.release();
        } catch (Exception ignored) {}
    }

    private void speak(String text) {
        if (!ttsReady || tts == null || text == null || text.isEmpty()) return;
        if (Build.VERSION.SDK_INT >= 21) {
            Bundle params = new Bundle();
            tts.speak(text, TextToSpeech.QUEUE_ADD, params, "kratt-dev-voice-" + System.nanoTime());
        } else {
            tts.speak(text, TextToSpeech.QUEUE_ADD, null);
        }
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "Kratt Dev Voice listening",
                NotificationManager.IMPORTANCE_LOW
        );
        channel.setDescription("Keeps Kratt Dev Voice microphone dictation alive in the background");
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        nm.createNotificationChannel(channel);
    }

    private Notification buildNotification(String text) {
        Intent openIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                this,
                0,
                openIntent,
                Build.VERSION.SDK_INT >= 23 ? PendingIntent.FLAG_IMMUTABLE : 0
        );
        Notification.Builder builder = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(this, CHANNEL_ID)
                : new Notification.Builder(this);
        builder.setContentTitle("Kratt Dev Voice kuulab")
                .setContentText(text)
                .setSmallIcon(android.R.drawable.ic_btn_speak_now)
                .setOngoing(true)
                .setContentIntent(pendingIntent);
        return builder.build();
    }

    private void updateNotification(String text) {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        nm.notify(NOTIFICATION_ID, buildNotification(text));
    }
}
