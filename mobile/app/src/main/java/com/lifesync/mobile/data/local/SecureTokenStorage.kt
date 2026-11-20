package com.lifesync.mobile.data.local

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.lifesync.mobile.core.security.TokenStorage
import com.lifesync.mobile.domain.model.AuthToken
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Persistencia cifrada por hardware: la llave maestra AES-256-GCM reside en el
 * Android Keystore (TEE/StrongBox cuando está disponible) y nunca sale del
 * dispositivo. Equivale a Expo SecureStore / Flutter Secure Storage.
 */
@Singleton
class SecureTokenStorage @Inject constructor(
    @ApplicationContext context: Context,
) : TokenStorage {
    private val masterKey: MasterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val preferences: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        PREFERENCES_NAME,
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    private val _isAuthenticated = MutableStateFlow(
        !preferences.getString(KEY_ACCESS_TOKEN, null).isNullOrBlank()
    )
    override val isAuthenticated: StateFlow<Boolean> = _isAuthenticated.asStateFlow()

    override fun getAccessToken(): String? = preferences.getString(KEY_ACCESS_TOKEN, null)

    override fun getRefreshToken(): String? = preferences.getString(KEY_REFRESH_TOKEN, null)

    override suspend fun save(token: AuthToken) = withContext(Dispatchers.IO) {
        preferences.edit()
            .putString(KEY_ACCESS_TOKEN, token.accessToken)
            .putString(KEY_REFRESH_TOKEN, token.refreshToken)
            .putString(KEY_TOKEN_TYPE, token.tokenType)
            .putInt(KEY_EXPIRES_IN, token.expiresIn)
            .apply()
        _isAuthenticated.value = true
    }

    override suspend fun clear() = withContext(Dispatchers.IO) {
        preferences.edit().clear().apply()
        _isAuthenticated.value = false
    }

    private companion object {
        const val PREFERENCES_NAME = "lifesync_secure_prefs"
        const val KEY_ACCESS_TOKEN = "access_token"
        const val KEY_REFRESH_TOKEN = "refresh_token"
        const val KEY_TOKEN_TYPE = "token_type"
        const val KEY_EXPIRES_IN = "expires_in"
    }
}
