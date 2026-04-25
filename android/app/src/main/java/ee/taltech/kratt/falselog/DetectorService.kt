package ee.taltech.kratt.falselog

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.os.SystemClock
import android.util.Log
import androidx.core.app.NotificationCompat
import ee.taltech.kratt.falselog.audio.AudioCapture
import ee.taltech.kratt.falselog.audio.AudioRingBuffer
import ee.taltech.kratt.falselog.detect.MultiDetector
import ee.taltech.kratt.falselog.log.EventLogger
import ee.taltech.kratt.falselog.log.SnippetWriter
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger

class DetectorService : Service() {

    private val workerRunning = AtomicBoolean(false)
    private val detectionCount = AtomicInteger(0)

    private var wakeLock: PowerManager.WakeLock? = null
    private lateinit var capture: AudioCapture
    private lateinit var detector: MultiDetector
    private lateinit var ringBuffer: AudioRingBuffer
    private lateinit var snippetWriter: SnippetWriter
    private lateinit var eventLogger: EventLogger

    private val audioQueue = LinkedBlockingQueue<ShortArray>()
    private var workerThread: Thread? = null

    // --- Post-roll capture bookkeeping -------------------------------------
    private data class PendingSnippet(
        val pre: ShortArray,
        val post: ArrayList<Short>,
        var remaining: Int,
        val triggerModel: String,
        val triggerScore: Float,
        val allScores: Map<String, Float>,
        val count: Int,
    )

    private var pending: PendingSnippet? = null
    @Volatile private var lastDetectionTimeMs: Long = 0

    // Session timing for accurate duration recording
    @Volatile private var sessionStartTs: String = ""
    @Volatile private var sessionStartMs: Long = 0

    // --- Config ------------------------------------------------------------
    private val sampleRate: Int = 16_000
    @Volatile private var threshold: Float = 0.85f
    @Volatile private var cooldownSec: Float = 2f
    @Volatile private var preRollSec: Float = 4f
    @Volatile private var postRollSec: Float = 1f
    @Volatile private var modelAssets: List<String> = listOf(DEFAULT_MODEL)
    @Volatile private var triggerMode: TriggerMode = TriggerMode.ANY
    private val appVersion: String = "0.3.0"

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        ServiceState.running.postValue(false)
        createChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action ?: ACTION_START
        when (action) {
            ACTION_STOP -> {
                stopWorker()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
                return START_NOT_STICKY
            }
        }

        applyConfig(intent)
        startForegroundSafely()
        startWorker()
        return START_STICKY
    }

    override fun onDestroy() {
        stopWorker()
        ServiceState.running.postValue(false)
        super.onDestroy()
    }

    // -----------------------------------------------------------------------
    // Worker lifecycle
    // -----------------------------------------------------------------------

    private fun applyConfig(intent: Intent?) {
        intent ?: return
        intent.getStringArrayExtra(EXTRA_MODELS)?.toList()?.let { modelAssets = it }
        if (intent.hasExtra(EXTRA_TRIGGER_MODE)) {
            triggerMode = TriggerMode.fromWireValue(intent.getStringExtra(EXTRA_TRIGGER_MODE))
        }
        if (intent.hasExtra(EXTRA_THRESHOLD)) {
            threshold = intent.getFloatExtra(EXTRA_THRESHOLD, threshold)
        }
        if (intent.hasExtra(EXTRA_COOLDOWN)) {
            cooldownSec = intent.getFloatExtra(EXTRA_COOLDOWN, cooldownSec)
        }
        if (intent.hasExtra(EXTRA_PRE_ROLL)) {
            preRollSec = intent.getFloatExtra(EXTRA_PRE_ROLL, preRollSec)
        }
        if (intent.hasExtra(EXTRA_POST_ROLL)) {
            postRollSec = intent.getFloatExtra(EXTRA_POST_ROLL, postRollSec)
        }
    }

    private fun startWorker() {
        if (workerRunning.get()) return
        workerRunning.set(true)

        acquireWakeLock()

        ringBuffer = AudioRingBuffer((sampleRate * preRollSec).toInt())
        snippetWriter = SnippetWriter(this, sampleRate)
        eventLogger = EventLogger(this)

        sessionStartTs = ee.taltech.kratt.falselog.log.EventLogger.isoNow()
        sessionStartMs = SystemClock.elapsedRealtime()
        detectionCount.set(0)

        eventLogger.appendHeader(
            models = modelAssets,
            triggerMode = triggerMode,
            threshold = threshold,
            cooldownSec = cooldownSec,
            preRollSec = preRollSec,
            postRollSec = postRollSec,
            appVersion = appVersion,
        )

        detector = MultiDetector(this, modelAssets)

        capture = AudioCapture(sampleRate = sampleRate, frameMs = 20) { buf, len ->
            val copy = buf.copyOf(len)
            ringBuffer.write(copy, len)
            capturePost(copy, len)
            audioQueue.offer(copy)
        }
        if (!capture.start()) {
            Log.e(TAG, "capture.start() failed")
            ServiceState.lastError.postValue("AudioRecord failed to initialise")
            stopWorker()
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
            return
        }

        workerThread = Thread({
            Log.i(TAG, "detector worker started with ${modelAssets.size} models")
            while (workerRunning.get()) {
                val chunk = try {
                    audioQueue.take()
                } catch (_: InterruptedException) {
                    break
                }
                try {
                    detector.processSamples(chunk) { frameScores ->
                        maybeTriggerDetection(frameScores)
                    }
                } catch (t: Throwable) {
                    Log.e(TAG, "processSamples threw", t)
                    ServiceState.lastError.postValue("detector crash: ${t.message}")
                }
            }
            Log.i(TAG, "detector worker stopped")
        }, "kratt-detector-worker").apply {
            priority = Thread.MAX_PRIORITY - 1
            start()
        }

        val active = when (triggerMode) {
            TriggerMode.ANY -> if (modelAssets.size == 1) modelAssets[0] else "${modelAssets.size} models"
            TriggerMode.CONSENSUS -> modelAssets
                .joinToString(" + ") { it.removeSuffix(".tflite").removePrefix("kuule_kratt_") }
        }
        ServiceState.activeModel.postValue(active)
        ServiceState.running.postValue(true)
    }

    private fun stopWorker() {
        if (!workerRunning.compareAndSet(true, false)) return
        try { capture.stop() } catch (_: Throwable) {}
        audioQueue.clear()
        workerThread?.interrupt()
        try { workerThread?.join(1_500) } catch (_: InterruptedException) {}
        workerThread = null
        try { detector.close() } catch (_: Throwable) {}

        // Log accurate session end + duration before releasing resources
        if (sessionStartMs > 0 && ::eventLogger.isInitialized) {
            val durationS = (SystemClock.elapsedRealtime() - sessionStartMs) / 1000.0
            try {
                eventLogger.appendSessionEnd(
                    sessionStartTs = sessionStartTs,
                    durationSec = durationS,
                    detectionCount = detectionCount.get(),
                    appVersion = appVersion,
                )
            } catch (t: Throwable) {
                Log.w(TAG, "session_end append failed: ${t.message}")
            }
        }

        releaseWakeLock()
        ServiceState.running.postValue(false)
    }

    // -----------------------------------------------------------------------
    // Detection handling
    // -----------------------------------------------------------------------

    private fun maybeTriggerDetection(frameScores: MultiDetector.FrameScores) {
        // Find best-scoring model and collect non-null scores
        var bestModel: String? = null
        var bestScore = 0f
        val allScores = LinkedHashMap<String, Float>()

        for ((model, score) in frameScores.scores) {
            if (score != null) {
                allScores[model] = score
                if (score > bestScore) {
                    bestScore = score
                    bestModel = model
                }
            }
        }

        if (bestModel != null) {
            ServiceState.lastScore.postValue(bestScore)
        }

        // Suppress until ring buffer is full
        if (!ringBuffer.isFull) return

        val now = SystemClock.elapsedRealtime()
        val inCooldown = (now - lastDetectionTimeMs) < (cooldownSec * 1000).toLong()
        if (inCooldown) return

        val shouldTrigger = when (triggerMode) {
            TriggerMode.ANY -> bestModel != null && bestScore > threshold
            TriggerMode.CONSENSUS ->
                allScores.isNotEmpty() && allScores.size == modelAssets.size &&
                    allScores.values.all { it > threshold }
        }
        if (!shouldTrigger || bestModel == null) return

        val triggerLabel = when (triggerMode) {
            TriggerMode.ANY -> bestModel
            TriggerMode.CONSENSUS -> modelAssets.joinToString("+")
        }

        lastDetectionTimeMs = now
        val count = detectionCount.incrementAndGet()

        val pre = ringBuffer.snapshot()
        val postSamples = (postRollSec * sampleRate).toInt()
        synchronized(this) {
            pending = PendingSnippet(
                pre = pre,
                post = ArrayList(postSamples + 512),
                remaining = postSamples,
                triggerModel = triggerLabel,
                triggerScore = bestScore,
                allScores = allScores,
                count = count,
            )
        }

        ServiceState.lastDetectionCount.postValue(count)
        ServiceState.lastDetectionScore.postValue(bestScore)
        Log.i(
            TAG,
            "DETECTED mode=${triggerMode.wireValue} model=$triggerLabel score=$bestScore count=$count " +
                "scores=${allScores.entries.joinToString { "${it.key.removeSuffix(".tflite")}=%.3f".format(it.value) }}"
        )

        if (postSamples == 0) {
            finalizePending()
        }
    }

    private fun capturePost(buf: ShortArray, len: Int) {
        val snap = synchronized(this) { pending } ?: return
        if (snap.remaining <= 0) return
        val take = minOf(snap.remaining, len)
        for (i in 0 until take) snap.post.add(buf[i])
        snap.remaining -= take
        if (snap.remaining <= 0) {
            finalizePending()
        }
    }

    private fun finalizePending() {
        val snap = synchronized(this) {
            val p = pending
            pending = null
            p
        } ?: return

        val pcm = ShortArray(snap.pre.size + snap.post.size)
        System.arraycopy(snap.pre, 0, pcm, 0, snap.pre.size)
        for (i in snap.post.indices) pcm[snap.pre.size + i] = snap.post[i]

        val wavRelativePath = try {
            snippetWriter.save(pcm, snap.triggerScore, snap.count, snap.triggerModel)
        } catch (t: Throwable) {
            Log.e(TAG, "wav save failed", t)
            ServiceState.lastError.postValue("wav save failed: ${t.message}")
            return
        }

        try {
            eventLogger.appendDetection(
                triggerModel = snap.triggerModel,
                triggerScore = snap.triggerScore,
                scores = snap.allScores,
                triggerMode = triggerMode,
                threshold = threshold,
                cooldownSec = cooldownSec,
                preRollSec = preRollSec,
                postRollSec = postRollSec,
                wavRelativePath = wavRelativePath,
                appVersion = appVersion,
            )
        } catch (t: Throwable) {
            Log.e(TAG, "jsonl append failed", t)
            ServiceState.lastError.postValue("jsonl append failed: ${t.message}")
        }

        ServiceState.lastSnippetPath.postValue(wavRelativePath)
    }

    // -----------------------------------------------------------------------
    // Foreground / notifications
    // -----------------------------------------------------------------------

    private fun startForegroundSafely() {
        val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        val intent = Intent(this, MainActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
        }
        val pi = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )

        val n: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.service_notification_title))
            .setContentText(getString(R.string.service_notification_text))
            .setSmallIcon(android.R.drawable.presence_audio_online)
            .setOngoing(true)
            .setContentIntent(pi)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .build()

        nm.createNotificationChannel(
            NotificationChannel(
                CHANNEL_ID,
                getString(R.string.service_channel_name),
                NotificationManager.IMPORTANCE_LOW,
            ).apply {
                description = getString(R.string.service_channel_desc)
                setShowBadge(false)
            }
        )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTIFICATION_ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        } else {
            startForeground(NOTIFICATION_ID, n)
        }
    }

    private fun createChannel() {
        val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        if (nm.getNotificationChannel(CHANNEL_ID) == null) {
            nm.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_ID,
                    getString(R.string.service_channel_name),
                    NotificationManager.IMPORTANCE_LOW,
                ).apply {
                    description = getString(R.string.service_channel_desc)
                    setShowBadge(false)
                }
            )
        }
    }

    private fun acquireWakeLock() {
        if (wakeLock?.isHeld == true) return
        val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
        val wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "kratt:detector")
        wl.setReferenceCounted(false)
        wl.acquire(24L * 60 * 60 * 1000) // 24h safety upper bound
        wakeLock = wl
    }

    private fun releaseWakeLock() {
        try { wakeLock?.release() } catch (_: Throwable) {}
        wakeLock = null
    }

    companion object {
        private const val TAG = "DetectorService"
        private const val CHANNEL_ID = "kratt_detector"
        private const val NOTIFICATION_ID = 4321

        const val ACTION_START = "ee.taltech.kratt.falselog.action.START"
        const val ACTION_STOP = "ee.taltech.kratt.falselog.action.STOP"

        const val EXTRA_MODELS = "models"
        const val EXTRA_TRIGGER_MODE = "trigger_mode"
        const val EXTRA_THRESHOLD = "threshold"
        const val EXTRA_COOLDOWN = "cooldown"
        const val EXTRA_PRE_ROLL = "pre_roll"
        const val EXTRA_POST_ROLL = "post_roll"

        fun startIntent(
            context: Context,
            modelAssets: List<String>,
            triggerMode: TriggerMode,
            threshold: Float,
            cooldownSec: Float,
            preRollSec: Float,
            postRollSec: Float,
        ): Intent = Intent(context, DetectorService::class.java).apply {
            action = ACTION_START
            putExtra(EXTRA_MODELS, modelAssets.toTypedArray())
            putExtra(EXTRA_TRIGGER_MODE, triggerMode.wireValue)
            putExtra(EXTRA_THRESHOLD, threshold)
            putExtra(EXTRA_COOLDOWN, cooldownSec)
            putExtra(EXTRA_PRE_ROLL, preRollSec)
            putExtra(EXTRA_POST_ROLL, postRollSec)
        }

        fun stopIntent(context: Context): Intent = Intent(context, DetectorService::class.java).apply {
            action = ACTION_STOP
        }
    }
}
