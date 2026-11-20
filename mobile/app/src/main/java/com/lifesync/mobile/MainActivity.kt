package com.lifesync.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.runtime.getValue
import com.lifesync.mobile.navigation.AppNavigation
import com.lifesync.mobile.presentation.LifeSyncTheme
import com.lifesync.mobile.presentation.auth.AuthViewModel
import com.lifesync.mobile.presentation.home.HomeViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val authViewModel: AuthViewModel by viewModels()
    private val homeViewModel: HomeViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            LifeSyncTheme {
                val isAuthenticated by authViewModel.isAuthenticated
                    .collectAsStateWithLifecycle(initialValue = false)
                AppNavigation(isAuthenticated, authViewModel, homeViewModel)
            }
        }
    }
}
