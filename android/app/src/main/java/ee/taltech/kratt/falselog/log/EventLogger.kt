package ee.taltech.kratt.falselog.log

import android.content.Context
import android.os.Build
import ee.taltech.kratt.falselog.TriggerMode
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

@Serializable
data class DetectionEvent(
    val ts: String,
    val trigger_model: String,
    val trigger_score: Float,
    val scores: Map<String, Float>,
    val trigger_mode: String,
    val threshold: Float,
    val cooldown_sec: Float,
    val pre_roll_sec: Float,
    val post_roll_sec: Float,
    val wav: String,
    val device: String,
    val app_version: String,
)

@Serializable
data class SessionHeader(
    val ts: String,
    val session_start: Boolean = true,
    val models: List<String>,
    val trigger_mode: String,
    val threshold: Float,
    val cooldown_sec: Float,
    val pre_roll_sec: Float,
    val post_roll_sec: Float,
    val device: String,
    val android_sdk: Int,
    val app_version: String,
)

@Serializable
data class SessionEnd(
    val ts: String,
    val session_end: Boolean = true,
    val session_start_ts: String,
    val duration_s: Double,
    val detection_count: Int,
    val app_version: String,
)

class EventLogger(context: Context) {

    private val json = Json { encodeDefaults = true }
    private val logsDir: File = File(context.getExternalFilesDir(null), "logs").apply { mkdirs() }
    private val logFile: File = File(logsDir, "events.jsonl")

    @Synchronized
    fun appendHeader(
        models: List<String>,
        triggerMode: TriggerMode,
        threshold: Float,
        cooldownSec: Float,
        preRollSec: Float,
        postRollSec: Float,
        appVersion: String,
    ) {
        val header = SessionHeader(
            ts = isoNow(),
            models = models,
            trigger_mode = triggerMode.wireValue,
            threshold = threshold,
            cooldown_sec = cooldownSec,
            pre_roll_sec = preRollSec,
            post_roll_sec = postRollSec,
            device = Build.MODEL,
            android_sdk = Build.VERSION.SDK_INT,
            app_version = appVersion,
        )
        FileWriter(logFile, true).use { w ->
            w.appendLine(json.encodeToString(SessionHeader.serializer(), header))
        }
    }

    @Synchronized
    fun appendDetection(
        triggerModel: String,
        triggerScore: Float,
        scores: Map<String, Float>,
        triggerMode: TriggerMode,
        threshold: Float,
        cooldownSec: Float,
        preRollSec: Float,
        postRollSec: Float,
        wavRelativePath: String,
        appVersion: String,
    ) {
        // Sparse: only non-zero scores to keep JSONL compact (saves ~90% when
        // most models are silent). Offline readers assume missing models = 0.
        val sparse = scores.filterValues { it > 0f }
        val evt = DetectionEvent(
            ts = isoNow(),
            trigger_model = triggerModel,
            trigger_score = triggerScore,
            scores = sparse,
            trigger_mode = triggerMode.wireValue,
            threshold = threshold,
            cooldown_sec = cooldownSec,
            pre_roll_sec = preRollSec,
            post_roll_sec = postRollSec,
            wav = wavRelativePath,
            device = Build.MODEL,
            app_version = appVersion,
        )
        FileWriter(logFile, true).use { w ->
            w.appendLine(json.encodeToString(DetectionEvent.serializer(), evt))
        }
    }

    @Synchronized
    fun appendSessionEnd(
        sessionStartTs: String,
        durationSec: Double,
        detectionCount: Int,
        appVersion: String,
    ) {
        val end = SessionEnd(
            ts = isoNow(),
            session_start_ts = sessionStartTs,
            duration_s = durationSec,
            detection_count = detectionCount,
            app_version = appVersion,
        )
        FileWriter(logFile, true).use { w ->
            w.appendLine(json.encodeToString(SessionEnd.serializer(), end))
        }
    }

    fun logFilePath(): String = logFile.absolutePath

    companion object {
        private val ISO: SimpleDateFormat by lazy {
            SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US).apply {
                timeZone = TimeZone.getTimeZone("UTC")
            }
        }

        fun isoNow(): String = ISO.format(Date())
    }
}
