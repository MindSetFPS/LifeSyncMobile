package com.lifesync.mobile.domain.model

/** Petición de autorización lista para abrirse en el navegador externo. */
data class AuthorizationRequest(
    val url: String,
    val state: String,
)
