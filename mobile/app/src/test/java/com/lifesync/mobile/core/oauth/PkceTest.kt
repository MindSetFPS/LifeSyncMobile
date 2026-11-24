package com.lifesync.mobile.core.oauth

import com.google.common.truth.Truth.assertThat
import org.junit.Test
import java.security.MessageDigest
import java.util.Base64

class PkceTest {
    @Test
    fun `el verifier respeta la longitud y el alfabeto de RFC 7636`() {
        val verifier = Pkce.generateVerifier()

        assertThat(verifier.length).isAtLeast(43)
        assertThat(verifier.length).isAtMost(128)
        assertThat(verifier).matches("[A-Za-z0-9\\-_]+")
    }

    @Test
    fun `el challenge es el SHA-256 base64url sin padding del verifier`() {
        val verifier = "v".repeat(50)

        val expected = Base64.getUrlEncoder()
            .withoutPadding()
            .encodeToString(
                MessageDigest.getInstance("SHA-256")
                    .digest(verifier.toByteArray(Charsets.US_ASCII)),
            )

        assertThat(Pkce.challenge(verifier)).isEqualTo(expected)
    }

    @Test
    fun `dos verifiers consecutivos son distintos`() {
        assertThat(Pkce.generateVerifier()).isNotEqualTo(Pkce.generateVerifier())
    }

    @Test
    fun `el vector de ejemplo de RFC 7636 coincide`() {
        // RFC 7636 Apéndice B.
        val verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        assertThat(Pkce.challenge(verifier))
            .isEqualTo("E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM")
    }
}
