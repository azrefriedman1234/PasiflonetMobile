package com.pasiflon.mobile

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(0xFF050505.toInt())
        }
        val tv = TextView(this).apply {
            text = "פסיפלונט מובייל - מערכת מחוברת"
            setTextColor(0xFF00F2FF.toInt())
            textSize = 24f
            setPadding(50, 50, 50, 50)
        }
        layout.addView(tv)
        setContentView(layout)
    }
}
