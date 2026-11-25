# Conserver los modelos serializados usados por Retrofit/kotlinx.serialization
-keepattributes AnnotationDefault, RuntimeVisibleAnnotations, Signature
-keepclassmembers class com.lifesync.mobile.data.remote.dto.** { *; }
-dontwarn kotlinx.serialization.**
# Tink (androidx.security) referencia anotaciones de errorprone no empaquetadas.
-dontwarn com.google.errorprone.annotations.**
