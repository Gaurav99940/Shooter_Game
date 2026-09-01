[app]
# App Identity
title = Galactic Voyager Ace Shooter
package.name = galacticvoyager
package.domain = com.gaurav99940

# Version
version = 1.0

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,mp3,ogg

# Requirements
requirements = python3,pygame

# Orientation
orientation = portrait

# Icon & Splash (create these images)
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# Android
android.permissions = VIBRATE, INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Build
android.release_artifact = apk
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
