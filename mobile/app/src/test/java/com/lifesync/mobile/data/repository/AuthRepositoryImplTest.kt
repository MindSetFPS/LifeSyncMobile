package com.lifesync.mobile.data.repository

import app.cash.turbine.test
import com.google.common.truth.Truth.assertThat
import com.lifesync.mobile.core.oauth.OAuthConfiguration
import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.data.remote.AuthorizationRequestStore
import kotlinx.coroutines.test.runTest
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.Test
import retrofit2.HttpException
import retrofit2.Response

class AuthRepositoryImplTest {
    private fun repository(
        api: FakeAuthApiService = FakeAuthApiService(),
        storage: FakeTokenStorage = FakeTokenStorage(),
        store: AuthorizationRequestStore = AuthorizationRequestStore(),
    ) = AuthRepositoryImpl(api, storage, store)

    @Test
    fun `login guarda el JWT en almacenamiento seguro`() = runTest {
        val api = FakeAuthApiService().apply { loginResult = testTokenDto }
        val storage = FakeTokenStorage()
        val repository = repository(api, storage)

        val result = repository.login("ana@lifesync.mx", "SuperSegura123!")

        assertThat(result).isInstanceOf(Resource.Success::class.java)
        assertThat(storage.storedAccessToken).isEqualTo("access-jwt")
        assertThat(storage.storedRefreshToken).isEqualTo("refresh-jwt")
    }

    @Test
    fun `isAuthenticated reacciona al guardado y al cierre de sesion`() = runTest {
        val api = FakeAuthApiService().apply { loginResult = testTokenDto }
        val storage = FakeTokenStorage()
        val repository = repository(api, storage)

        repository.isAuthenticated.test {
            assertThat(awaitItem()).isFalse()
            repository.login("ana@lifesync.mx", "SuperSegura123!")
            assertThat(awaitItem()).isTrue()
            repository.logout()
            assertThat(awaitItem()).isFalse()
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `registro mapea el DTO sin persistir token`() = runTest {
        val api = FakeAuthApiService().apply { registerResult = testUserDto }
        val storage = FakeTokenStorage()
        val repository = repository(api, storage)

        val result = repository.register("ana@lifesync.mx", "Ana Pérez", "SuperSegura123!")

        val success = result as Resource.Success
        assertThat(success.data.email).isEqualTo("ana@lifesync.mx")
        assertThat(success.data.fullName).isEqualTo("Ana Pérez")
        assertThat(storage.storedAccessToken).isNull()
    }

    @Test
    fun `perfil obtenido con el token del interceptor`() = runTest {
        val api = FakeAuthApiService().apply { meResult = testUserDto }
        val repository = repository(api)

        val result = repository.getProfile() as Resource.Success

        assertThat(result.data.id).isEqualTo("user-1")
    }

    @Test
    fun `logout revoca el refresh token y limpia el almacenamiento`() = runTest {
        val api = FakeAuthApiService()
        val storage = FakeTokenStorage()
        storage.save(testTokenDto.toDomain())

        repository(api, storage).logout()

        assertThat(api.revokedToken).isEqualTo("refresh-jwt")
        assertThat(storage.clearCount).isEqualTo(1)
        assertThat(storage.getAccessToken()).isNull()
    }

    @Test
    fun `logout limpia el almacenamiento aunque la revocacion falle`() = runTest {
        val api = FakeAuthApiService().apply { revokeThrowable = IllegalStateException("sin red") }
        val storage = FakeTokenStorage()
        storage.save(testTokenDto.toDomain())

        repository(api, storage).logout()

        assertThat(storage.clearCount).isEqualTo(1)
        assertThat(storage.getAccessToken()).isNull()
    }

    @Test
    fun `error 401 se traduce a mensaje amigable`() = runTest {
        val body = "{}".toResponseBody("application/json".toMediaType())
        val api = FakeAuthApiService().apply {
            throwable = HttpException(Response.error<Unit>(401, body))
        }
        val repository = repository(api)

        val result = repository.login("ana@lifesync.mx", "mala") as Resource.Error

        assertThat(result.message).isEqualTo("Correo o contraseña incorrectos")
    }

    @Test
    fun `startAuthorization arma la URL con PKCE S256 y guarda el verifier`() = runTest {
        val api = FakeAuthApiService()
        val store = AuthorizationRequestStore()
        val repository = repository(api, store = store)

        val request = repository.startAuthorization()

        assertThat(request.url).contains("/oauth/authorize?")
        assertThat(request.url).contains("response_type=code")
        assertThat(request.url).contains("code_challenge_method=S256")
        assertThat(request.url).contains("client_id=${OAuthConfiguration.CLIENT_ID}")
        assertThat(request.url).contains(
            "redirect_uri=${java.net.URLEncoder.encode(OAuthConfiguration.REDIRECT_URI, "UTF-8")}",
        )
        assertThat(request.url).contains("state=${request.state}")
        assertThat(request.state).isNotEmpty()
    }

    @Test
    fun `canje del codigo usa el verifier y persiste los tokens`() = runTest {
        val api = FakeAuthApiService().apply { exchangeResult = testTokenDto }
        val storage = FakeTokenStorage()
        val store = AuthorizationRequestStore()
        val repository = repository(api, storage, store)

        val request = repository.startAuthorization()
        val result = repository.exchangeAuthorizationCode("codigo-123", request.state)

        assertThat(result).isInstanceOf(Resource.Success::class.java)
        assertThat(api.lastExchangedCode).isEqualTo("codigo-123")
        assertThat(api.lastExchangedVerifier).isNotNull()
        assertThat(storage.storedAccessToken).isEqualTo("access-jwt")
    }

    @Test
    fun `un state que no coincide es rechazado sin llamar al backend`() = runTest {
        val api = FakeAuthApiService().apply { exchangeResult = testTokenDto }
        val repository = repository(api, store = AuthorizationRequestStore())

        repository.startAuthorization()
        val result = repository.exchangeAuthorizationCode("codigo-123", "state-adversario")

        assertThat(result).isInstanceOf(Resource.Error::class.java)
        assertThat(api.lastExchangedCode).isNull()
    }

    @Test
    fun `el codigo de autorizacion solo puede canjearse una vez`() = runTest {
        val api = FakeAuthApiService().apply { exchangeResult = testTokenDto }
        val repository = repository(api, store = AuthorizationRequestStore())

        val request = repository.startAuthorization()
        repository.exchangeAuthorizationCode("codigo-123", request.state)
        val replay = repository.exchangeAuthorizationCode("codigo-123", request.state)

        assertThat(replay).isInstanceOf(Resource.Error::class.java)
    }
}
