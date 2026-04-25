package ee.taltech.kratt.falselog.detect

import android.content.Context
import android.util.Log
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

/**
 * Runs a single microWakeWord TFLite model against pre-computed features.
 * Does NOT own a MicroFrontend — features are provided externally by
 * [MultiDetector] so they can be shared across many runners.
 *
 * Each runner maintains its own streaming state and sliding-window MA.
 */
class ModelRunner(
    context: Context,
    val name: String,
    private val featureScale: Float = 0.0390625f,
    warmupFrames: Int = 100,
    private val slidingWindowSize: Int = 5,
) : AutoCloseable {

    private val interpreter: Interpreter
    val inputScale: Float
    val inputZeroPoint: Int
    private val outputZeroPoint: Int
    val numFeatures: Int
    val framesPerStep: Int

    private var framesSeen: Int = 0
    private val initialWarmup: Int = warmupFrames

    private val inputBuffer: ByteBuffer
    private val outputBuffer: ByteBuffer

    private val scoreWindow = FloatArray(slidingWindowSize)
    private var scoreWindowPos: Int = 0
    private var scoreWindowFilled: Int = 0

    /** Last smoothed score, or null if still warming up. */
    var lastScore: Float? = null
        private set

    init {
        val mapped = loadModelFile(context, name)
        val opts = Interpreter.Options().apply {
            setNumThreads(1)  // shared across N models, keep per-model light
            setUseXNNPACK(true)
        }
        interpreter = Interpreter(mapped, opts)

        val inputTensor = interpreter.getInputTensor(0)
        val outputTensor = interpreter.getOutputTensor(0)

        val inputShape = inputTensor.shape()
        require(inputTensor.dataType() == org.tensorflow.lite.DataType.INT8) {
            "Expected int8 streaming input for $name, got ${inputTensor.dataType()}"
        }
        val qIn = inputTensor.quantizationParams()
        inputScale = qIn.scale
        inputZeroPoint = qIn.zeroPoint

        val qOut = outputTensor.quantizationParams()
        outputZeroPoint = qOut.zeroPoint

        numFeatures = inputShape.last()
        framesPerStep = inputShape[inputShape.size - 2]

        inputBuffer = ByteBuffer
            .allocateDirect(framesPerStep * numFeatures)
            .order(ByteOrder.nativeOrder())
        outputBuffer = ByteBuffer
            .allocateDirect(outputTensor.numBytes())
            .order(ByteOrder.nativeOrder())

        Log.i(TAG, "ModelRunner[$name] ready: features=$numFeatures scale=$inputScale zp=$inputZeroPoint")
    }

    /**
     * Run inference on one feature frame. Returns the smoothed score,
     * or null if still in warmup / sliding window fill phase.
     */
    fun processFrame(frame: IntArray): Float? {
        val expected = framesPerStep * numFeatures
        if (frame.size < numFeatures) return null

        inputBuffer.rewind()
        for (i in 0 until expected) {
            val f = if (i < frame.size) frame[i].toFloat() else 0f
            val scaled = f * featureScale
            var quantised = Math.round(scaled / inputScale + inputZeroPoint)
            if (quantised < -128) quantised = -128
            if (quantised > 127) quantised = 127
            inputBuffer.put(quantised.toByte())
        }
        inputBuffer.rewind()
        outputBuffer.rewind()

        interpreter.run(inputBuffer, outputBuffer)

        framesSeen += 1
        if (framesSeen <= initialWarmup) return null

        outputBuffer.rewind()
        val raw = outputBuffer.get().toInt() and 0xFF
        val rawScore = (raw - outputZeroPoint) / 255f

        scoreWindow[scoreWindowPos] = rawScore
        scoreWindowPos = (scoreWindowPos + 1) % slidingWindowSize
        if (scoreWindowFilled < slidingWindowSize) {
            scoreWindowFilled += 1
            return null
        }

        var sum = 0f
        for (v in scoreWindow) sum += v
        val smoothed = sum / slidingWindowSize
        lastScore = smoothed
        return smoothed
    }

    fun reset() {
        framesSeen = 0
        scoreWindowPos = 0
        scoreWindowFilled = 0
        lastScore = null
        for (i in scoreWindow.indices) scoreWindow[i] = 0f
        try {
            interpreter.resetVariableTensors()
        } catch (t: Throwable) {
            Log.w(TAG, "resetVariableTensors[$name]: ${t.message}")
        }
    }

    override fun close() {
        interpreter.close()
    }

    companion object {
        private const val TAG = "ModelRunner"

        private fun loadModelFile(context: Context, assetName: String): MappedByteBuffer {
            val afd = context.assets.openFd(assetName)
            FileInputStream(afd.fileDescriptor).use { fis ->
                val channel = fis.channel
                return channel.map(
                    FileChannel.MapMode.READ_ONLY,
                    afd.startOffset,
                    afd.declaredLength,
                )
            }
        }
    }
}
