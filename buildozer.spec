[app]
title = Pasiflonet Test
package.name = pasiflonet.test
package.domain = org.azre.pasiflonet
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.5

# --- ניקוי עמוק: רק פייתון וממשק גרפי ---
requirements = python3,kivy,kivymd,pillow

# --- הגדרות מסך ---
orientation = sensor
fullscreen = 0

# --- הרשאות בסיסיות בלבד ---
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# --- הגדרות אנדרואיד סטנדרטיות ---
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
