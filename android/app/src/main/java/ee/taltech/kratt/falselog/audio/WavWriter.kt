package ee.taltech.kratt.falselog.audio

import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

object WavWriter {
    fun write(file: File, pcm: ShortArray, sampleRate: Int) {
        val dataBytes = pcm.size * 2
        val totalSize = 36 + dataBytes

        file.parentFile?.mkdirs()

        FileOutputStream(file).use { fos ->
            val header = ByteBuffer.allocate(44).order(ByteOrder.LITTLE_ENDIAN)
            header.put("RIFF".toByteArray(Charsets.US_ASCII))
            header.putInt(totalSize)
            header.put("WAVE".toByteArray(Charsets.US_ASCII))
            header.put("fmt ".toByteArray(Charsets.US_ASCII))
            header.putInt(16)                              // fmt chunk size
            header.putShort(1)                             // PCM
            header.putShort(1)                             // channels
            header.putInt(sampleRate)
            header.putInt(sampleRate * 2)                  // byte rate
            header.putShort(2)                             // block align
            header.putShort(16)                            // bits per sample
            header.put("data".toByteArray(Charsets.US_ASCII))
            header.putInt(dataBytes)
            fos.write(header.array())

            val body = ByteBuffer.allocate(dataBytes).order(ByteOrder.LITTLE_ENDIAN)
            body.asShortBuffer().put(pcm)
            fos.write(body.array())
        }
    }
}
