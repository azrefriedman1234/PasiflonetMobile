package com.pasiflon.mobile

import android.os.Bundle
import android.view.*
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.*
import android.graphics.Color
import android.content.Intent

data class TelegramMsg(val id: Long, val sender: String, var text: String)

class MainActivity : AppCompatActivity() {
    private val messages = mutableListOf<TelegramMsg>()
    private lateinit var adapter: MessageAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<ImageButton>(R.id.btn_settings).setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        val recycler = findViewById<RecyclerView>(R.id.messages_recycler)
        adapter = MessageAdapter(messages)
        recycler.layoutManager = LinearLayoutManager(this)
        recycler.adapter = adapter

        // הודעות לדוגמה בערבית לבדיקת התרגום
        messages.add(TelegramMsg(1, "ערוץ עזה", "عاجל: انفجارات في شمال قطاع غزة"))
        messages.add(TelegramMsg(2, "חדשות חוץ", "Breaking news from the border"))
        adapter.notifyDataSetChanged()
    }

    inner class MessageAdapter(private val list: List<TelegramMsg>) : RecyclerView.Adapter<MessageAdapter.ViewHolder>() {
        class ViewHolder(v: View) : RecyclerView.ViewHolder(v) {
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
            
            // לחיצה ארוכה מתרגמת לעברית
            holder.itemView.setOnLongClickListener {
                TranslationManager.translateToHebrew(msg.text) { translated ->
                    msg.text = translated
                    notifyItemChanged(position)
                }
                true
            }

            // לחיצה קצרה פותחת עריכת מדיה
            holder.itemView.setOnClickListener {
                startActivity(Intent(this@MainActivity, EditorActivity::class.java))
            }
        }
        override fun getItemCount() = list.size
    }
}
