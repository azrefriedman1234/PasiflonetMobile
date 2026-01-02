package com.pasiflon.mobile

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.media3.common.MediaItem
import androidx.media3.effect.OverlayEffect
import androidx.media3.effect.BitmapOverlay
import androidx.media3.effect.TextureOverlay
import androidx.media3.transformer.Transformer
import androidx.media3.transformer.Composition
import androidx.media3.transformer.EditedMediaItem
import androidx.media3.transformer.ExportException
import androidx.media3.transformer.ExportResult
import com.google.common.collect.ImmutableList
import java.io.File

class EditorActivity : AppCompatActivity() {
    private var isProcessing = false
    private var videoUriString: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_editor)

        val watermarkView = findViewById<ImageView>(R.id.watermark_overlay)
        val btnExport = findViewById<Button>(R.id.btn_export)
        val btnAddBlur = findViewById<Button>(R.id.btn_add_blur) // נשאיר כפתור דמה כרגע
        
        // הסתרת הטשטוש כי ב-Media3 זה מורכב יותר, נתמקד בלוגו קודם
        findViewById<View>(R.id.blur_overlay).visibility = View.GONE
        btnAddBlur.visibility = View.GONE 

        videoUriString = intent.getStringExtra("video_uri")
        val prefs = getSharedPreferences("pasiflon_prefs", Context.MODE_PRIVATE)
        val targetUsername = prefs.getString("chat_id", "")
        val logoUriStr = prefs.getString("logo_uri", null)

        logoUriStr?.let { watermarkView.setImageURI(Uri.parse(it)) }

        btnExport.setOnClickListener {
            if (isProcessing) return@setOnClickListener
            
            if (targetUsername.isNullOrEmpty()) {
                Toast.makeText(this, "שגיאה: הגדר ערוץ יעד בהגדרות", Toast.LENGTH_LONG).show()
                return@setOnClickListener
            }
            if (logoUriStr == null) {
                Toast.makeText(this, "שגיאה: חובה לבחור לוגו", Toast.LENGTH_LONG).show()
                return@setOnClickListener
            }

            isProcessing = true
            Toast.makeText(this, "מתחיל עיבוד מהיר (Media3)...", Toast.LENGTH_SHORT).show()

            // תהליך הייצוא
            startMedia3Export(Uri.parse(videoUriString), Uri.parse(logoUriStr), targetUsername)
        }
    }

    private fun startMedia3Export(videoUri: Uri, logoUri: Uri, target: String) {
        val outputFile = File(getExternalFilesDir(null), "pasiflon_export_${System.currentTimeMillis()}.mp4")
        
        // 1. יצירת ה-Overlay של הלוגו
        val logoBitmap = getBitmapFromUri(logoUri)
        if (logoBitmap == null) {
            Toast.makeText(this, "שגיאה בטעינת הלוגו", Toast.LENGTH_SHORT).show()
            isProcessing = false
            return
        }

        // יצירת אפקט הלוגו - ממקם אותו בפינה (או איפה שתבחר)
        val imageOverlay = BitmapOverlay.createStaticBitmapOverlay(logoBitmap)
        // הערה: כרגע זה מדביק על כל המסך או במיקום דיפולטיבי.
        // ב-Media3 הגדרת מיקום מדויק דורשת מטריצות, נתחיל בבסיס שיעבוד.
        val overlayEffect = OverlayEffect(ImmutableList.of(imageOverlay))

        // 2. בניית פריט המדיה לעריכה
        val mediaItem = MediaItem.fromUri(videoUri)
        val editedMediaItem = EditedMediaItem.Builder(mediaItem)
            .setEffects(ImmutableList.of(overlayEffect))
            .build()

        // 3. הגדרת הטרנספורמר
        val transformer = Transformer.Builder(this)
            .addListener(object : Transformer.Listener {
                override fun onCompleted(composition: Composition, result: ExportResult) {
                    runOnUiThread {
                        isProcessing = false
                        Toast.makeText(this@EditorActivity, "הוידאו מוכן! נשלח ל-$target", Toast.LENGTH_LONG).show()
                        finish()
                    }
                }
                override fun onError(composition: Composition, result: ExportResult, exception: ExportException) {
                    runOnUiThread {
                        isProcessing = false
                        Toast.makeText(this@EditorActivity, "שגיאה: ${exception.message}", Toast.LENGTH_LONG).show()
                    }
                }
            })
            .build()

        // 4. התחלת הייצוא
        transformer.start(editedMediaItem, outputFile.absolutePath)
    }

    private fun getBitmapFromUri(uri: Uri): Bitmap? {
        return try {
            val inputStream = contentResolver.openInputStream(uri)
            BitmapFactory.decodeStream(inputStream)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
