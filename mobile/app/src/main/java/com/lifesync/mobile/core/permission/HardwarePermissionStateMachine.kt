package com.lifesync.mobile.core.permission

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Máquina de estados pura de un permiso de hardware.
 *
 * No conoce Android: el ViewModel la alimenta con el resultado del sistema.
 * Ver `docs/permission_state_machine.md` para el mapeo teórico.
 */
class HardwarePermissionStateMachine {

    private val _state = MutableStateFlow<PermissionState>(PermissionState.NotRequested)
    val state: StateFlow<PermissionState> = _state.asStateFlow()

    /** Reconciliación con la fuente de verdad del sistema (`checkSelfPermission`). */
    fun onChecked(granted: Boolean) {
        _state.value = when {
            granted -> PermissionState.Granted
            _state.value is PermissionState.PermanentlyDenied -> PermissionState.PermanentlyDenied
            else -> PermissionState.NotRequested
        }
    }

    fun onRequestStarted() {
        _state.value = PermissionState.Requesting
    }

    fun onResult(granted: Boolean, canAskAgain: Boolean) {
        _state.value = when {
            granted -> PermissionState.Granted
            canAskAgain -> PermissionState.Denied
            else -> PermissionState.PermanentlyDenied
        }
    }
}
