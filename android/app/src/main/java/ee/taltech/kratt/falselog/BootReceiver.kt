package ee.taltech.kratt.falselog

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.core.content.ContextCompat

/**
 * Restarts the detector service automatically on device boot, so that
 * 24/7 logging resumes after a reboot without requiring the user to
 * launch the app manually.
 *
 * The service only takes the last-known defaults here; if you need a
 * specific configuration after boot, open the app at least once to
 * persist them (post-MVP we'd store these via DataStore).
 */
class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BOOT_COMPLETED,
            Intent.ACTION_LOCKED_BOOT_COMPLETED,
            Intent.ACTION_MY_PACKAGE_REPLACED -> {
                val cfg = SettingsRepository(context).loadBlocking()
                val start = DetectorService.startIntent(
                    context = context,
                    threshold = cfg.threshold,
                    cooldownSec = cfg.cooldownSec,
                    preRollSec = cfg.preRollSec,
                    postRollSec = cfg.postRollSec,
                )
                ContextCompat.startForegroundService(context, start)
            }
        }
    }
}
