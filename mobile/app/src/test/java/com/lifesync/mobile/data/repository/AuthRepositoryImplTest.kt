package com.lifesync.mobile.data.repository

import app.cash.turbine.test
import com.google.common.truth.Truth.assertThat
import com.lifesync.mobile.core.result.Resource
import kotlinx.coroutines.test.runTest
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.Test
import retrofit2.HttpException
import retrofit2.Response

class AuthRepositoryImplTest {
    @Test
    fun `login guarda el JWT en almacenamiento seguro`() = runTest {
        val api = FakeAuthApiService().apply { loginResult = testTokenDto }
        val storage = FakeTokenStorage()
        val repository = AuthRepositoryImpl(api, storage)

        val result = repository.login("ana@lifesync.mx", "SuperSegura123!")

        assertThat(result).isInstanceOf(Resource.Success::class.java)
        assertThat(storage.storedAccessToken).isEqualTo("access-jwt")
        assertThat(storage.storedRefreshToken).isEqualTo("refresh-jwt")
    }

    @Test
    fun `isAuthenticated reacciona al guardado y al cierre de sesion`() = runTest {
        val api = FakeAuthApiService().apply { loginResult = testTokenDto }
        val storage = FakeTokenStorage()
        val repository = AuthRepositoryImpl(api, storage)

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
        val repository = AuthRepositoryImpl(api, storage)

        val result = repository.register("ana@lifesync.mx", "Ana Pérez", "SuperSegura123!")

        val success = result as Resource.Success
        assertThat(success.data.email).isEqualTo("ana@lifesync.mx")
        assertThat(success.data.fullName).isEqualTo("Ana Pérez")
        assertThat(storage.storedAccessToken).isNull()
    }

    @Test
    fun `perfil obtenido con el token del interceptor`() = runTest {
        val api = FakeAuthApiService().apply { meResult = testUserDto }
        val repository = AuthRepositoryImpl(api, FakeTokenStorage())

        val result = repository.getProfile() as Resource.Success

        assertThat(result.data.id).isEqualTo("user-1")
    }

    @Test
    fun `logout limpia el almacenamiento`() = runTest {
        val storage = FakeTokenStorage()
        storage.save(testTokenDto.toDomain())

        AuthRepositoryImpl(FakeAuthApiService(), storage).logout()

        assertThat(storage.clearCount).isEqualTo(1)
        assertThat(storage.getAccessToken()).isNull()
    }

    @Test
    fun `error 401 se traduce a mensaje amigable`() = runTest {
        val body = "{}".toResponseBody("application/json".toMediaType())
        val api = FakeAuthApiService().apply {
            throwable = HttpException(Response.error<Unit>(401, body))
        }
        val repository = AuthRepositoryImpl(api, FakeTokenStorage())

        val result = repository.login("ana@lifesync.mx", "mala") as Resource.Error

        assertThat(result.message).isEqualTo("Correo o contraseña incorrectos")
    }
}
