[app]
title = Orange Chat App
package.name = orangechatapp
package.domain = org.anuj
source.dir = .
# ✅ FIXED: Added ttf so the engine renders assets perfectly
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1

# ✅ FIXED: Pointing Buildozer directly to your new 512x512 icon file
icon.filename = %(source.dir)s/icon.png

# ✅ FIXED: Cleaned out the copy-paste text clutter and completely removed kivymd
requirements = python3,kivy,urllib3,certifi,charset_normalizer
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
