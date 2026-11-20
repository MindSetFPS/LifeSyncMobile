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

/** Contrato HTTP del API centralizado (OAuth 2.0 password grant). */
interface AuthApiService {
    @FormUrlEncoded
    @POST("auth/token")
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String,
        @Field("grant_type") grantType: String = "password",
    ): TokenDto

    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): UserDto

    @GET("auth/me")
    suspend fun me(): UserDto

    @POST("auth/refresh")
    suspend fun refresh(@Body request: RefreshRequest): TokenDto
}
