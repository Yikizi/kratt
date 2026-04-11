package ee.taltech.kratt.falselog.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Wraps an [AudioRecord] instance configured for 16 kHz mono PCM16 capture,
 * delivering audio chunks on a dedicated background thread.
 */
class AudioCapture(
    private val sampleRate: Int = 16_000,
    private val frameMs: Int = 20,
    private val listener: (ShortArray, Int) -> Unit,
) {
    private val running = AtomicBoolean(false)
    private var thread: Thread? = null
    private var recorder: AudioRecord? = null

    fun start(): Boolean {
        if (running.get()) return true

        val minBufBytes = AudioRecord.getMinBufferSize(
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
        )
        if (minBufBytes <= 0) {
            Log.e(TAG, "AudioRecord.getMinBufferSize returned $minBufBytes")
            return false
        }

        // Use a generous internal buffer (~4x min) to avoid overruns.
        val internalBufBytes = maxOf(minBufBytes * 4, sampleRate * 2 / 2)

        @Suppress("MissingPermission")
        val rec = AudioRecord(
            MediaRecorder.AudioSource.VOICE_RECOGNITION,
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            internalBufBytes,
        )

        if (rec.state != AudioRecord.STATE_INITIALIZED) {
            Log.e(TAG, "AudioRecord not initialised (state=${rec.state})")
            rec.release()
            return false
        }

        recorder = rec
        running.set(true)
        rec.startRecording()

        val frameSamples = sampleRate * frameMs / 1000
        thread = Thread({
            val buf = ShortArray(frameSamples)
            while (running.get()) {
                val n = rec.read(buf, 0, buf.size, AudioRecord.READ_BLOCKING)
                if (n > 0) {
                    listener(buf, n)
                } else if (n == 0) {
                    // keep going
                } else {
                    Log.w(TAG, "AudioRecord.read returned $n")
                    break
                }
            }
        }, "kratt-audio-reader").apply {
            priority = Thread.MAX_PRIORITY - 1
            start()
        }
        return true
    }

    fun stop() {
        if (!running.compareAndSet(true, false)) return
        try {
            thread?.join(1_000)
        } catch (_: InterruptedException) {
        }
        thread = null
        try {
            recorder?.stop()
        } catch (e: Throwable) {
            Log.w(TAG, "stop(): ${e.message}")
        }
        recorder?.release()
        recorder = null
    }

    companion object {
        private const val TAG = "AudioCapture"
    }
}
