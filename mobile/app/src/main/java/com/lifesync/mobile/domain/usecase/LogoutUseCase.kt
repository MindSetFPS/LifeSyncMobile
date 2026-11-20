package com.lifesync.mobile.domain.usecase

import com.lifesync.mobile.domain.repository.AuthRepository
import javax.inject.Inject

class LogoutUseCase @Inject constructor(private val repository: AuthRepository) {
    suspend operator fun invoke() = repository.logout()
}
