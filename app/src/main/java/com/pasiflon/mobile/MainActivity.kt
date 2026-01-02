package com.pasiflon.mobile

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.graphics.Color

data class TelegramMsg(val id: Long, val sender: String, var text: String, val hasMedia: Boolean = false)

class MainActivity : AppCompatActivity() {
    private val messages = mutableListOf<TelegramMsg>()
    private lateinit var adapter: MessageAdapter
    private var loginDialog: AlertDialog? = null

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        if (permissions.entries.all { it.value }) {
            Toast.makeText(this, "הרשאות מדיה אושרו", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        checkAndRequestPermissions()

        findViewById<ImageButton>(R.id.btn_settings).setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        val recycler = findViewById<RecyclerView>(R.id.messages_recycler)
        adapter = MessageAdapter(messages)
        recycler.layoutManager = LinearLayoutManager(this)
        recycler.adapter = adapter
    }

    // הבדיקה עוברת לכאן כדי שתרוץ בכל פעם שחוזרים למסך הראשי
    override fun onResume() {
        super.onResume()
        checkLoginStatus()
    }

    private fun checkAndRequestPermissions() {
        val permissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            arrayOf(Manifest.permission.READ_MEDIA_IMAGES, Manifest.permission.READ_MEDIA_VIDEO)
        } else {
            arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE)
        }
        
        if (permissions.any { ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }) {
            requestPermissionLauncher.launch(permissions)
        }
    }

    private fun checkLoginStatus() {
        val prefs = getSharedPreferences("pasiflon_prefs", Context.MODE_PRIVATE)
        val apiId = prefs.getString("api_id", "")
        val isLoggedIn = prefs.getBoolean("is_logged_in", false)

        // תרחיש 1: אין API מוגדר -> חייב לשלוח להגדרות
        if (apiId.isNullOrEmpty()) {
            showMissingApiDialog()
            return
        }

        // תרחיש 2: יש API אבל לא מחובר -> דיאלוג התחברות
        if (!isLoggedIn) {
            showPhoneLoginDialog()
        } else {
            // תרחיש 3: מחובר -> טוען הודעות (סימולציה כרגע)
            if (messages.isEmpty()) {
                messages.add(TelegramMsg(1, "מערכת", "המערכת מחוברת ומוכנה לפעולה.", false))
                adapter.notifyDataSetChanged()
            }
        }
    }

    private fun showMissingApiDialog() {
        if (loginDialog?.isShowing == true) return 

        loginDialog = AlertDialog.Builder(this)
            .setTitle("הגדרה ראשונית נדרשת")
            .setMessage("כדי להפעיל את המערכת, עליך להזין תחילה את ה-API ID וה-Hash של טלגרם.")
            .setPositiveButton("עבור להגדרות כעת") { _, _ ->
                startActivity(Intent(this, SettingsActivity::class.java))
            }
            .setCancelable(false) // לא נותן לסגור בלי ללכת להגדרות
            .show()
    }

    private fun showPhoneLoginDialog() {
        if (loginDialog?.isShowing == true) return

        val builder = AlertDialog.Builder(this)
        builder.setTitle("התחברות לטלגרם")
        
        val layout = LinearLayout(this)
        layout.orientation = LinearLayout.VERTICAL
        layout.setPadding(50, 20, 50, 0)
        
        val input = EditText(this)
        input.hint = "מספר טלפון (+972...)"
        input.inputType = android.text.InputType.TYPE_CLASS_PHONE
        layout.addView(input)
        
        builder.setView(layout)

        builder.setPositiveButton("שלח קוד") { _, _ ->
            val phone = input.text.toString()
            if (phone.isNotEmpty()) showCodeLoginDialog(phone)
        }
        
        // התיקון שלך: כפתור קיצור להגדרות מתוך מסך הלוגין
        builder.setNeutralButton("פתח הגדרות API") { _, _ ->
            startActivity(Intent(this, SettingsActivity::class.java))
        }
        
        builder.setCancelable(false)
        loginDialog = builder.show()
    }

    private fun showCodeLoginDialog(phone: String) {
        val builder = AlertDialog.Builder(this)
        builder.setTitle("אימות דו-שלבי")
        builder.setMessage("קוד נשלח ל-$phone")
        
        val input = EditText(this)
        input.hint = "קוד אימות"
        input.inputType = android.text.InputType.TYPE_CLASS_NUMBER
        builder.setView(input)

        builder.setPositiveButton("התחבר") { _, _ ->
            // שמירת סטטוס התחברות
            getSharedPreferences("pasiflon_prefs", Context.MODE_PRIVATE)
                .edit().putBoolean("is_logged_in", true).apply()
            
            Toast.makeText(this, "התחברת בהצלחה! טוען נתונים...", Toast.LENGTH_SHORT).show()
            recreate() // רענון המסך כדי להעלים את הדיאלוגים ולטעון את המצב החדש
        }
        
        builder.setCancelable(false)
        builder.show()
    }

    inner class MessageAdapter(private val list: List<TelegramMsg>) : RecyclerView.Adapter<MessageAdapter.ViewHolder>() {
        inner class ViewHolder(v: View) : RecyclerView.ViewHolder(v) {
            val sender: TextView = v.findViewById(android.R.id.text1)
            val content: TextView = v.findViewById(android.R.id.text2)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            val v = LayoutInflater.from(parent.context).inflate(android.R.layout.simple_list_item_2, parent, false)
            return ViewHolder(v)
        }

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val msg = list[position]
            holder.sender.text = msg.sender
            holder.sender.setTextColor(Color.parseColor("#00F2FF"))
            holder.content.text = msg.text
            holder.content.setTextColor(Color.WHITE)
            
            holder.itemView.setOnClickListener {
                val intent = Intent(this@MainActivity, DetailsActivity::class.java)
                intent.putExtra("msg_text", msg.text)
                intent.putExtra("has_media", msg.hasMedia)
                startActivity(intent)
            }
        }
        override fun getItemCount() = list.size
    }
}
