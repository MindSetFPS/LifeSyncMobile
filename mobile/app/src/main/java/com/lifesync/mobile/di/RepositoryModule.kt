package com.lifesync.mobile.di

import com.lifesync.mobile.data.repository.AuthRepositoryImpl
import com.lifesync.mobile.domain.repository.AuthRepository
import dagger.Binds
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import java.security.SecureRandom
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindAuthRepository(implementation: AuthRepositoryImpl): AuthRepository

    companion object {
        @Provides
        @Singleton
        fun provideSecureRandom(): SecureRandom = SecureRandom()
    }
}
