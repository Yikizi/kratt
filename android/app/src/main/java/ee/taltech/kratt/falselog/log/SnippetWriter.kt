package ee.taltech.kratt.falselog.log

import android.content.Context
import ee.taltech.kratt.falselog.audio.WavWriter
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class SnippetWriter(context: Context, private val sampleRate: Int = 16_000) {

    private val capturesDir: File = File(context.getExternalFilesDir(null), "captures").apply { mkdirs() }

    /**
     * Saves the given PCM snippet as a WAV file and returns the relative path
     * (captures/<name>.wav) that should be referenced in the log row.
     */
    fun save(pcm: ShortArray, score: Float, count: Int): String {
        val stamp = FILENAME_FMT.format(Date())
        val name = String.format(Locale.US, "%s_kuule_kratt_p%.3f_c%d.wav", stamp, score, count)
        val file = File(capturesDir, name)
        WavWriter.write(file, pcm, sampleRate)
        return "captures/" + file.name
    }

    fun capturesDir(): File = capturesDir

    companion object {
        private val FILENAME_FMT = SimpleDateFormat("yyyyMMdd_HHmmss_SSS", Locale.US)
    }
}
