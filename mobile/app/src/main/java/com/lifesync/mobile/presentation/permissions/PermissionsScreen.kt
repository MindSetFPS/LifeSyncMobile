package com.lifesync.mobile.presentation.permissions

import android.Manifest
import android.app.Activity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.core.app.ActivityCompat
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.lifesync.mobile.R
import com.lifesync.mobile.core.permission.HardwarePermission
import com.lifesync.mobile.core.permission.PermissionState

@Composable
fun PermissionsRoute(
    onBack: () -> Unit,
    viewModel: PermissionsViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val activity = LocalContext.current as? Activity

    // Reconciliar con el sistema al volver de Ajustes (degradación gradual).
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { viewModel.refresh() }

    val cameraLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted ->
        viewModel.onPermissionResult(
            permission = HardwarePermission.CAMERA,
            granted = granted,
            canAskAgain = activity?.let {
                ActivityCompat.shouldShowRequestPermissionRationale(it, Manifest.permission.CAMERA)
            } ?: false,
        )
    }

    val locationLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted ->
        viewModel.onPermissionResult(
            permission = HardwarePermission.LOCATION,
            granted = granted,
            canAskAgain = activity?.let {
                ActivityCompat.shouldShowRequestPermissionRationale(
                    it,
                    Manifest.permission.ACCESS_FINE_LOCATION,
                )
            } ?: false,
        )
    }

    PermissionsScreen(
        uiState = uiState,
        onRequestCamera = {
            viewModel.onRequestStarted(HardwarePermission.CAMERA)
            cameraLauncher.launch(Manifest.permission.CAMERA)
        },
        onRequestLocation = {
            viewModel.onRequestStarted(HardwarePermission.LOCATION)
            locationLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
        },
        onOpenSettings = viewModel::openAppSettings,
        onBack = onBack,
    )
}

@Composable
fun PermissionsScreen(
    uiState: PermissionsUiState,
    onRequestCamera: () -> Unit,
    onRequestLocation: () -> Unit,
    onOpenSettings: () -> Unit,
    onBack: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = stringResource(R.string.permissions_title),
            style = MaterialTheme.typography.headlineMedium,
        )
        Spacer(Modifier.height(16.dp))

        PermissionSection(
            title = stringResource(R.string.permission_camera),
            state = uiState.camera,
            consequence = stringResource(R.string.permission_camera_denied),
            onRequest = onRequestCamera,
            onOpenSettings = onOpenSettings,
        )
        Spacer(Modifier.height(12.dp))
        PermissionSection(
            title = stringResource(R.string.permission_location),
            state = uiState.location,
            consequence = stringResource(R.string.permission_location_denied),
            onRequest = onRequestLocation,
            onOpenSettings = onOpenSettings,
        )

        if (uiState.locationDegraded) {
            Spacer(Modifier.height(16.dp))
            Text(
                text = stringResource(R.string.permission_offline_mode),
                color = MaterialTheme.colorScheme.secondary,
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        Spacer(Modifier.height(24.dp))
        Button(onClick = onBack, modifier = Modifier.fillMaxWidth()) {
            Text(stringResource(R.string.back))
        }
    }
}

@Composable
private fun PermissionSection(
    title: String,
    state: PermissionState,
    consequence: String,
    onRequest: () -> Unit,
    onOpenSettings: () -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(text = title, style = MaterialTheme.typography.titleMedium)
            Text(
                text = stateLabel(state),
                style = MaterialTheme.typography.bodyMedium,
                color = when (state) {
                    is PermissionState.Granted -> MaterialTheme.colorScheme.primary
                    is PermissionState.Denied,
                    is PermissionState.PermanentlyDenied,
                    -> MaterialTheme.colorScheme.error
                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                },
            )

            when (state) {
                is PermissionState.Granted -> Unit
                is PermissionState.PermanentlyDenied -> {
                    Text(
                        text = consequence,
                        style = MaterialTheme.typography.bodySmall,
                    )
                    Button(onClick = onOpenSettings) {
                        Text(stringResource(R.string.permission_open_settings))
                    }
                }
                else -> {
                    if (state is PermissionState.Denied) {
                        Text(
                            text = consequence,
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                    Button(onClick = onRequest) {
                        Text(stringResource(R.string.permission_request))
                    }
                }
            }
        }
    }
}

@Composable
private fun stateLabel(state: PermissionState): String = when (state) {
    is PermissionState.NotRequested -> stringResource(R.string.permission_state_not_requested)
    is PermissionState.Requesting -> stringResource(R.string.permission_state_requesting)
    is PermissionState.Granted -> stringResource(R.string.permission_state_granted)
    is PermissionState.Denied -> stringResource(R.string.permission_state_denied)
    is PermissionState.PermanentlyDenied -> stringResource(R.string.permission_state_blocked)
}
