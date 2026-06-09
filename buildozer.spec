[app]

# (string) Title of your application
title = Orange Chat App

# (string) Package name
package.name = orangechatapp

# (string) Package domain (needed for android packaging)
package.domain = org.anuj

# (string) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (string) Application versioning
version = 0.1

# (list) Application requirements
# Added certifi and openssl so your chat app can securely connect to the internet/Firebase
requirements = python3,kivy,requests,urllib3,certifi,openssl

# (str) Supported orientations
orientation = portrait

# ---------------------------------------------
# Android specific configurations
# ---------------------------------------------

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions your chat app needs
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use logcat filters to clear up spam during debugging
android.logcat_filters = *:S python:D

# (str) The Android arch to build for
android.archs = arm64-v8a

# 🔥 FIXES THE SDKMANAGER ERROR: Forces buildozer to use modern tools layout
android.enable_text_sdkmanager = True

# Automatically accept licenses inside the build tool config
android.accept_sdk_license = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug and outputs)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
