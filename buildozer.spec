[app]
title = Pasiflonet Final
package.name = pasiflonet.final
package.domain = org.azre.pasiflonet
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.5

# --- התיקון: מחקנו את pyjnius מהרשימה כי זה שבר את הבנייה ---
requirements = python3,kivy,kivymd,telethon,pillow,deep-translator,arabic-reshaper,python-bidi,openssl,requests

# תמיכה בכל המעבדים
android.archs = arm64-v8a, armeabi-v7a

orientation = landscape
fullscreen = 1

# הרשאות מפורשות (כולל אנדרואיד 13)
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,WAKE_LOCK,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO

android.api = 33
android.minapi = 21
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
