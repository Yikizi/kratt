package ee.taltech.kratt.falselog.audio

/**
 * Fixed-size circular buffer for PCM16 samples. Thread-safe via an internal
 * monitor lock. Used as the pre-roll buffer so that detections can save a
 * snippet of audio captured before the trigger point.
 */
class AudioRingBuffer(capacitySamples: Int) {

    private val buffer: ShortArray = ShortArray(capacitySamples.coerceAtLeast(1))
    private var writePos: Int = 0
    private var filled: Int = 0
    private val lock = Any()

    val capacity: Int get() = buffer.size

    /** True once the ring buffer has been written to its full capacity at least once. */
    val isFull: Boolean
        get() = synchronized(lock) { filled >= buffer.size }

    fun write(samples: ShortArray, length: Int = samples.size) {
        if (length <= 0) return
        synchronized(lock) {
            val cap = buffer.size
            if (length >= cap) {
                System.arraycopy(samples, length - cap, buffer, 0, cap)
                writePos = 0
                filled = cap
                return
            }
            val first = minOf(cap - writePos, length)
            System.arraycopy(samples, 0, buffer, writePos, first)
            val second = length - first
            if (second > 0) {
                System.arraycopy(samples, first, buffer, 0, second)
            }
            writePos = (writePos + length) % cap
            filled = minOf(cap, filled + length)
        }
    }

    /** Returns a copy of the current buffer contents in chronological order. */
    fun snapshot(): ShortArray {
        synchronized(lock) {
            val cap = buffer.size
            if (filled == 0) return ShortArray(0)
            if (filled < cap) {
                val out = ShortArray(filled)
                System.arraycopy(buffer, 0, out, 0, filled)
                return out
            }
            val out = ShortArray(cap)
            val tail = cap - writePos
            System.arraycopy(buffer, writePos, out, 0, tail)
            if (writePos > 0) {
                System.arraycopy(buffer, 0, out, tail, writePos)
            }
            return out
        }
    }

    fun clear() {
        synchronized(lock) {
            writePos = 0
            filled = 0
        }
    }
}
