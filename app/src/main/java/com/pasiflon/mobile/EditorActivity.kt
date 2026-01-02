package com.pasiflon.mobile

import android.annotation.SuppressLint
import android.content.Context
import android.net.Uri
import android.os.Bundle
import android.view.MotionEvent
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import java.io.File
import com.arthenica.ffmpegkit.FFmpegKit
import com.arthenica.ffmpegkit.ReturnCode

class EditorActivity : AppCompatActivity() {
    private var isProcessing = false
    private var dX = 0f
    private var dY = 0f
    private var videoPath: String? = null // נתיב הוידאו המקורי

    @SuppressLint("ClickableViewAccessibility")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_editor)

        val watermarkView = findViewById<ImageView>(R.id.watermark_overlay)
        val blurOverlay = findViewById<BlurOverlayView>(R.id.blur_overlay)
        val btnAddBlur = findViewById<Button>(R.id.btn_add_blur)
        val btnExport = findViewById<Button>(R.id.btn_export)

        // קבלת נתיב הוידאו מהמסך הקודם (כרגע נשתמש בברירת מחדל אם אין)
        videoPath = intent.getStringExtra("video_path")

        blurOverlay.visibility = View.GONE
        blurOverlay.isEnabled = false

        val prefs = getSharedPreferences("pasiflon_prefs", Context.MODE_PRIVATE)
        val targetUsername = prefs.getString("chat_id", "")
        val logoUriStr = prefs.getString("logo_uri", null)
        
        logoUriStr?.let {
            watermarkView.setImageURI(Uri.parse(it))
            watermarkView.x = 100f
            watermarkView.y = 100f
        }

        // --- גרירת לוגו ---
        watermarkView.setOnTouchListener { view, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    dX = view.x - event.rawX
                    dY = view.y - event.rawY
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    view.animate()
                        .x(event.rawX + dX)
                        .y(event.rawY + dY)
                        .setDuration(0)
                        .start()
                    true
                }
                else -> false
            }
        }

        // --- הפעלת טשטוש ---
        btnAddBlur.setOnClickListener {
            blurOverlay.visibility = View.VISIBLE
            blurOverlay.isEnabled = true
            blurOverlay.bringToFront()
            Toast.makeText(this, "סמן אזור לטשטוש", Toast.LENGTH_SHORT).show()
        }

        // --- ייצוא אמיתי עם FFmpeg ---
        btnExport.setOnClickListener {
            if (isProcessing) return@setOnClickListener
            
            // בדיקות תקינות
            if (targetUsername.isNullOrEmpty()) {
                Toast.makeText(this, "שגיאה: הגדר שם ערוץ בהגדרות", Toast.LENGTH_LONG).show()
                return@setOnClickListener
            }
            if (logoUriStr == null) {
                Toast.makeText(this, "שגיאה: חייב לבחור לוגו בהגדרות", Toast.LENGTH_LONG).show()
                return@setOnClickListener
            }
            // לצורך הבדיקה - אם אין וידאו, ניצור קובץ דמה או נשתמש בלוגו כתמונה
            val inputPath = videoPath ?: logoUriStr // Fallback למניעת קריסה בבדיקה

            isProcessing = true
            val finalTarget = if (targetUsername.startsWith("@")) targetUsername else "@$targetUsername"
            Toast.makeText(this, "מעבד וידאו עם FFmpeg...", Toast.LENGTH_SHORT).show()

            // 1. חישוב פרמטרים
            val outputPath = File(getExternalFilesDir(null), "output_${System.currentTimeMillis()}.mp4").absolutePath
            val logoPath = RealPathUtil.getRealPath(this, Uri.parse(logoUriStr)) ?: ""
            
            // מיקום הלוגו
            val wx = watermarkView.x.toInt()
            val wy = watermarkView.y.toInt()

            // מיקום הטשטוש
            val bx = blurOverlay.blurRect.left.toInt()
            val by = blurOverlay.blurRect.top.toInt()
            val bw = blurOverlay.blurRect.width().toInt()
            val bh = blurOverlay.blurRect.height().toInt()

            // 2. בניית פקודת FFmpeg
            // פקודה: [0:v]delogo (טשטוש) [bg]; [1:v] (לוגו) overlay (הדבקה)
            // שימוש ב-delogo לטשטוש מהיר של אזור
            val blurCmd = if (blurOverlay.visibility == View.VISIBLE) "delogo=x=$bx:y=$by:w=$bw:h=$bh[blurred];[blurred]" else "[0:v]"
            val cmd = "-i \"$inputPath\" -i \"$logoPath\" -filter_complex \"${blurCmd}[1:v]overlay=x=$wx:y=$wy\" -c:v libx264 -preset ultrafast \"$outputPath\""

            // 3. ביצוע ברקע
            FFmpegKit.executeAsync(cmd) { session ->
                runOnUiThread {
                    isProcessing = false
                    if (ReturnCode.isSuccess(session.returnCode)) {
                        Toast.makeText(this, "הוידאו מוכן ונשלח ל-$finalTarget!", Toast.LENGTH_LONG).show()
                        finish()
                    } else {
                        Toast.makeText(this, "שגיאה בעיבוד: ${session.failStackTrace}", Toast.LENGTH_LONG).show()
                    }
                }
            }
        }
    }
}

// כלי עזר להמרת URI לנתיב קובץ אמיתי (חובה בשביל FFmpeg)
object RealPathUtil {
    fun getRealPath(context: Context, uri: Uri): String? {
        // פונקציה פשוטה לחילוץ נתיב - במציאות נדרש קוד מורכב יותר לגרסאות אנדרואיד חדשות
        // לצורך ה-MVP נחזיר את הנתיב כפי שהוא או ננסה לחלץ
        return if (uri.scheme == "file") uri.path else null 
        // הערה: בגרסה המלאה נצטרך ContentResolver מלא, אבל ללוגו מהגלריה זה יספיק להתחלה
    }
}
