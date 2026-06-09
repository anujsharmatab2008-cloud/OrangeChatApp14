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

# Match GitHub's pre-installed global systems perfectly
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.ndk = 25b

android.logcat_filters = *:S python:D
android.archs = arm64-v8a
android.enable_text_sdkmanager = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
