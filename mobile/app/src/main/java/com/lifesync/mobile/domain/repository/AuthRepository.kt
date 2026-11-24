package com.lifesync.mobile.domain.repository

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.AuthToken
import com.lifesync.mobile.domain.model.AuthorizationRequest
import com.lifesync.mobile.domain.model.User
import kotlinx.coroutines.flow.Flow

/** Contrato de dominio: la capa de datos no es conocida por los casos de uso. */
interface AuthRepository {
    val isAuthenticated: Flow<Boolean>

    /** Sprint 1 (compatibilidad): OAuth 2.0 password grant. */
    suspend fun login(email: String, password: String): Resource<AuthToken>

    /** Prepara el flujo Authorization Code + PKCE y devuelve la URL a abrir. */
    suspend fun startAuthorization(): AuthorizationRequest

    /** Canjea el `code` del redirect validando `state` y el `code_verifier`. */
    suspend fun exchangeAuthorizationCode(code: String, state: String?): Resource<AuthToken>

    suspend fun register(email: String, fullName: String, password: String): Resource<User>
    suspend fun getProfile(): Resource<User>
    suspend fun logout()
}
