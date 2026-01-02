package com.pasiflon.mobile

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.activity.result.contract.ActivityResultContracts

class SettingsActivity : AppCompatActivity() {
    private var selectedLogoUri: String? = null
    private lateinit var logoPreview: ImageView

    private val getLogo = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let {
            selectedLogoUri = it.toString()
            logoPreview.setImageURI(it)
            logoPreview.visibility = android.view.View.VISIBLE
            Toast.makeText(this, "לוגו נבחר בהצלחה", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // יצירת ממשק בסיסי כולל ImageView לתצוגה מקדימה
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(android.graphics.Color.parseColor("#050505"))
            setPadding(50, 50, 50, 50)
        }

        val title = TextView(this).apply {
            text = "הגדרות סייבר"
            setTextColor(android.graphics.Color.parseColor("#00F2FF"))
            textSize = 22f
            gravity = android.view.Gravity.CENTER
        }

        val apiIdField = EditText(this).apply { hint = "API ID"; setTextColor(android.graphics.Color.WHITE) }
        val apiHashField = EditText(this).apply { hint = "API Hash"; setTextColor(android.graphics.Color.WHITE) }
        
        logoPreview = ImageView(this).apply {
            layoutParams = LinearLayout.LayoutParams(300, 300).apply { gravity = android.view.Gravity.CENTER }
            visibility = android.view.View.GONE
        }

        val btnPick = Button(this).apply {
            text = "בחר לוגו מהגלריה"
            backgroundTintList = android.content.res.ColorStateList.valueOf(android.graphics.Color.parseColor("#FF00E5"))
            setOnClickListener { getLogo.launch("image/*") }
        }

        val btnSave = Button(this).apply {
            text = "שמור הכל"
            backgroundTintList = android.content.res.ColorStateList.valueOf(android.graphics.Color.parseColor("#00F2FF"))
            setOnClickListener {
                val prefs = getSharedPreferences("pasiflon_prefs", Context.MODE_PRIVATE)
                prefs.edit().apply {
                    putString("api_id", apiIdField.text.toString())
                    putString("api_hash", apiHashField.text.toString())
                    putString("logo_uri", selectedLogoUri)
                    apply()
                }
                Toast.makeText(this@SettingsActivity, "נשמר!", Toast.LENGTH_SHORT).show()
                finish()
            }
        }

        layout.addView(title)
        layout.addView(apiIdField)
        layout.addView(apiHashField)
        layout.addView(btnPick)
        layout.addView(logoPreview)
        layout.addView(btnSave)
        setContentView(layout)

        // טעינה ראשונית אם קיים
        val prefs = getSharedPreferences("pasiflon_prefs", Context.MODE_PRIVATE)
        apiIdField.setText(prefs.getString("api_id", ""))
        apiHashField.setText(prefs.getString("api_hash", ""))
        prefs.getString("logo_uri", null)?.let {
            selectedLogoUri = it
            logoPreview.setImageURI(Uri.parse(it))
            logoPreview.visibility = android.view.View.VISIBLE
        }
    }
}
