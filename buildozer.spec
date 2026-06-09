[app]

# (string) Title of your application
title = Orange Chat App

# (string) Package name
package.name = orangechatapp

# (string) Package domain (needed for android packaging)
package.domain = org.anuj

# (string) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let's include py and png files)
source.include_exts = py,png,jpg,kv,atlas

# (string) Application versioning
version = 0.1

# (list) Application requirements
# WARNING: If you are using KivyMD, add kivymd here!
requirements = python3,kivy,requests,urllib3

# (str) Supported orientations
orientation = portrait

# ---------------------------------------------
# Android specific configurations
# ---------------------------------------------

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions your chat app needs (Internet is critical for chat!)
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 28c

# (bool) Use logcat filters to clear up spam during debugging
android.logcat_filters = *:S python:D

# (str) The Android arch to build for (GitHub runners love arm64)
android.archs = arm64-v8a

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug and outputs)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
