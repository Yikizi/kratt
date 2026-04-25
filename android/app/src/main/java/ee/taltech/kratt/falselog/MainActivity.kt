package ee.taltech.kratt.falselog

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    KrattScreen()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun KrattScreen() {
    val ctx = LocalContext.current
    val scope = rememberCoroutineScope()
    val settings = remember { SettingsRepository(ctx) }

    val running by ServiceState.running.observeAsState(false)
    val count by ServiceState.lastDetectionCount.observeAsState(0)
    val lastScore by ServiceState.lastScore.observeAsState(null)
    val lastDetectionScore by ServiceState.lastDetectionScore.observeAsState(null)
    val lastSnippet by ServiceState.lastSnippetPath.observeAsState(null)
    val lastError by ServiceState.lastError.observeAsState(null)
    val activeModel by ServiceState.activeModel.observeAsState(null)

    val availableModels = remember {
        ctx.assets.list("")?.filter { it.endsWith(".tflite") }?.sorted() ?: emptyList()
    }
    val comboPresets = remember(availableModels) {
        CONSENSUS_COMBO_PRESETS.filter { preset -> preset.modelAssets.all { it in availableModels } }
    }

    val initialConfig = remember { settings.loadBlocking() }
    var triggerMode by remember { mutableStateOf(initialConfig.triggerMode) }
    var selectedModels by remember { mutableStateOf(initialConfig.modelAssets.toSet()) }
    var selectedComboLabel by remember {
        mutableStateOf(comboPresets.firstOrNull { it.modelAssets.toSet() == selectedModels }?.label)
    }
    var threshold by remember { mutableStateOf(initialConfig.threshold.toString()) }
    var cooldownSec by remember { mutableStateOf(initialConfig.cooldownSec.toString()) }
    var preRollSec by remember { mutableStateOf(initialConfig.preRollSec.toString()) }
    var postRollSec by remember { mutableStateOf(initialConfig.postRollSec.toString()) }

    var hasMicPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(ctx, Manifest.permission.RECORD_AUDIO) ==
                PackageManager.PERMISSION_GRANTED
        )
    }
    var hasNotifPermission by remember {
        mutableStateOf(
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU)
                ContextCompat.checkSelfPermission(ctx, Manifest.permission.POST_NOTIFICATIONS) ==
                    PackageManager.PERMISSION_GRANTED
            else true
        )
    }

    val micLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted -> hasMicPermission = granted }

    val notifLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted -> hasNotifPermission = granted }

    LaunchedEffect(Unit) {
        if (!hasMicPermission) micLauncher.launch(Manifest.permission.RECORD_AUDIO)
        if (!hasNotifPermission && Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            notifLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    LaunchedEffect(triggerMode, comboPresets) {
        if (triggerMode == TriggerMode.CONSENSUS && comboPresets.isEmpty()) {
            triggerMode = TriggerMode.ANY
        }
    }

    LaunchedEffect(triggerMode) {
        if (triggerMode == TriggerMode.ANY) {
            selectedComboLabel = null
        }
    }

    LaunchedEffect(triggerMode, comboPresets, selectedComboLabel) {
        if (triggerMode == TriggerMode.CONSENSUS && comboPresets.isNotEmpty()) {
            val selected = comboPresets.firstOrNull { it.label == selectedComboLabel } ?: comboPresets.first()
            if (selectedComboLabel != selected.label) {
                selectedComboLabel = selected.label
            }
            val selectedSet = selected.modelAssets.toSet()
            if (selectedModels != selectedSet) {
                selectedModels = selectedSet
            }
        }
    }

    val selectedComboPreset = comboPresets.firstOrNull { it.label == selectedComboLabel }

    val modeOptions = buildList {
        add(TriggerMode.ANY)
        if (comboPresets.isNotEmpty()) add(TriggerMode.CONSENSUS)
    }

    val startEnabled = !running && hasMicPermission && when (triggerMode) {
        TriggerMode.ANY -> selectedModels.isNotEmpty()
        TriggerMode.CONSENSUS -> selectedComboLabel != null && selectedModels.size >= 2
    }

    Scaffold(topBar = { TopAppBar(title = { Text("Kratt False Logger") }) }) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .padding(16.dp)
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp)) {
                    Text("Status", style = MaterialTheme.typography.titleMedium)
                    Text(if (running) "● Running" else "○ Stopped")
                    Text("Trigger mode: ${triggerMode.wireValue.uppercase()}")
                    if (activeModel != null) Text("Active: $activeModel")
                    Text("Detections: $count")
                    if (lastDetectionScore != null) Text("Last detection score: %.3f".format(lastDetectionScore))
                    if (lastScore != null) Text("Live score: %.3f".format(lastScore))
                    if (lastSnippet != null) Text("Last snippet: $lastSnippet")
                    if (lastError != null) Text("Error: $lastError", color = MaterialTheme.colorScheme.error)
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Trigger mode", style = MaterialTheme.typography.titleMedium)
                    SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
                        modeOptions.forEachIndexed { index, mode ->
                            SegmentedButton(
                                shape = SegmentedButtonDefaults.itemShape(index = index, count = modeOptions.size),
                                selected = triggerMode == mode,
                                onClick = {
                                    if (!running) {
                                        triggerMode = mode
                                    }
                                },
                                enabled = !running,
                            ) {
                                Text(if (mode == TriggerMode.ANY) "ANY" else "CONSENSUS")
                            }
                        }
                    }
                    Text(
                        if (triggerMode == TriggerMode.ANY)
                            "ANY: trigger kui vähemalt üks mudel ületab thresholdi"
                        else
                            "CONSENSUS: trigger ainult kui kõik combo mudelid ületavad thresholdi"
                    )
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    if (triggerMode == TriggerMode.CONSENSUS) {
                        Text("Consensus combos (${comboPresets.size})", style = MaterialTheme.typography.titleMedium)
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalArrangement = Arrangement.spacedBy(2.dp),
                        ) {
                            comboPresets.forEach { preset ->
                                FilterChip(
                                    selected = selectedComboLabel == preset.label,
                                    onClick = {
                                        if (!running) {
                                            selectedComboLabel = preset.label
                                            selectedModels = preset.modelAssets.toSet()
                                        }
                                    },
                                    label = { Text(preset.label) },
                                    enabled = !running,
                                )
                            }
                        }
                        val comboText = selectedComboPreset
                            ?.modelAssets
                            ?.joinToString(", ") {
                                it.removeSuffix(".tflite").removePrefix("kuule_kratt_")
                            }
                        if (!comboText.isNullOrBlank()) {
                            Text("Selected combo models: $comboText")
                        }
                    } else {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                        ) {
                            Text(
                                "Models (${selectedModels.size}/${availableModels.size})",
                                style = MaterialTheme.typography.titleMedium,
                            )
                            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                TextButton(
                                    onClick = { selectedModels = availableModels.toSet() },
                                    enabled = !running,
                                ) { Text("All") }
                                TextButton(
                                    onClick = { selectedModels = emptySet() },
                                    enabled = !running,
                                ) { Text("None") }
                            }
                        }
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalArrangement = Arrangement.spacedBy(2.dp),
                        ) {
                            availableModels.forEach { model ->
                                val label = model.removeSuffix(".tflite").removePrefix("kuule_kratt_")
                                FilterChip(
                                    selected = model in selectedModels,
                                    onClick = {
                                        if (!running) {
                                            selectedModels = if (model in selectedModels) {
                                                selectedModels - model
                                            } else {
                                                selectedModels + model
                                            }
                                        }
                                    },
                                    label = { Text(label) },
                                    enabled = !running,
                                )
                            }
                        }
                    }
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                    ) {
                        Text("Configuration", style = MaterialTheme.typography.titleMedium)
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            TextButton(
                                onClick = {
                                    val c = DetectorConfig.COLLECTION
                                    threshold = c.threshold.toString()
                                    cooldownSec = c.cooldownSec.toString()
                                    preRollSec = c.preRollSec.toString()
                                    postRollSec = c.postRollSec.toString()
                                },
                                enabled = !running,
                            ) { Text("Collection") }
                            TextButton(
                                onClick = {
                                    val c = DetectorConfig.DEFAULT
                                    threshold = c.threshold.toString()
                                    cooldownSec = c.cooldownSec.toString()
                                    preRollSec = c.preRollSec.toString()
                                    postRollSec = c.postRollSec.toString()
                                },
                                enabled = !running,
                            ) { Text("Default") }
                        }
                    }
                    OutlinedTextField(
                        value = threshold,
                        onValueChange = { threshold = it },
                        label = { Text("Threshold") },
                        singleLine = true,
                        enabled = !running,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = cooldownSec,
                        onValueChange = { cooldownSec = it },
                        label = { Text("Cooldown (sec)") },
                        singleLine = true,
                        enabled = !running,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = preRollSec,
                        onValueChange = { preRollSec = it },
                        label = { Text("Pre-roll (sec)") },
                        singleLine = true,
                        enabled = !running,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = postRollSec,
                        onValueChange = { postRollSec = it },
                        label = { Text("Post-roll (sec)") },
                        singleLine = true,
                        enabled = !running,
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            }

            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Button(
                    onClick = {
                        val cfg = DetectorConfig(
                            modelAssets = selectedModels.sorted(),
                            triggerMode = triggerMode,
                            threshold = threshold.toFloatOrNull() ?: 0.85f,
                            cooldownSec = cooldownSec.toFloatOrNull() ?: 2f,
                            preRollSec = preRollSec.toFloatOrNull() ?: 4f,
                            postRollSec = postRollSec.toFloatOrNull() ?: 1f,
                        )
                        scope.launch { settings.save(cfg) }
                        val intent = DetectorService.startIntent(
                            context = ctx,
                            modelAssets = cfg.modelAssets,
                            triggerMode = cfg.triggerMode,
                            threshold = cfg.threshold,
                            cooldownSec = cfg.cooldownSec,
                            preRollSec = cfg.preRollSec,
                            postRollSec = cfg.postRollSec,
                        )
                        ContextCompat.startForegroundService(ctx, intent)
                    },
                    enabled = startEnabled,
                ) { Text("Start") }

                OutlinedButton(
                    onClick = { ctx.startService(DetectorService.stopIntent(ctx)) },
                    enabled = running,
                ) { Text("Stop") }
            }

            OutlinedButton(
                onClick = { openCapturesFolder(ctx) },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Open captures folder (Downloads/Kratt/captures)") }

            OutlinedButton(
                onClick = { openBatterySettings(ctx) },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Open battery settings (set to Unrestricted)") }

            Spacer(Modifier.height(8.dp))
            Text("WAV snippets: Downloads/Kratt/captures/", style = MaterialTheme.typography.bodySmall)
            Text(
                "Events log: Android/data/ee.taltech.kratt.falselog/files/logs/events.jsonl",
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

private fun openCapturesFolder(ctx: Context) {
    val downloadsIntent = Intent(android.app.DownloadManager.ACTION_VIEW_DOWNLOADS).apply {
        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }
    try {
        ctx.startActivity(downloadsIntent)
        return
    } catch (_: Throwable) {
        // fall through
    }

    try {
        val safIntent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            putExtra(
                "android.provider.extra.INITIAL_URI",
                Uri.parse(
                    "content://com.android.externalstorage.documents/document/" +
                        "primary%3ADownload%2FKratt%2Fcaptures"
                )
            )
        }
        ctx.startActivity(safIntent)
    } catch (_: Throwable) {
    }
}

private fun openBatterySettings(ctx: Context) {
    val pm = ctx.getSystemService(Context.POWER_SERVICE) as PowerManager
    val ignoring = pm.isIgnoringBatteryOptimizations(ctx.packageName)
    val intent = if (!ignoring) {
        Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
            data = Uri.parse("package:${ctx.packageName}")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
    } else {
        Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.parse("package:${ctx.packageName}")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
    }
    try {
        ctx.startActivity(intent)
    } catch (_: Throwable) {
    }
}
