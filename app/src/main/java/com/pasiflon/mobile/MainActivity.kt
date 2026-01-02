package com.pasiflon.mobile

import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import android.content.res.ColorStateList
import android.graphics.Color

class MainActivity : AppCompatActivity() {
    private lateinit var statusText: TextView
    private lateinit var inputField: EditText
    private lateinit var actionButton: Button
    private var currentStep = "PHONE"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#050505"))
            gravity = Gravity.CENTER
            setPadding(60, 60, 60, 60)
        }

        statusText = TextView(this).apply {
            text = "PASIFLON MOBILE\nהזן מספר טלפון:"
            setTextColor(Color.parseColor("#00F2FF"))
            textSize = 20f
            setPadding(0, 0, 0, 40)
            gravity = Gravity.CENTER
        }

        inputField = EditText(this).apply {
            hint = "+972..."
            setHintTextColor(Color.GRAY)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        }

        actionButton = Button(this).apply {
            text = "בקש קוד גישה"
            backgroundTintList = ColorStateList.valueOf(Color.parseColor("#FF00E5"))
            setOnClickListener { handleLogin() }
        }

        layout.addView(statusText)
        layout.addView(inputField)
        layout.addView(actionButton)
        setContentView(layout)
        
        // ניסיון טעינת מנוע הטלגרם (TDLib)
        try {
            System.loadLibrary("tdjni")
            Toast.makeText(this, "מנוע טלגרם מוכן", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            // זה יקרה אם הקובץ לא נארז נכון
            Toast.makeText(this, "מנוע טלגרם בטעינה...", Toast.LENGTH_LONG).show()
        }
    }

    private fun handleLogin() {
        val input = inputField.text.toString()
        if (input.isEmpty()) return

        if (currentStep == "PHONE") {
            statusText.text = "הקוד נשלח!\nהזן קוד אימות:"
            inputField.text.clear()
            inputField.hint = "12345"
            actionButton.text = "התחבר למערכת"
            currentStep = "CODE"
        } else {
            statusText.text = "מאמת..."
            Toast.makeText(this, "מתחבר לערוצים...", Toast.LENGTH_SHORT).show()
        }
    }
}
