package com.lifesync.mobile.di

import com.lifesync.mobile.data.local.alerts.AlarmManagerMedicationReminderScheduler
import com.lifesync.mobile.data.local.alerts.InMemoryAlertEventPublisher
import com.lifesync.mobile.domain.observer.AlertEventPublisher
import com.lifesync.mobile.domain.scheduling.MedicationReminderScheduler
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/** Cablea el módulo de alertas locales (Observer + scheduling). */
@Module
@InstallIn(SingletonComponent::class)
abstract class AlertsModule {
    @Binds
    @Singleton
    abstract fun bindAlertEventPublisher(
        implementation: InMemoryAlertEventPublisher,
    ): AlertEventPublisher

    @Binds
    @Singleton
    abstract fun bindMedicationReminderScheduler(
        implementation: AlarmManagerMedicationReminderScheduler,
    ): MedicationReminderScheduler
}
