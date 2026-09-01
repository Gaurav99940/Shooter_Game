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
requirements = python3,pygame-ce

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (list) Permissions
android.permissions = VIBRATE,INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) The Android archs to build for (arm64-v8a is modern 64-bit Android)
android.archs = arm64-v8a

# (str) Bootstrap to use
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
