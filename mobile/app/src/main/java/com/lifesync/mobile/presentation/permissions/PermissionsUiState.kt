package com.lifesync.mobile.presentation.permissions

import com.lifesync.mobile.core.permission.PermissionState

data class PermissionsUiState(
    val camera: PermissionState = PermissionState.NotRequested,
    val location: PermissionState = PermissionState.NotRequested,
) {
    val cameraScanEnabled: Boolean get() = camera is PermissionState.Granted
    val cloudTrackingEnabled: Boolean get() = location is PermissionState.Granted
    val locationDegraded: Boolean
        get() = location is PermissionState.Denied ||
            location is PermissionState.PermanentlyDenied
}
