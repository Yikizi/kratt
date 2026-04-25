package ee.taltech.kratt.falselog

import android.content.Context
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking

private val Context.settingsStore by preferencesDataStore(name = "kratt_settings")

const val DEFAULT_MODEL = "kuule_kratt_v12.tflite"

enum class TriggerMode(val wireValue: String) {
    ANY("any"),
    CONSENSUS("consensus");

    companion object {
        fun fromWireValue(value: String?): TriggerMode =
            entries.firstOrNull { it.wireValue == value } ?: ANY
    }
}

data class ComboPreset(
    val label: String,
    val modelAssets: List<String>,
)

private fun assetFor(modelName: String): String = "kuule_kratt_${modelName}.tflite"

private val RAW_CONSENSUS_COMBOS: List<List<String>> = listOf(
    listOf("v14", "expert-a"),
    listOf("v14", "ex3a"),
    listOf("v14", "v6-residual"),
    listOf("v14", "expert-b2"),
    listOf("v14", "v16b"),
    listOf("v6-residual", "ex3a"),
    listOf("v6-residual", "v16b"),
    listOf("v6-residual", "expert-b2"),
    listOf("v6-residual", "expert-a", "ex3a"),
    listOf("v16b", "ex3a"),
    listOf("v16b", "expert-a"),
    listOf("v16b", "expert-b2"),
    listOf("v16a", "ex3a"),
    listOf("v16a", "expert-a"),
    listOf("v14", "ex3a", "expert-a"),
    listOf("v14", "v6-residual", "expert-a"),
    listOf("v16b", "ex3a", "expert-a"),
    listOf("v16b", "v14", "expert-a"),
    listOf("v6-residual", "v14", "ex3a"),
)

val CONSENSUS_COMBO_PRESETS: List<ComboPreset> = buildList {
    val seen = mutableSetOf<String>()
    for (combo in RAW_CONSENSUS_COMBOS) {
        val canonical = combo.sorted().joinToString("+")
        if (!seen.add(canonical)) continue
        add(
            ComboPreset(
                label = combo.joinToString(" + "),
                modelAssets = combo.map(::assetFor),
            )
        )
    }
}

data class DetectorConfig(
    val modelAssets: List<String> = listOf(DEFAULT_MODEL),
    val triggerMode: TriggerMode = TriggerMode.ANY,
    val threshold: Float = 0.85f,
    val cooldownSec: Float = 2f,
    val preRollSec: Float = 4f,
    val postRollSec: Float = 1f,
) {
    companion object {
        /** Default detection/logging preset (tight FAPH measurement). */
        val DEFAULT = DetectorConfig()

        /**
         * Recall-data collection preset. Low threshold, tiny rolls, short
         * cooldown — optimised for capturing many short "Kuule Kratt"
         * utterances from multiple speakers without overlap. Post-filter
         * with STT to separate real positives from false triggers.
         */
        val COLLECTION = DetectorConfig(
            threshold = 0.6f,
            preRollSec = 1.0f,
            postRollSec = 0.3f,
            cooldownSec = 0.5f,
        )
    }
}

object SettingsKeys {
    val MODEL_ASSETS = stringPreferencesKey("model_assets")  // comma-separated
    val TRIGGER_MODE = stringPreferencesKey("trigger_mode")
    val THRESHOLD = floatPreferencesKey("threshold")
    val COOLDOWN = floatPreferencesKey("cooldown_sec")
    val PRE_ROLL = floatPreferencesKey("pre_roll_sec")
    val POST_ROLL = floatPreferencesKey("post_roll_sec")
}

class SettingsRepository(private val context: Context) {

    val configFlow: Flow<DetectorConfig> =
        context.settingsStore.data.map { prefs -> prefs.toConfig() }

    suspend fun current(): DetectorConfig =
        context.settingsStore.data.first().toConfig()

    fun loadBlocking(): DetectorConfig = runBlocking {
        context.settingsStore.data.first().toConfig()
    }

    suspend fun save(config: DetectorConfig) {
        context.settingsStore.edit { prefs ->
            prefs[SettingsKeys.MODEL_ASSETS] = config.modelAssets.joinToString(",")
            prefs[SettingsKeys.TRIGGER_MODE] = config.triggerMode.wireValue
            prefs[SettingsKeys.THRESHOLD] = config.threshold
            prefs[SettingsKeys.COOLDOWN] = config.cooldownSec
            prefs[SettingsKeys.PRE_ROLL] = config.preRollSec
            prefs[SettingsKeys.POST_ROLL] = config.postRollSec
        }
    }

    private fun Preferences.toConfig(): DetectorConfig {
        val defaults = DetectorConfig()
        val modelsStr = this[SettingsKeys.MODEL_ASSETS]
        val models = if (modelsStr.isNullOrBlank()) defaults.modelAssets
                     else modelsStr.split(",").filter { it.isNotBlank() }
        return DetectorConfig(
            modelAssets = models,
            triggerMode = TriggerMode.fromWireValue(this[SettingsKeys.TRIGGER_MODE]),
            threshold = this[SettingsKeys.THRESHOLD] ?: defaults.threshold,
            cooldownSec = this[SettingsKeys.COOLDOWN] ?: defaults.cooldownSec,
            preRollSec = this[SettingsKeys.PRE_ROLL] ?: defaults.preRollSec,
            postRollSec = this[SettingsKeys.POST_ROLL] ?: defaults.postRollSec,
        )
    }
}
