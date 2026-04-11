package ee.taltech.kratt.falselog

import androidx.lifecycle.MutableLiveData

/**
 * Process-wide observable state bridge between [DetectorService] and the UI.
 * A LiveData holder is acceptable for an MVP on a single-activity, single-user
 * app; we would move to a ViewModel/StateFlow for anything larger.
 */
object ServiceState {
    val running = MutableLiveData<Boolean>(false)
    val lastScore = MutableLiveData<Float?>(null)
    val lastDetectionCount = MutableLiveData<Int>(0)
    val lastDetectionScore = MutableLiveData<Float?>(null)
    val lastSnippetPath = MutableLiveData<String?>(null)
    val lastError = MutableLiveData<String?>(null)
}
