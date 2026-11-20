package com.lifesync.mobile.domain.usecase

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.User
import com.lifesync.mobile.domain.repository.AuthRepository
import javax.inject.Inject

class RegisterUseCase @Inject constructor(private val repository: AuthRepository) {
    suspend operator fun invoke(
        email: String,
        fullName: String,
        password: String,
    ): Resource<User> {
        if (email.isBlank() || fullName.isBlank() || password.length < 8) {
            return Resource.Error("Revisa los datos: contraseña mínima de 8 caracteres")
        }
        return repository.register(email.trim(), fullName.trim(), password)
    }
}
