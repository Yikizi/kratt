package ee.taltech.kratt.falselog.log

import android.content.Context
import android.os.Build
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
    val model: String,
    val threshold: Float,
    val score: Float,
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
    val model: String,
    val threshold: Float,
    val cooldown_sec: Float,
    val pre_roll_sec: Float,
    val post_roll_sec: Float,
    val device: String,
    val android_sdk: Int,
    val app_version: String,
)

class EventLogger(context: Context) {

    private val json = Json { encodeDefaults = true }
    private val logsDir: File = File(context.getExternalFilesDir(null), "logs").apply { mkdirs() }
    private val logFile: File = File(logsDir, "events.jsonl")

    @Synchronized
    fun appendHeader(
        model: String,
        threshold: Float,
        cooldownSec: Float,
        preRollSec: Float,
        postRollSec: Float,
        appVersion: String,
    ) {
        val header = SessionHeader(
            ts = isoNow(),
            model = model,
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
        model: String,
        threshold: Float,
        score: Float,
        cooldownSec: Float,
        preRollSec: Float,
        postRollSec: Float,
        wavRelativePath: String,
        appVersion: String,
    ) {
        val evt = DetectionEvent(
            ts = isoNow(),
            model = model,
            threshold = threshold,
            score = score,
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
