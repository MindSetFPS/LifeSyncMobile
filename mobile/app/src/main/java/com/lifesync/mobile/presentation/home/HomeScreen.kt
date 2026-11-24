package com.lifesync.mobile.presentation.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.lifesync.mobile.R
import com.lifesync.mobile.presentation.auth.HomeUiState

@Composable
fun HomeScreen(
    uiState: HomeUiState,
    onOpenPatientProfile: () -> Unit,
    onLogout: () -> Unit,
    onRetry: () -> Unit,
) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(text = stringResource(R.string.profile_title), style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(20.dp))

        when {
            uiState.isLoading -> CircularProgressIndicator()
            uiState.errorMessage != null -> {
                Text(text = uiState.errorMessage!!, color = MaterialTheme.colorScheme.error)
                Spacer(Modifier.height(12.dp))
                Button(onClick = onRetry) { Text("Reintentar") }
            }
            uiState.user != null -> {
                Text(text = uiState.user!!.fullName, style = MaterialTheme.typography.titleLarge)
                Spacer(Modifier.height(8.dp))
                Text(text = uiState.user!!.email)
            }
        }

        Spacer(Modifier.height(32.dp))
        Button(
            onClick = onOpenPatientProfile,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.patient_profile_button))
        }
        Spacer(Modifier.height(8.dp))
        Button(
            onClick = onLogout,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.logout_button))
        }
    }
}
