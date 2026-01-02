[app]
title = Pasiflonet Pro
package.name = pasiflonet
package.domain = org.azre.pasiflonet
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp4
version = 0.2

# --- קריטי: דרישות מערכת מעודכנות ---
requirements = python3,kivy,kivymd,telethon,pillow,deep-translator,arabic-reshaper,python-bidi,openssl,requests,ffmpeg

# --- קריטי: הגדרה לרוחב ---
orientation = landscape
fullscreen = 1

# --- הרשאות ---
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# --- הגדרות אנדרואיד ---
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
