package com.lifesync.mobile.data.repository

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.core.security.TokenStorage
import com.lifesync.mobile.data.remote.dto.RegisterRequest
import com.lifesync.mobile.data.remote.dto.RefreshRequest
import com.lifesync.mobile.data.remote.dto.TokenDto
import com.lifesync.mobile.data.remote.dto.UserDto
import com.lifesync.mobile.data.remote.service.AuthApiService
import com.lifesync.mobile.domain.model.AuthToken
import com.lifesync.mobile.domain.model.User
import com.lifesync.mobile.domain.repository.AuthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

val testTokenDto = TokenDto(
    accessToken = "access-jwt",
    refreshToken = "refresh-jwt",
    tokenType = "bearer",
    expiresIn = 900,
)

val testUserDto = UserDto(
    id = "user-1",
    email = "ana@lifesync.mx",
    fullName = "Ana Pérez",
    isActive = true,
)

class FakeAuthApiService : AuthApiService {
    var loginResult: TokenDto? = null
    var registerResult: UserDto? = null
    var meResult: UserDto? = null
    var refreshResult: TokenDto? = null
    var throwable: Throwable? = null

    override suspend fun login(username: String, password: String, grantType: String): TokenDto =
        throwable?.let { throw it } ?: loginResult ?: error("loginResult no configurado")

    override suspend fun register(request: RegisterRequest): UserDto =
        throwable?.let { throw it } ?: registerResult ?: error("registerResult no configurado")

    override suspend fun me(): UserDto =
        throwable?.let { throw it } ?: meResult ?: error("meResult no configurado")

    override suspend fun refresh(request: RefreshRequest): TokenDto =
        throwable?.let { throw it } ?: refreshResult ?: error("refreshResult no configurado")
}

class FakeTokenStorage : TokenStorage {
    private val _isAuthenticated = MutableStateFlow(false)
    override val isAuthenticated: StateFlow<Boolean> = _isAuthenticated.asStateFlow()

    var storedAccessToken: String? = null
        private set
    var storedRefreshToken: String? = null
        private set
    var clearCount: Int = 0
        private set

    override fun getAccessToken(): String? = storedAccessToken
    override fun getRefreshToken(): String? = storedRefreshToken

    override suspend fun save(token: AuthToken) {
        storedAccessToken = token.accessToken
        storedRefreshToken = token.refreshToken
        _isAuthenticated.value = true
    }

    override suspend fun clear() {
        storedAccessToken = null
        storedRefreshToken = null
        clearCount++
        _isAuthenticated.value = false
    }
}

class FakeAuthRepository : AuthRepository {
    private val _isAuthenticated = MutableStateFlow(false)
    override val isAuthenticated: StateFlow<Boolean> = _isAuthenticated.asStateFlow()

    var loginResult: Resource<AuthToken> = Resource.Error("no configurado")
    var registerResult: Resource<User> = Resource.Error("no configurado")
    var profileResult: Resource<User> = Resource.Error("no configurado")
    val loginCalls = mutableListOf<Pair<String, String>>()

    override suspend fun login(email: String, password: String): Resource<AuthToken> {
        loginCalls += email to password
        if (loginResult is Resource.Success) _isAuthenticated.value = true
        return loginResult
    }

    override suspend fun register(
        email: String,
        fullName: String,
        password: String,
    ): Resource<User> = registerResult

    override suspend fun getProfile(): Resource<User> = profileResult

    override suspend fun logout() {
        _isAuthenticated.value = false
    }
}
