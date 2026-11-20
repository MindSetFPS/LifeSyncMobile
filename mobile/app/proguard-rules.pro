# Conserver los modelos serializados usados por Retrofit/kotlinx.serialization
-keepattributes AnnotationDefault, RuntimeVisibleAnnotations, Signature
-keepclassmembers class com.lifesync.mobile.data.remote.dto.** { *; }
-dontwarn kotlinx.serialization.**
