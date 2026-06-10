[app]
title = Orange Chat App
package.name = orangechatapp
package.domain = org.anuj
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# UPDATED: We removed the hardcoded old versions so Buildozer grabs the modern matching pair
# Change this exact line in your buildozer.spec:
requirements = python3==3.11.1,kivy,kivymd==1.2.0,requests,urllib3,certifi,charset_normalizer
orientation = portrait

# ---------------------------------------------
# Android specific configurations
# ---------------------------------------------
fullscreen = 1
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

android.enable_text_sdkmanager = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
