package com.pasiflon.mobile

import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import android.net.Uri
import android.content.Context
import java.io.File

class EditorActivity : AppCompatActivity() {
    private var isProcessing = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_editor)

        val watermarkView = findViewById<ImageView>(R.id.watermark_overlay)
        val blurOverlay = findViewById<BlurOverlayView>(R.id.blur_overlay)
        val btnExport = findViewById<Button>(R.id.btn_export)

        // טעינת לוגו ו-Chat ID
        val prefs = getSharedPreferences("pasiflon_prefs", Context.MODE_PRIVATE)
        val targetChatId = prefs.getString("chat_id", "")
        
        prefs.getString("logo_uri", null)?.let {
            watermarkView.setImageURI(Uri.parse(it))
        }

        btnExport.setOnClickListener {
            if (isProcessing) return@setOnClickListener
            
            if (targetChatId.isNullOrEmpty()) {
                Toast.makeText(this, "שגיאה: לא הוגדר ערוץ יעד בהגדרות!", Toast.LENGTH_LONG).show()
                return@setOnClickListener
            }

            isProcessing = true
            Toast.makeText(this, "מעבד ושולח לערוץ $targetChatId...", Toast.LENGTH_SHORT).show()
            
            // סימולציית תהליך שליחה ב-API
            // כאן יכנס בעתיד הקוד של TdApi.SendMessage
            btnExport.postDelayed({
                isProcessing = false
                Toast.makeText(this, "הקובץ נשלח לטלגרם בהצלחה! ✅", Toast.LENGTH_LONG).show()
                finish() // סוגר את העורך וחוזר לטבלה
            }, 3000)
        }
    }
}
