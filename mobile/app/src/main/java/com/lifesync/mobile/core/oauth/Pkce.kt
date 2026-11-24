package com.lifesync.mobile.core.oauth

import java.security.MessageDigest
import java.security.SecureRandom
import java.util.Base64

/**
 * PKCE según RFC 7636. El `code_verifier` nunca sale del dispositivo hasta el
 * canje del código, y el `code_challenge` (S256) es lo único que viaja al
 * servidor de autorización.
 */
object Pkce {
    private const val VERIFIER_BYTES = 48

    fun generateVerifier(random: SecureRandom = SecureRandom()): String {
        val bytes = ByteArray(VERIFIER_BYTES)
        random.nextBytes(bytes)
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes)
    }

    fun challenge(verifier: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
            .digest(verifier.toByteArray(Charsets.US_ASCII))
        return Base64.getUrlEncoder().withoutPadding().encodeToString(digest)
    }
}
