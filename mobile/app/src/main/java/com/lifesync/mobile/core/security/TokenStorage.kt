package com.lifesync.mobile.core.security

import com.lifesync.mobile.domain.model.AuthToken
import kotlinx.coroutines.flow.Flow

/**
 * Contrato de almacenamiento seguro. La implementación real usa Android Keystore
 * + EncryptedSharedPreferences; las pruebas JVM usan un doble en memoria.
 */
interface TokenStorage {
    val isAuthenticated: Flow<Boolean>
    fun getAccessToken(): String?
    fun getRefreshToken(): String?
    suspend fun save(token: AuthToken)
    suspend fun clear()
}
