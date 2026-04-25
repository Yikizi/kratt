package ee.taltech.kratt.falselog.log

import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import ee.taltech.kratt.falselog.audio.WavWriter
import java.io.File
import java.io.OutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Persists detection snippets as WAV files. On Android 10+ writes go through
 * MediaStore Downloads under the public relative path `Download/Kratt/captures/`,
 * so the user can browse and play them from any file manager without needing
 * adb. The returned `wav` field in the JSONL log is the same relative path,
 * so offline analysis can pull files via `adb pull /sdcard/<path>`.
 *
 * On API < 29 we fall back to app-specific external files (we don't support
 * those devices in production but the code path is there for the emulator).
 */
class SnippetWriter(
    private val context: Context,
    private val sampleRate: Int = 16_000,
) {

    private val captureRelativeDir: String = "Download/Kratt/captures"

    fun save(pcm: ShortArray, score: Float, count: Int, triggerModel: String = "unknown"): String {
        val stamp = FILENAME_FMT.format(Date())
        val modelTag = triggerModel.removeSuffix(".tflite").removePrefix("kuule_kratt_")
        val filename = String.format(
            Locale.US, "%s_%s_p%.3f_c%d.wav", stamp, modelTag, score, count
        )

        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            saveViaMediaStore(filename, pcm)
        } else {
            saveToAppSpecific(filename, pcm)
        }
    }

    private fun saveViaMediaStore(filename: String, pcm: ShortArray): String {
        val resolver = context.contentResolver
        val collection = MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)

        val values = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, filename)
            put(MediaStore.Downloads.MIME_TYPE, "audio/x-wav")
            put(MediaStore.Downloads.RELATIVE_PATH, captureRelativeDir)
            put(MediaStore.Downloads.IS_PENDING, 1)
        }

        val uri: Uri = resolver.insert(collection, values)
            ?: throw IllegalStateException("MediaStore.insert returned null for $filename")

        try {
            resolver.openOutputStream(uri, "w")?.use { os ->
                writeWavToStream(pcm, os)
            } ?: throw IllegalStateException("openOutputStream returned null for $uri")
        } catch (t: Throwable) {
            // Roll back the pending row so we don't leak orphan entries.
            try { resolver.delete(uri, null, null) } catch (_: Throwable) {}
            throw t
        }

        values.clear()
        values.put(MediaStore.Downloads.IS_PENDING, 0)
        resolver.update(uri, values, null, null)

        return "$captureRelativeDir/$filename"
    }

    private fun saveToAppSpecific(filename: String, pcm: ShortArray): String {
        val downloads = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        val dir = File(downloads, "Kratt/captures").apply { mkdirs() }
        val file = File(dir, filename)
        WavWriter.write(file, pcm, sampleRate)
        return "$captureRelativeDir/$filename"
    }

    private fun writeWavToStream(pcm: ShortArray, os: OutputStream) {
        // Reuse WavWriter logic by writing to a memory buffer first.
        val tempFile = File(context.cacheDir, "snippet.wav")
        try {
            WavWriter.write(tempFile, pcm, sampleRate)
            tempFile.inputStream().use { it.copyTo(os) }
        } finally {
            tempFile.delete()
        }
    }

    fun publicCapturesPath(): String = captureRelativeDir

    companion object {
        private val FILENAME_FMT = SimpleDateFormat("yyyyMMdd_HHmmss_SSS", Locale.US)
    }
}
