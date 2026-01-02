[app]
title = Pasiflonet Atomic
package.name = pasiflonet.atomic
package.domain = org.azre.pasiflonet
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.7

# --- רק Kivy נקי, בלי KivyMD ---
requirements = python3,kivy

# --- הגדרה קריטית: תמיכה בכל המעבדים ---
android.archs = arm64-v8a, armeabi-v7a

orientation = landscape
fullscreen = 1

# --- בלי הרשאות בכלל (למניעת קריסות אבטחה) ---
# android.permissions = 

android.api = 33
android.minapi = 21
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
