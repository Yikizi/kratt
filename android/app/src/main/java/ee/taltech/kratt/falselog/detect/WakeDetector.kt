package ee.taltech.kratt.falselog.detect

import android.content.Context
import android.util.Log
import ee.taltech.kratt.falselog.audio.MicroFrontend
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

/**
 * Wraps the streaming microWakeWord TFLite model + a C `MicroFrontend` feature
 * extractor. Feed PCM16 samples via [processSamples]; the callback runs once per
 * invocation whenever a frame's score crosses the threshold (cooldown-aware).
 *
 * The model is stateful — the interpreter holds state tensors between
 * invocations, so this class is NOT thread-safe and must be called from a
 * single worker thread.
 */
class WakeDetector(
    context: Context,
    modelAsset: String = "kuule_kratt_v9.tflite",
    private val featureScale: Float = 0.0390625f,
    warmupFrames: Int = 50,
) : AutoCloseable {

    private val frontend = MicroFrontend()
    private val interpreter: Interpreter
    private val inputShape: IntArray
    private val inputScale: Float
    private val inputZeroPoint: Int
    private val outputZeroPoint: Int
    private val numFeatures: Int
    private val framesPerStep: Int

    private var framesSeen: Int = 0
    private val initialWarmup: Int = warmupFrames

    private val inputBuffer: ByteBuffer
    private val outputBuffer: ByteBuffer

    init {
        val mapped = loadModelFile(context, modelAsset)
        val opts = Interpreter.Options().apply {
            setNumThreads(2)
            setUseXNNPACK(true)
        }
        interpreter = Interpreter(mapped, opts)

        val inputTensor = interpreter.getInputTensor(0)
        val outputTensor = interpreter.getOutputTensor(0)

        inputShape = inputTensor.shape()
        require(inputTensor.dataType() == org.tensorflow.lite.DataType.INT8) {
            "Expected int8 streaming input, got ${inputTensor.dataType()}"
        }
        val qIn = inputTensor.quantizationParams()
        inputScale = qIn.scale
        inputZeroPoint = qIn.zeroPoint

        val qOut = outputTensor.quantizationParams()
        outputZeroPoint = qOut.zeroPoint

        // Expected shape [1,1,40] → framesPerStep=1, numFeatures=40.
        numFeatures = inputShape.last()
        framesPerStep = inputShape[inputShape.size - 2]

        inputBuffer = ByteBuffer
            .allocateDirect(framesPerStep * numFeatures)
            .order(ByteOrder.nativeOrder())
        outputBuffer = ByteBuffer
            .allocateDirect(outputTensor.numBytes())
            .order(ByteOrder.nativeOrder())

        Log.i(
            TAG,
            "WakeDetector ready: input=${inputShape.toList()} scale=$inputScale zp=$inputZeroPoint " +
                "outScale=${qOut.scale} outZp=$outputZeroPoint numFeatures=$numFeatures framesPerStep=$framesPerStep"
        )
    }

    /** Runs feature extraction + one inference per completed frame. */
    fun processSamples(
        pcm: ShortArray,
        length: Int = pcm.size,
        onScore: (Float) -> Unit,
    ) {
        val slice = if (length == pcm.size) pcm else pcm.copyOf(length)
        val frames = frontend.process(slice)
        if (frames.isEmpty()) return

        for (frame in frames) {
            // Feature shape must match what the model expects.
            val expected = framesPerStep * numFeatures
            if (frame.size < numFeatures) continue

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
            if (framesSeen <= initialWarmup) continue

            outputBuffer.rewind()
            val raw = outputBuffer.get().toInt() and 0xFF
            val score = (raw - outputZeroPoint) / 255f
            onScore(score)
        }
    }

    fun reset() {
        framesSeen = 0
        frontend.reset()
        try {
            interpreter.resetVariableTensors()
        } catch (t: Throwable) {
            Log.w(TAG, "resetVariableTensors: ${t.message}")
        }
    }

    override fun close() {
        frontend.close()
        interpreter.close()
    }

    companion object {
        private const val TAG = "WakeDetector"

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
