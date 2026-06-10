[app]
title = Orange Chat App
package.name = orangechatapp
package.domain = org.anuj
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# UPDATED: We removed the hardcoded old versions so Buildozer grabs the modern matching pair
requirements = python3,kivy,kivymd,requests,urllib3,certifi

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
