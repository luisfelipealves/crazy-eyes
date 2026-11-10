plugins { id("com.android.application") }

android {
    namespace = "com.luisfelipe.crazyeyes.watchface"
    compileSdk = 36
    defaultConfig {
        applicationId = "com.luisfelipe.crazyeyes.watchface.shake"
        minSdk = 33
        targetSdk = 36
        versionCode = 4
        versionName = "0.1.3-experimental"
    }
    buildTypes {
        getByName("debug") {
            // AGP generates R classes even without sources. R8 removes them so the WFF APK has no DEX.
            isMinifyEnabled = true
            isShrinkResources = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
    signingConfigs {
        getByName("debug") {
            val localKey = rootProject.file("ci/debug.keystore")
            if (localKey.isFile) {
                storeFile = localKey
                storePassword = "android"
                keyAlias = "androiddebugkey"
                keyPassword = "android"
            }
        }
    }
}
