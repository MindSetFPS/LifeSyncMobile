package com.lifesync.mobile.core.permission

/** Estados de la solicitud asíncrona de un permiso de hardware. */
sealed interface PermissionState {
    val isGranted: Boolean get() = this is Granted

    data object NotRequested : PermissionState
    data object Requesting : PermissionState
    data object Granted : PermissionState
    data object Denied : PermissionState
    data object PermanentlyDenied : PermissionState
}
