package com.lifesync.mobile.data.remote

import javax.inject.Inject
import javax.inject.Singleton

/**
 * Guarda en memoria el `state` y el `code_verifier` del flujo en curso.
 *
 * Se conserva en memoria (no en disco) a propósito: si el proceso muere el
 * flujo se reinicia, lo que es preferible a dejar un verifier persistido.
 */
@Singleton
class AuthorizationRequestStore @Inject constructor() {
    data class Pending(val state: String, val codeVerifier: String)

    private var pending: Pending? = null

    fun save(state: String, codeVerifier: String) {
        pending = Pending(state, codeVerifier)
    }

    /** Devuelve y consume el pendiente solo si el `state` coincide. */
    fun consume(state: String): Pending? {
        val current = pending ?: return null
        if (current.state != state) return null
        pending = null
        return current
    }

    fun clear() {
        pending = null
    }
}
