[app]
title = Pasiflonet Pro
package.name = pasiflonet.pro
package.domain = org.azre.pasiflonet
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.3

requirements = python3,kivy,kivymd,telethon,pillow,deep-translator,arabic-reshaper,python-bidi,openssl,requests

# תמיכה בכל המעבדים (למניעת קריסה בפתיחה)
android.archs = arm64-v8a, armeabi-v7a

orientation = landscape
fullscreen = 1

# --- התיקון הקריטי: הרשאות לאנדרואיד 13 ומעלה ---
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,WAKE_LOCK,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO

android.api = 33
android.minapi = 21
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
