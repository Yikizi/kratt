package ee.taltech.kratt.falselog.audio

/**
 * Thin Kotlin wrapper around the vendored tflite-micro MicroFrontend C library.
 * Matches pymicro-features defaults used by microWakeWord training.
 */
object MicroFrontendJNI {

    init {
        System.loadLibrary("krattfrontend")
    }

    @JvmStatic
    external fun nativeCreate(
        sampleRate: Int,
        windowSizeMs: Int,
        windowStepMs: Int,
        numChannels: Int,
        upperBandLimit: Float,
        lowerBandLimit: Float,
        enablePcan: Boolean,
    ): Long

    @JvmStatic
    external fun nativeDestroy(handle: Long)

    @JvmStatic
    external fun nativeReset(handle: Long)

    /**
     * Process PCM16 audio samples. Returns a flat int array containing
     * `N * numChannels` entries, where N is the number of complete feature
     * frames produced (0 if the internal window did not fill).
     */
    @JvmStatic
    external fun nativeProcess(handle: Long, pcm: ShortArray): IntArray
}

class MicroFrontend(
    val sampleRate: Int = 16_000,
    val windowSizeMs: Int = 30,
    val windowStepMs: Int = 10,
    val numChannels: Int = 40,
    val upperBandLimit: Float = 7_500f,
    val lowerBandLimit: Float = 125f,
    val enablePcan: Boolean = true,
) : AutoCloseable {

    private var handle: Long = MicroFrontendJNI.nativeCreate(
        sampleRate,
        windowSizeMs,
        windowStepMs,
        numChannels,
        upperBandLimit,
        lowerBandLimit,
        enablePcan,
    )

    init {
        require(handle != 0L) { "Failed to initialise MicroFrontend" }
    }

    fun reset() {
        if (handle != 0L) MicroFrontendJNI.nativeReset(handle)
    }

    /** Returns a list of feature frames (each of length [numChannels]). */
    fun process(pcm: ShortArray): List<IntArray> {
        if (handle == 0L || pcm.isEmpty()) return emptyList()
        val flat = MicroFrontendJNI.nativeProcess(handle, pcm)
        if (flat.isEmpty()) return emptyList()
        val frames = flat.size / numChannels
        if (frames == 0) return emptyList()
        val out = ArrayList<IntArray>(frames)
        for (f in 0 until frames) {
            val row = IntArray(numChannels)
            System.arraycopy(flat, f * numChannels, row, 0, numChannels)
            out.add(row)
        }
        return out
    }

    override fun close() {
        if (handle != 0L) {
            MicroFrontendJNI.nativeDestroy(handle)
            handle = 0L
        }
    }
}
