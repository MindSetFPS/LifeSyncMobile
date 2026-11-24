package com.lifesync.mobile.data.remote.service

import com.lifesync.mobile.data.remote.dto.RefreshRequest
import com.lifesync.mobile.data.remote.dto.RegisterRequest
import com.lifesync.mobile.data.remote.dto.TokenDto
import com.lifesync.mobile.data.remote.dto.UserDto
import retrofit2.http.Body
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.POST

/**
 * Contrato HTTP del API centralizado.
 *
 * Sprint 1: `grant_type=password` (compatibilidad y demo del aula).
 * OAuth 2.1: `grant_type=authorization_code` con PKCE (RFC 7636/8252).
 */
interface AuthApiService {
    @FormUrlEncoded
    @POST("auth/token")
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String,
        @Field("grant_type") grantType: String = "password",
        @Field("scope") scope: String? = null,
    ): TokenDto

    @FormUrlEncoded
    @POST("auth/token")
    suspend fun exchangeAuthorizationCode(
        @Field("grant_type") grantType: String = "authorization_code",
        @Field("code") code: String,
        @Field("redirect_uri") redirectUri: String,
        @Field("code_verifier") codeVerifier: String,
        @Field("client_id") clientId: String,
    ): TokenDto

    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): UserDto

    @GET("auth/me")
    suspend fun me(): UserDto

    @POST("auth/refresh")
    suspend fun refresh(@Body request: RefreshRequest): TokenDto

    /** RFC 7009: revoca la familia del refresh token al cerrar sesión. */
    @FormUrlEncoded
    @POST("auth/revoke")
    suspend fun revoke(
        @Field("token") token: String,
        @Field("token_type_hint") tokenTypeHint: String = "refresh_token",
    )
}
