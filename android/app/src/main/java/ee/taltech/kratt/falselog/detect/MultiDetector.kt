package ee.taltech.kratt.falselog.detect

import android.content.Context
import android.util.Log
import ee.taltech.kratt.falselog.audio.MicroFrontend

/**
 * Runs N wake word models in parallel against the same audio stream.
 * One shared [MicroFrontend] produces features; each [ModelRunner] gets
 * the same feature frames. This is efficient because feature extraction
 * is the expensive part (~0.2ms), while INT8 inference is ~0.1ms per model.
 *
 * Not thread-safe — call from a single worker thread.
 */
class MultiDetector(
    context: Context,
    modelAssets: List<String>,
) : AutoCloseable {

    private val frontend = MicroFrontend()
    val runners: List<ModelRunner> = modelAssets.map { ModelRunner(context, it) }

    /**
     * Score map: model name → latest smoothed score (or null if warming up).
     */
    data class FrameScores(
        val scores: Map<String, Float?>,
    )

    /**
     * Feed PCM16 samples. For each completed feature frame, runs all models
     * and calls [onFrameScores] with the full score map. The caller decides
     * which (if any) model triggered a detection.
     */
    fun processSamples(
        pcm: ShortArray,
        length: Int = pcm.size,
        onFrameScores: (FrameScores) -> Unit,
    ) {
        val slice = if (length == pcm.size) pcm else pcm.copyOf(length)
        val frames = frontend.process(slice)
        if (frames.isEmpty()) return

        for (frame in frames) {
            val scores = LinkedHashMap<String, Float?>(runners.size)
            for (runner in runners) {
                scores[runner.name] = runner.processFrame(frame)
            }
            // Only emit once all models have produced at least null/score
            onFrameScores(FrameScores(scores))
        }
    }

    fun reset() {
        frontend.reset()
        for (runner in runners) runner.reset()
    }

    override fun close() {
        frontend.close()
        for (runner in runners) runner.close()
    }

    companion object {
        private const val TAG = "MultiDetector"
    }
}
