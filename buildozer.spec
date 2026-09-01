[app]
# (str) Title of your application
title = Galactic Voyager

# (str) Package name
package.name = galacticvoyager

# (str) Package domain (needed for android packaging)
package.domain = com.gaurav99940

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,wav,mp3,ogg,dat

# (str) Application versioning
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pygame

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = VIBRATE,INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
