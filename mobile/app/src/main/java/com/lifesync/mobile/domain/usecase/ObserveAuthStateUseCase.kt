package com.lifesync.mobile.domain.usecase

import com.lifesync.mobile.domain.repository.AuthRepository
import javax.inject.Inject

/** Expone el estado de sesión para los gráficos de navegación protegidos. */
class ObserveAuthStateUseCase @Inject constructor(private val repository: AuthRepository) {
    operator fun invoke() = repository.isAuthenticated
}
