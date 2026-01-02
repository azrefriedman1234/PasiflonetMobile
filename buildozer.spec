[app]
title = Pasiflonet Test
package.name = pasiflonet.test
package.domain = org.azre.pasiflonet
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.6

# גרסה קלה ללא ספריות כבדות (לבדיקת קריסות)
requirements = python3,kivy,kivymd,pillow

# --- התיקון: חזרנו ל-landscape ---
orientation = landscape
fullscreen = 1

# הרשאות בסיסיות
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
