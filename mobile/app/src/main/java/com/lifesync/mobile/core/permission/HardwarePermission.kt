package com.lifesync.mobile.core.permission

import android.Manifest

/** Permisos de hardware que usa el Sprint 3. */
enum class HardwarePermission(val manifestPermission: String) {
    CAMERA(Manifest.permission.CAMERA),
    LOCATION(Manifest.permission.ACCESS_FINE_LOCATION),
}
