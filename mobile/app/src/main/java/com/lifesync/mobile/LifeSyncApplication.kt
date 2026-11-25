package com.lifesync.mobile

import android.app.Application
import com.lifesync.mobile.data.local.alerts.AlertNotificationFactory
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject

@HiltAndroidApp
class LifeSyncApplication : Application() {

    @Inject
    lateinit var notificationFactory: AlertNotificationFactory

    override fun onCreate() {
        super.onCreate()
        notificationFactory.ensureChannel()
    }
}
