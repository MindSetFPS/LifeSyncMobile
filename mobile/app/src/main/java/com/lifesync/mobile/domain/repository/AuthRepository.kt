package com.lifesync.mobile.domain.repository

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.AuthToken
import com.lifesync.mobile.domain.model.User
import kotlinx.coroutines.flow.Flow

/** Contrato de dominio: la capa de datos no es conocida por los casos de uso. */
interface AuthRepository {
    val isAuthenticated: Flow<Boolean>
    suspend fun login(email: String, password: String): Resource<AuthToken>
    suspend fun register(email: String, fullName: String, password: String): Resource<User>
    suspend fun getProfile(): Resource<User>
    suspend fun logout()
}
