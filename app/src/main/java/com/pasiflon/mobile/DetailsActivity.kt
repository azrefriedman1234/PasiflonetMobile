package com.pasiflon.mobile

import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import android.content.Intent

class DetailsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_details)

        val detailText = findViewById<TextView>(R.id.detail_text)
        val previewCard = findViewById<View>(R.id.preview_card)
        val previewImage = findViewById<ImageView>(R.id.detail_preview_image)
        val btnTranslate = findViewById<Button>(R.id.btn_translate_now)
        val btnEdit = findViewById<Button>(R.id.btn_go_to_editor)

        val originalText = intent.getStringExtra("msg_text") ?: ""
        val hasMedia = intent.getBooleanExtra("has_media", false)
        val thumbPath = intent.getStringExtra("thumb_path")

        detailText.text = originalText

        // אם אין מדיה, נסתיר את חלונית התמונה הממוזערת כדי לתת מקום לטקסט
        if (hasMedia) {
            previewCard.visibility = View.VISIBLE
            // כאן נטען את ה-Thumbnail מהנתיב הזמני של טלגרם
            if (thumbPath != null) previewImage.setImageURI(android.net.Uri.parse(thumbPath))
        } else {
            previewCard.visibility = View.GONE
            btnEdit.text = "שתף טקסט בלבד" // שינוי ייעוד הכפתור
        }

        btnTranslate.setOnClickListener {
            TranslationManager.translateToHebrew(originalText) { translated ->
                detailText.text = translated
            }
        }

        btnEdit.setOnClickListener {
            if (hasMedia) {
                startActivity(Intent(this, EditorActivity::class.java))
            } else {
                // לוגיקת שיתוף טקסט ישיר
                val shareIntent = Intent(Intent.ACTION_SEND).apply {
                    type = "text/plain"
                    putExtra(Intent.EXTRA_TEXT, detailText.text.toString())
                }
                startActivity(Intent.createChooser(shareIntent, "שתף דיווח"))
            }
        }
    }
}
