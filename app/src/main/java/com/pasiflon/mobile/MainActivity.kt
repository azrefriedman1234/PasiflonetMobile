package com.pasiflon.mobile
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.widget.TextView
import android.view.Gravity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tv = TextView(this).apply {
            text = "SYSTEM ACTIVE\nPasiflon Mobile"
            setTextColor(0xFF00F2FF.toInt())
            textSize = 30f
            gravity = Gravity.CENTER
        }
        setContentView(tv)
    }
}
