package com.lifesync.mobile.presentation.profile

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Tab
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.lifesync.mobile.R
import com.lifesync.mobile.domain.model.Allergy
import com.lifesync.mobile.domain.model.AllergyCategory
import com.lifesync.mobile.domain.model.AllergySeverity
import com.lifesync.mobile.domain.model.BloodType
import com.lifesync.mobile.domain.model.DoseUnit
import com.lifesync.mobile.domain.model.EmergencyContact
import com.lifesync.mobile.domain.model.Medication
import com.lifesync.mobile.domain.model.MedicationRoute
import com.lifesync.mobile.domain.model.RhFactor

private val tabs = listOf("Datos", "Alergias", "Medicamentos", "Contactos")

@Composable
fun PatientProfileRoute(
    onBack: () -> Unit,
    viewModel: PatientProfileViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    LaunchedEffect(Unit) { viewModel.load() }

    PatientProfileScreen(
        uiState = uiState,
        onBack = onBack,
        onRetry = viewModel::load,
        onProfileChange = viewModel::updateProfileForm,
        onSaveProfile = viewModel::saveProfile,
        onAllergyFormChange = viewModel::updateAllergyForm,
        onAddAllergy = viewModel::addAllergy,
        onDeleteAllergy = viewModel::deleteAllergy,
        onMedicationFormChange = viewModel::updateMedicationForm,
        onAddMedication = viewModel::addMedication,
        onDeleteMedication = viewModel::deleteMedication,
        onContactFormChange = viewModel::updateContactForm,
        onAddContact = viewModel::addContact,
        onDeleteContact = viewModel::deleteContact,
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PatientProfileScreen(
    uiState: ProfileUiState,
    onBack: () -> Unit,
    onRetry: () -> Unit,
    onProfileChange: (ProfileForm) -> Unit,
    onSaveProfile: () -> Unit,
    onAllergyFormChange: (AllergyForm) -> Unit,
    onAddAllergy: () -> Unit,
    onDeleteAllergy: (String) -> Unit,
    onMedicationFormChange: (MedicationForm) -> Unit,
    onAddMedication: () -> Unit,
    onDeleteMedication: (String) -> Unit,
    onContactFormChange: (ContactForm) -> Unit,
    onAddContact: () -> Unit,
    onDeleteContact: (String) -> Unit,
) {
    var selectedTab by rememberSaveable { mutableIntStateOf(0) }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = stringResource(R.string.patient_profile_title),
                        fontWeight = FontWeight.Bold,
                    )
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.onSurface,
                    navigationIconContentColor = MaterialTheme.colorScheme.onSurface,
                ),
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.back),
                        )
                    }
                },
            )
        },
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding)) {
            if (uiState.isLoading) {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
                return@Column
            }

            uiState.errorMessage?.let { message ->
                MessageBanner(
                    text = message,
                    container = MaterialTheme.colorScheme.errorContainer,
                    content = MaterialTheme.colorScheme.onErrorContainer,
                    onRetry = onRetry,
                )
            }
            uiState.successMessage?.let { message ->
                MessageBanner(
                    text = message,
                    container = MaterialTheme.colorScheme.secondaryContainer,
                    content = MaterialTheme.colorScheme.onSecondaryContainer,
                    onRetry = null,
                )
            }

            ScrollableTabRow(
                selectedTabIndex = selectedTab,
                edgePadding = 8.dp,
                containerColor = MaterialTheme.colorScheme.surface,
                contentColor = MaterialTheme.colorScheme.primary,
            ) {
                tabs.forEachIndexed { index, title ->
                    Tab(
                        selected = selectedTab == index,
                        onClick = { selectedTab = index },
                        text = {
                            Text(text = title, fontWeight = FontWeight.SemiBold)
                        },
                    )
                }
            }

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                when (selectedTab) {
                    0 -> ProfileTab(
                        form = uiState.profile,
                        isSaving = uiState.isSaving,
                        onChange = onProfileChange,
                        onSave = onSaveProfile,
                    )
                    1 -> AllergyTab(
                        records = uiState.allergies,
                        form = uiState.allergyForm,
                        isSaving = uiState.isSaving,
                        onChange = onAllergyFormChange,
                        onAdd = onAddAllergy,
                        onDelete = onDeleteAllergy,
                    )
                    2 -> MedicationTab(
                        records = uiState.medications,
                        form = uiState.medicationForm,
                        isSaving = uiState.isSaving,
                        onChange = onMedicationFormChange,
                        onAdd = onAddMedication,
                        onDelete = onDeleteMedication,
                    )
                    else -> ContactTab(
                        records = uiState.contacts,
                        form = uiState.contactForm,
                        isSaving = uiState.isSaving,
                        onChange = onContactFormChange,
                        onAdd = onAddContact,
                        onDelete = onDeleteContact,
                    )
                }
            }
        }
    }
}

@Composable
private fun ProfileTab(
    form: ProfileForm,
    isSaving: Boolean,
    onChange: (ProfileForm) -> Unit,
    onSave: () -> Unit,
) {
    SectionTitle("Datos clínicos")
    EnumSelector(
        label = "Tipo de sangre",
        options = BloodType.entries,
        selected = form.bloodType,
        allowNone = true,
        onSelect = { onChange(form.copy(bloodType = it)) },
    )
    EnumSelector(
        label = "Factor RH",
        options = RhFactor.entries,
        selected = form.rhFactor,
        allowNone = true,
        display = { it.label() },
        onSelect = { onChange(form.copy(rhFactor = it)) },
    )
    OutlinedTextField(
        value = form.dateOfBirth,
        onValueChange = { onChange(form.copy(dateOfBirth = it)) },
        label = { Text("Fecha de nacimiento (AAAA-MM-DD)") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.heightCm,
        onValueChange = { onChange(form.copy(heightCm = it)) },
        label = { Text("Estatura (cm)") },
        singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.weightKg,
        onValueChange = { onChange(form.copy(weightKg = it)) },
        label = { Text("Peso (kg)") },
        singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
        modifier = Modifier.fillMaxWidth(),
    )
    Row(verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f)) {
            Text("Donante de órganos", style = MaterialTheme.typography.bodyLarge)
            Text(
                "Dato opcional",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Switch(
            checked = form.organDonor == true,
            onCheckedChange = { onChange(form.copy(organDonor = it)) },
        )
    }
    OutlinedTextField(
        value = form.chronicConditions,
        onValueChange = { onChange(form.copy(chronicConditions = it)) },
        label = { Text("Condiciones crónicas") },
        minLines = 3,
        modifier = Modifier.fillMaxWidth(),
    )
    Button(
        onClick = onSave,
        enabled = !isSaving,
        shape = MaterialTheme.shapes.medium,
        modifier = Modifier
            .fillMaxWidth()
            .height(50.dp),
    ) {
        Text(stringResource(R.string.save_profile_button))
    }
}

@Composable
private fun AllergyTab(
    records: List<Allergy>,
    form: AllergyForm,
    isSaving: Boolean,
    onChange: (AllergyForm) -> Unit,
    onAdd: () -> Unit,
    onDelete: (String) -> Unit,
) {
    SectionTitle("Alergias registradas")
    if (records.isEmpty()) {
        EmptyText("Sin alergias registradas")
    } else {
        records.forEach { allergy ->
            RecordCard(
                title = allergy.allergenName,
                subtitle = "${allergy.category.label()} · ${allergy.severity.label()}",
                onDelete = { onDelete(allergy.id) },
            )
        }
    }

    HorizontalDivider()
    SectionTitle("Nueva alergia")
    OutlinedTextField(
        value = form.allergenName,
        onValueChange = { onChange(form.copy(allergenName = it)) },
        label = { Text("Alérgeno") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    EnumSelector(
        label = "Categoría",
        options = AllergyCategory.entries,
        selected = form.category,
        display = { it.label() },
        onSelect = { value -> value?.let { onChange(form.copy(category = it)) } },
    )
    EnumSelector(
        label = "Severidad",
        options = AllergySeverity.entries,
        selected = form.severity,
        display = { it.label() },
        onSelect = { value -> value?.let { onChange(form.copy(severity = it)) } },
    )
    OutlinedTextField(
        value = form.reaction,
        onValueChange = { onChange(form.copy(reaction = it)) },
        label = { Text("Reacción") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.notes,
        onValueChange = { onChange(form.copy(notes = it)) },
        label = { Text("Notas") },
        minLines = 2,
        modifier = Modifier.fillMaxWidth(),
    )
    Button(
        onClick = onAdd,
        enabled = !isSaving,
        shape = MaterialTheme.shapes.medium,
        modifier = Modifier
            .fillMaxWidth()
            .height(50.dp),
    ) {
        Text("Agregar alergia")
    }
}

@Composable
private fun MedicationTab(
    records: List<Medication>,
    form: MedicationForm,
    isSaving: Boolean,
    onChange: (MedicationForm) -> Unit,
    onAdd: () -> Unit,
    onDelete: (String) -> Unit,
) {
    SectionTitle("Medicamentos registrados")
    if (records.isEmpty()) {
        EmptyText("Sin medicamentos registrados")
    } else {
        records.forEach { medication ->
            val subtitle = buildString {
                append("${medication.dosage} ${medication.doseUnit.label()}")
                append(" · ${medication.frequencyText}")
                if (medication.isControlled) append(" · CONTROLADO")
            }
            RecordCard(
                title = medication.name,
                subtitle = subtitle,
                onDelete = { onDelete(medication.id) },
            )
        }
    }

    HorizontalDivider()
    SectionTitle("Nuevo medicamento")
    OutlinedTextField(
        value = form.name,
        onValueChange = { onChange(form.copy(name = it)) },
        label = { Text("Nombre") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.activeIngredient,
        onValueChange = { onChange(form.copy(activeIngredient = it)) },
        label = { Text("Principio activo") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.dosage,
        onValueChange = { onChange(form.copy(dosage = it)) },
        label = { Text("Dosis") },
        singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
        modifier = Modifier.fillMaxWidth(),
    )
    EnumSelector(
        label = "Unidad de dosis",
        options = DoseUnit.entries,
        selected = form.doseUnit,
        display = { it.label() },
        onSelect = { value -> value?.let { onChange(form.copy(doseUnit = it)) } },
    )
    EnumSelector(
        label = "Vía",
        options = MedicationRoute.entries,
        selected = form.route,
        display = { it.label() },
        onSelect = { value -> value?.let { onChange(form.copy(route = it)) } },
    )
    OutlinedTextField(
        value = form.frequencyText,
        onValueChange = { onChange(form.copy(frequencyText = it)) },
        label = { Text("Frecuencia (ej. cada 8 horas)") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.startDate,
        onValueChange = { onChange(form.copy(startDate = it)) },
        label = { Text("Inicio (AAAA-MM-DD)") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.endDate,
        onValueChange = { onChange(form.copy(endDate = it)) },
        label = { Text("Fin (AAAA-MM-DD, opcional)") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(
            "Medicamento controlado",
            style = MaterialTheme.typography.bodyLarge,
            modifier = Modifier.weight(1f),
        )
        Switch(
            checked = form.isControlled,
            onCheckedChange = { onChange(form.copy(isControlled = it)) },
        )
    }
    if (form.isControlled) {
        OutlinedTextField(
            value = form.controlledSchedule,
            onValueChange = { onChange(form.copy(controlledSchedule = it)) },
            label = { Text("Programa/lista (ej. II)") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = form.prescriberName,
            onValueChange = { onChange(form.copy(prescriberName = it)) },
            label = { Text("Prescriptor") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
        )
    }
    OutlinedTextField(
        value = form.indication,
        onValueChange = { onChange(form.copy(indication = it)) },
        label = { Text("Indicación") },
        minLines = 2,
        modifier = Modifier.fillMaxWidth(),
    )
    Button(
        onClick = onAdd,
        enabled = !isSaving,
        shape = MaterialTheme.shapes.medium,
        modifier = Modifier
            .fillMaxWidth()
            .height(50.dp),
    ) {
        Text("Agregar medicamento")
    }
}

@Composable
private fun ContactTab(
    records: List<EmergencyContact>,
    form: ContactForm,
    isSaving: Boolean,
    onChange: (ContactForm) -> Unit,
    onAdd: () -> Unit,
    onDelete: (String) -> Unit,
) {
    SectionTitle("Contactos de emergencia")
    if (records.isEmpty()) {
        EmptyText("Sin contactos registrados")
    } else {
        records.forEach { contact ->
            RecordCard(
                title = contact.fullName,
                subtitle = "${contact.relationship} · ${contact.phonePrimary} · prioridad ${contact.priority}",
                onDelete = { onDelete(contact.id) },
            )
        }
    }

    HorizontalDivider()
    SectionTitle("Nuevo contacto")
    OutlinedTextField(
        value = form.fullName,
        onValueChange = { onChange(form.copy(fullName = it)) },
        label = { Text("Nombre completo") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.relationship,
        onValueChange = { onChange(form.copy(relationship = it)) },
        label = { Text("Parentesco") },
        singleLine = true,
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.phonePrimary,
        onValueChange = { onChange(form.copy(phonePrimary = it)) },
        label = { Text("Teléfono (E.164, ej. +5215555555555)") },
        singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.phoneSecondary,
        onValueChange = { onChange(form.copy(phoneSecondary = it)) },
        label = { Text("Teléfono alterno (opcional)") },
        singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.email,
        onValueChange = { onChange(form.copy(email = it)) },
        label = { Text("Correo (opcional)") },
        singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.priority,
        onValueChange = { onChange(form.copy(priority = it)) },
        label = { Text("Prioridad (0 = principal)") },
        singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = form.notes,
        onValueChange = { onChange(form.copy(notes = it)) },
        label = { Text("Notas") },
        minLines = 2,
        modifier = Modifier.fillMaxWidth(),
    )
    Button(
        onClick = onAdd,
        enabled = !isSaving,
        shape = MaterialTheme.shapes.medium,
        modifier = Modifier
            .fillMaxWidth()
            .height(50.dp),
    ) {
        Text("Agregar contacto")
    }
}

@Composable
private fun SectionTitle(text: String) {
    Text(
        text = text,
        style = MaterialTheme.typography.titleMedium,
        color = MaterialTheme.colorScheme.primary,
        modifier = Modifier.padding(top = 4.dp),
    )
}

@Composable
private fun EmptyText(text: String) {
    Text(
        text = text,
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
private fun RecordCard(
    title: String,
    subtitle: String,
    onDelete: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface,
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Row(
            modifier = Modifier.padding(start = 16.dp, end = 8.dp, top = 12.dp, bottom = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.titleMedium)
                Text(
                    subtitle,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            IconButton(onClick = onDelete) {
                Icon(
                    Icons.Default.Delete,
                    contentDescription = "Eliminar",
                    tint = MaterialTheme.colorScheme.error,
                )
            }
        }
    }
}

@Composable
private fun MessageBanner(
    text: String,
    container: Color,
    content: Color,
    onRetry: (() -> Unit)?,
) {
    Surface(
        color = container,
        shape = MaterialTheme.shapes.medium,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 6.dp),
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = text,
                color = content,
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.weight(1f),
            )
            if (onRetry != null) {
                TextButton(onClick = onRetry) {
                    Text(stringResource(R.string.retry_button))
                }
            }
        }
    }
}

@Composable
private fun <T> EnumSelector(
    label: String,
    options: List<T>,
    selected: T?,
    allowNone: Boolean = false,
    display: (T) -> String = { it.toString() },
    onSelect: (T?) -> Unit,
) {
    var expanded by remember { mutableStateOf(false) }
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(label, style = MaterialTheme.typography.labelLarge)
        Box(Modifier.fillMaxWidth()) {
            OutlinedButton(
                onClick = { expanded = true },
                shape = MaterialTheme.shapes.small,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = selected?.let(display) ?: "Seleccionar",
                    modifier = Modifier.weight(1f),
                    textAlign = TextAlign.Start,
                )
                Icon(Icons.Default.ArrowDropDown, contentDescription = null)
            }
            DropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false },
            ) {
                if (allowNone) {
                    DropdownMenuItem(
                        text = { Text("Sin especificar") },
                        onClick = {
                            expanded = false
                            onSelect(null)
                        },
                    )
                }
                options.forEach { option ->
                    DropdownMenuItem(
                        text = { Text(display(option)) },
                        onClick = {
                            expanded = false
                            onSelect(option)
                        },
                    )
                }
            }
        }
    }
}

private fun RhFactor.label(): String = when (this) {
    RhFactor.POSITIVE -> "Positivo (+)"
    RhFactor.NEGATIVE -> "Negativo (−)"
}

private fun AllergyCategory.label(): String = when (this) {
    AllergyCategory.MEDICATION -> "Medicamento"
    AllergyCategory.FOOD -> "Alimento"
    AllergyCategory.ENVIRONMENTAL -> "Ambiental"
    AllergyCategory.INSECT -> "Insecto"
    AllergyCategory.OTHER -> "Otro"
}

private fun AllergySeverity.label(): String = when (this) {
    AllergySeverity.MILD -> "Leve"
    AllergySeverity.MODERATE -> "Moderada"
    AllergySeverity.SEVERE -> "Severa"
    AllergySeverity.ANAPHYLAXIS -> "Anafilaxia"
    AllergySeverity.UNKNOWN -> "Desconocida"
}

private fun DoseUnit.label(): String = when (this) {
    DoseUnit.MG -> "mg"
    DoseUnit.ML -> "ml"
    DoseUnit.MCG -> "mcg"
    DoseUnit.G -> "g"
    DoseUnit.IU -> "UI"
    DoseUnit.DROPS -> "gotas"
    DoseUnit.PUFFS -> "inhalaciones"
    DoseUnit.TABLET -> "tableta"
    DoseUnit.CAPSULE -> "cápsula"
    DoseUnit.OTHER -> "otra"
}

private fun MedicationRoute.label(): String = when (this) {
    MedicationRoute.ORAL -> "Oral"
    MedicationRoute.IV -> "Intravenosa"
    MedicationRoute.IM -> "Intramuscular"
    MedicationRoute.TOPICAL -> "Tópica"
    MedicationRoute.INHALED -> "Inhalada"
    MedicationRoute.SUBLINGUAL -> "Sublingual"
    MedicationRoute.RECTAL -> "Rectal"
    MedicationRoute.OTHER -> "Otra"
}
