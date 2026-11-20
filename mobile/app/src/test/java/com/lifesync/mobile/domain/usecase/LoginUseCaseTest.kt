package com.lifesync.mobile.domain.usecase

import com.google.common.truth.Truth.assertThat
import com.lifesync.mobile.core.result.Resource
import com.lifesync.mobile.data.repository.FakeAuthRepository
import com.lifesync.mobile.domain.model.AuthToken
import kotlinx.coroutines.test.runTest
import org.junit.Test

class LoginUseCaseTest {
    @Test
    fun `credenciales vacias se rechazan sin llamar al repositorio`() = runTest {
        val repository = FakeAuthRepository()
        val useCase = LoginUseCase(repository)

        val result = useCase(" ", "")

        assertThat(result).isInstanceOf(Resource.Error::class.java)
        assertThat(repository.loginCalls).isEmpty()
    }

    @Test
    fun `recorta el correo y delega en el repositorio`() = runTest {
        val repository = FakeAuthRepository().apply {
            loginResult = Resource.Success(AuthToken("a", "r", expiresIn = 900))
        }
        val result = LoginUseCase(repository)("  ana@lifesync.mx ", "SuperSegura123!")

        assertThat(result).isInstanceOf(Resource.Success::class.java)
        assertThat(repository.loginCalls).containsExactly("ana@lifesync.mx" to "SuperSegura123!")
    }

    @Test
    fun `propaga el error del repositorio`() = runTest {
        val repository = FakeAuthRepository().apply {
            loginResult = Resource.Error("Correo o contraseña incorrectos")
        }
        val result = LoginUseCase(repository)("ana@lifesync.mx", "mala")

        assertThat((result as Resource.Error).message).isEqualTo("Correo o contraseña incorrectos")
    }
}
