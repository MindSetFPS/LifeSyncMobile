package com.lifesync.mobile.domain.usecase

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.AuthToken
import com.lifesync.mobile.domain.model.AuthorizationRequest
import com.lifesync.mobile.domain.repository.AuthRepository
import javax.inject.Inject

/** Prepara el flujo Authorization Code + PKCE (RFC 8252) devolviendo la URL. */
class StartAuthorizationUseCase @Inject constructor(private val repository: AuthRepository) {
    suspend operator fun invoke(): Resource<AuthorizationRequest> = try {
        Resource.Success(repository.startAuthorization())
    } catch (e: Exception) {
        Resource.Error(e.message ?: "No se pudo iniciar la autorización", e)
    }
}

/** Canjea el código del redirect por tokens y los persiste cifrados. */
class CompleteAuthorizationUseCase @Inject constructor(private val repository: AuthRepository) {
    suspend operator fun invoke(code: String, state: String?): Resource<AuthToken> {
        if (code.isBlank()) return Resource.Error("El código de autorización está vacío")
        return repository.exchangeAuthorizationCode(code, state)
    }
}
