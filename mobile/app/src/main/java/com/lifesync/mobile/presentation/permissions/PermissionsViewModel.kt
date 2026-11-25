package com.lifesync.mobile.presentation.permissions

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.Settings
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModel
import com.lifesync.mobile.core.permission.HardwarePermission
import com.lifesync.mobile.core.permission.HardwarePermissionStateMachine
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import javax.inject.Inject

/** Orquesta la máquina de estados de permisos y la reconcilia con el sistema. */
@HiltViewModel
class PermissionsViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel() {

    private val machines: Map<HardwarePermission, HardwarePermissionStateMachine> =
        HardwarePermission.entries.associateWith { HardwarePermissionStateMachine() }

    private val _uiState = MutableStateFlow(PermissionsUiState())
    val uiState: StateFlow<PermissionsUiState> = _uiState.asStateFlow()

    init {
        refresh()
    }

    /** Reconcilia cada máquina con `checkSelfPermission` (al abrir o volver de Ajustes). */
    fun refresh() {
        HardwarePermission.entries.forEach { permission ->
            val granted = ContextCompat.checkSelfPermission(
                context,
                permission.manifestPermission,
            ) == PackageManager.PERMISSION_GRANTED
            machines.getValue(permission).onChecked(granted)
        }
        publish()
    }

    fun onRequestStarted(permission: HardwarePermission) {
        machines.getValue(permission).onRequestStarted()
        publish()
    }

    fun onPermissionResult(permission: HardwarePermission, granted: Boolean, canAskAgain: Boolean) {
        machines.getValue(permission).onResult(granted, canAskAgain)
        publish()
    }

    fun openAppSettings() {
        val intent = Intent(
            Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
            Uri.fromParts("package", context.packageName, null),
        ).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
    }

    private fun publish() {
        _uiState.update {
            it.copy(
                camera = machines.getValue(HardwarePermission.CAMERA).state.value,
                location = machines.getValue(HardwarePermission.LOCATION).state.value,
            )
        }
    }
}
