package ee.taltech.kratt.falselog

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.core.content.ContextCompat

class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BOOT_COMPLETED,
            Intent.ACTION_LOCKED_BOOT_COMPLETED,
            Intent.ACTION_MY_PACKAGE_REPLACED -> {
                val cfg = SettingsRepository(context).loadBlocking()
                val start = DetectorService.startIntent(
                    context = context,
                    modelAssets = cfg.modelAssets,
                    triggerMode = cfg.triggerMode,
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
