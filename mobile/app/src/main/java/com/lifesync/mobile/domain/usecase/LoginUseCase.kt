package com.lifesync.mobile.domain.usecase

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.AuthToken
import com.lifesync.mobile.domain.repository.AuthRepository
import javax.inject.Inject

class LoginUseCase @Inject constructor(private val repository: AuthRepository) {
    suspend operator fun invoke(email: String, password: String): Resource<AuthToken> {
        if (email.isBlank() || password.isBlank()) {
            return Resource.Error("Ingresa correo y contraseña")
        }
        return repository.login(email.trim(), password)
    }
}
