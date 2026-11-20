package com.lifesync.mobile.domain.usecase

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.domain.model.User
import com.lifesync.mobile.domain.repository.AuthRepository
import javax.inject.Inject

class GetProfileUseCase @Inject constructor(private val repository: AuthRepository) {
    suspend operator fun invoke(): Resource<User> = repository.getProfile()
}
