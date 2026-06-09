[app]
title = Orange Chat App
package.name = orangechatapp
package.domain = org.anuj
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Stable dependencies using explicit pairing syntax
requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,urllib3,certifi,openssl

orientation = portrait

# ---------------------------------------------
# Android specific configurations
# ---------------------------------------------
fullscreen = 1
android.permissions = INTERNET
android.api = 33
android.minapi = 21

# FIXED: Removed explicit '25b' to let Buildozer use the runner's pre-configured NDK safely
android.archs = arm64-v8a
android.logcat_filters = *:S python:D

android.enable_text_sdkmanager = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
