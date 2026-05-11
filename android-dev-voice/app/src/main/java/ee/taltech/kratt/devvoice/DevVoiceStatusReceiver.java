package ee.taltech.kratt.devvoice;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

import java.lang.ref.WeakReference;

public class DevVoiceStatusReceiver extends BroadcastReceiver {
    private final WeakReference<MainActivity> activityRef;

    public DevVoiceStatusReceiver(MainActivity activity) {
        this.activityRef = new WeakReference<>(activity);
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        MainActivity activity = activityRef.get();
        if (activity != null) {
            activity.handleServiceStatus(intent);
        }
    }
}
