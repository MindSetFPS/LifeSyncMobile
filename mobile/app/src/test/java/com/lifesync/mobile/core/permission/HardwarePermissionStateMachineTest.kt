package com.lifesync.mobile.core.permission

import com.google.common.truth.Truth.assertThat
import org.junit.Test

class HardwarePermissionStateMachineTest {

    @Test
    fun `starts as not requested`() {
        assertThat(HardwarePermissionStateMachine().state.value)
            .isEqualTo(PermissionState.NotRequested)
    }

    @Test
    fun `granted result reaches granted`() {
        val machine = HardwarePermissionStateMachine()

        machine.onRequestStarted()
        assertThat(machine.state.value).isEqualTo(PermissionState.Requesting)

        machine.onResult(granted = true, canAskAgain = false)
        assertThat(machine.state.value).isEqualTo(PermissionState.Granted)
    }

    @Test
    fun `denial that can ask again is denied`() {
        val machine = HardwarePermissionStateMachine()

        machine.onRequestStarted()
        machine.onResult(granted = false, canAskAgain = true)

        assertThat(machine.state.value).isEqualTo(PermissionState.Denied)
    }

    @Test
    fun `denial without rationale is permanently denied`() {
        val machine = HardwarePermissionStateMachine()

        machine.onRequestStarted()
        machine.onResult(granted = false, canAskAgain = false)

        assertThat(machine.state.value).isEqualTo(PermissionState.PermanentlyDenied)
    }

    @Test
    fun `system check grants after returning from settings`() {
        val machine = HardwarePermissionStateMachine()
        machine.onRequestStarted()
        machine.onResult(granted = false, canAskAgain = false)

        machine.onChecked(granted = true)

        assertThat(machine.state.value).isEqualTo(PermissionState.Granted)
    }

    @Test
    fun `system check keeps a previous denial`() {
        val denied = HardwarePermissionStateMachine()
        denied.onRequestStarted()
        denied.onResult(granted = false, canAskAgain = true)

        denied.onChecked(granted = false)

        assertThat(denied.state.value).isEqualTo(PermissionState.Denied)
    }

    @Test
    fun `revoked permission returns to not requested but keeps permanent block`() {
        val granted = HardwarePermissionStateMachine()
        granted.onResult(granted = true, canAskAgain = false)
        granted.onChecked(granted = false)
        assertThat(granted.state.value).isEqualTo(PermissionState.NotRequested)

        val blocked = HardwarePermissionStateMachine()
        blocked.onResult(granted = false, canAskAgain = false)
        blocked.onChecked(granted = false)
        assertThat(blocked.state.value).isEqualTo(PermissionState.PermanentlyDenied)
    }
}
