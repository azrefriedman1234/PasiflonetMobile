package com.pasiflon.mobile

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import android.content.Context
import android.net.Uri
import androidx.activity.result.contract.ActivityResultContracts

class SettingsActivity : AppCompatActivity() {
    private var selectedLogoUri: String? = null
    private lateinit var logoPreview: ImageView

    private val getLogo = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let {
            selectedLogoUri = it.toString()
            logoPreview.setImageURI(it)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        val apiIdField = findViewById<EditText>(R.id.edit_api_id)
        val apiHashField = findViewById<EditText>(R.id.edit_api_hash)
        val chatIdField = findViewById<EditText>(R.id.edit_chat_id)
        logoPreview = findViewById(R.id.logo_preview)
        val btnSave = findViewById<Button>(R.id.btn_save)
        val btnPick = findViewById<Button>(R.id.btn_pick_logo)

        val prefs = getSharedPreferences("pasiflon_prefs", Context.MODE_PRIVATE)
        apiIdField.setText(prefs.getString("api_id", ""))
        apiHashField.setText(prefs.getString("api_hash", ""))
        chatIdField.setText(prefs.getString("chat_id", ""))
        
        prefs.getString("logo_uri", null)?.let {
            selectedLogoUri = it
            logoPreview.setImageURI(Uri.parse(it))
        }

        btnPick.setOnClickListener { getLogo.launch("image/*") }

        btnSave.setOnClickListener {
            prefs.edit().apply {
                putString("api_id", apiIdField.text.toString())
                putString("api_hash", apiHashField.text.toString())
                putString("chat_id", chatIdField.text.toString())
                putString("logo_uri", selectedLogoUri)
                apply()
            }
            Toast.makeText(this, "הגדרות נשמרו!", Toast.LENGTH_SHORT).show()
            finish()
        }
    }
}
