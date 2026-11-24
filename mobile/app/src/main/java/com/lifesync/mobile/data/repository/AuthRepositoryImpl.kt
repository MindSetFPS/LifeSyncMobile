package com.lifesync.mobile.data.repository

import com.lifesync.mobile.core.oauth.OAuthConfiguration
import com.lifesync.mobile.core.oauth.Pkce
import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.core.security.TokenStorage
import com.lifesync.mobile.data.remote.AuthorizationRequestStore
import com.lifesync.mobile.data.remote.dto.RegisterRequest
import com.lifesync.mobile.data.remote.service.AuthApiService
import com.lifesync.mobile.domain.model.AuthToken
import com.lifesync.mobile.domain.model.AuthorizationRequest
import com.lifesync.mobile.domain.model.User
import com.lifesync.mobile.domain.repository.AuthRepository
import retrofit2.HttpException
import java.io.IOException
import java.security.SecureRandom
import javax.inject.Inject
import javax.inject.Named
import javax.inject.Singleton

/** Implementación de dominio: consume la API de forma asíncrona y persiste el JWT. */
@Singleton
class AuthRepositoryImpl @Inject constructor(
    @Named("auth") private val api: AuthApiService,
    private val tokenStorage: TokenStorage,
    private val authorizationRequestStore: AuthorizationRequestStore,
    private val secureRandom: SecureRandom = SecureRandom(),
) : AuthRepository {
    override val isAuthenticated = tokenStorage.isAuthenticated

    override suspend fun login(email: String, password: String): Resource<AuthToken> {
        val result = safeCall {
            api.login(email, password, scope = OAuthConfiguration.SCOPE).toDomain()
        }
        if (result is Resource.Success) tokenStorage.save(result.data)
        return result
    }

    override suspend fun startAuthorization(): AuthorizationRequest {
        val state = Pkce.generateVerifier(secureRandom)
        val verifier = Pkce.generateVerifier(secureRandom)
        val challenge = Pkce.challenge(verifier)
        authorizationRequestStore.save(state = state, codeVerifier = verifier)
        return AuthorizationRequest(
            url = OAuthConfiguration.authorizationUrl(state = state, codeChallenge = challenge),
            state = state,
        )
    }

    override suspend fun exchangeAuthorizationCode(code: String, state: String?): Resource<AuthToken> {
        val pending = authorizationRequestStore.consume(state ?: "")
            ?: return Resource.Error("El estado de la autorización no coincide")

        val result = safeCall {
            api.exchangeAuthorizationCode(
                code = code,
                redirectUri = OAuthConfiguration.REDIRECT_URI,
                codeVerifier = pending.codeVerifier,
                clientId = OAuthConfiguration.CLIENT_ID,
            ).toDomain()
        }
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

    /** Cierra sesión revocando el refresh token (RFC 7009) antes de borrarlo. */
    override suspend fun logout() {
        val refreshToken = tokenStorage.getRefreshToken()
        if (!refreshToken.isNullOrBlank()) {
            try {
                api.revoke(refreshToken)
            } catch (_: Exception) {
                // El borrado local manda: sin red la sesión también debe cerrarse.
            }
        }
        tokenStorage.clear()
    }

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
        400, 401 -> "Correo o contraseña incorrectos"
        403 -> "La aplicación no tiene permiso para esta operación"
        409 -> "El correo ya está registrado"
        422 -> "Revisa los datos ingresados"
        in 500..599 -> "Error del servidor, intenta más tarde"
        else -> "Error de la petición ($code)"
    }
}
