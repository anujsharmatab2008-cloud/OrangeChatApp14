[app]
title = Orange Chat App
package.name = orangechatapp
package.domain = org.anuj
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,requests,urllib3,certifi,openssl
orientation = portrait

# ---------------------------------------------
# Android specific configurations
# ---------------------------------------------
fullscreen = 1
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b

android.logcat_filters = *:S python:D
android.archs = arm64-v8a

# Tells buildozer to download modern cmdline-tools automatically
android.enable_text_sdkmanager = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
