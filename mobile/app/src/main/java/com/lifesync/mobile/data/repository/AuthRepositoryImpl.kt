package com.lifesync.mobile.data.repository

import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.core.security.TokenStorage
import com.lifesync.mobile.data.remote.dto.RegisterRequest
import com.lifesync.mobile.data.remote.service.AuthApiService
import com.lifesync.mobile.domain.model.AuthToken
import com.lifesync.mobile.domain.model.User
import com.lifesync.mobile.domain.repository.AuthRepository
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject
import javax.inject.Named
import javax.inject.Singleton

/** Implementación de dominio: consume la API de forma asíncrona y persiste el JWT. */
@Singleton
class AuthRepositoryImpl @Inject constructor(
    @Named("auth") private val api: AuthApiService,
    private val tokenStorage: TokenStorage,
) : AuthRepository {
    override val isAuthenticated = tokenStorage.isAuthenticated

    override suspend fun login(email: String, password: String): Resource<AuthToken> {
        val result = safeCall { api.login(email, password).toDomain() }
        if (result is Resource.Success) tokenStorage.save(result.data)
        return result
    }

    override suspend fun register(
        email: String,
        fullName: String,
        password: String,
    ): Resource<User> = safeCall {
        api.register(RegisterRequest(email, fullName, password)).toDomain()
    }

    override suspend fun getProfile(): Resource<User> = safeCall { api.me().toDomain() }

    override suspend fun logout() = tokenStorage.clear()

    private suspend fun <T> safeCall(block: suspend () -> T): Resource<T> = try {
        Resource.Success(block())
    } catch (e: HttpException) {
        Resource.Error(mapHttpError(e.code()), e)
    } catch (e: IOException) {
        Resource.Error("Sin conexión con el servidor", e)
    } catch (e: Exception) {
        Resource.Error(e.message ?: "Error inesperado", e)
    }

    private fun mapHttpError(code: Int): String = when (code) {
        401 -> "Correo o contraseña incorrectos"
        409 -> "El correo ya está registrado"
        422 -> "Revisa los datos ingresados"
        in 500..599 -> "Error del servidor, intenta más tarde"
        else -> "Error de la petición ($code)"
    }
}
