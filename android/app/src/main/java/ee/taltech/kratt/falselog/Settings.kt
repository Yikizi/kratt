package ee.taltech.kratt.falselog

import android.content.Context
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking

private val Context.settingsStore by preferencesDataStore(name = "kratt_settings")

data class DetectorConfig(
    val threshold: Float = 0.85f,
    val cooldownSec: Float = 2f,
    val preRollSec: Float = 4f,
    val postRollSec: Float = 1f,
)

object SettingsKeys {
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

    /** Synchronous read for use from non-suspend contexts (e.g. BroadcastReceiver). */
    fun loadBlocking(): DetectorConfig = runBlocking {
        context.settingsStore.data.first().toConfig()
    }

    suspend fun save(config: DetectorConfig) {
        context.settingsStore.edit { prefs ->
            prefs[SettingsKeys.THRESHOLD] = config.threshold
            prefs[SettingsKeys.COOLDOWN] = config.cooldownSec
            prefs[SettingsKeys.PRE_ROLL] = config.preRollSec
            prefs[SettingsKeys.POST_ROLL] = config.postRollSec
        }
    }

    private fun Preferences.toConfig(): DetectorConfig {
        val defaults = DetectorConfig()
        return DetectorConfig(
            threshold = this[SettingsKeys.THRESHOLD] ?: defaults.threshold,
            cooldownSec = this[SettingsKeys.COOLDOWN] ?: defaults.cooldownSec,
            preRollSec = this[SettingsKeys.PRE_ROLL] ?: defaults.preRollSec,
            postRollSec = this[SettingsKeys.POST_ROLL] ?: defaults.postRollSec,
        )
    }
}
