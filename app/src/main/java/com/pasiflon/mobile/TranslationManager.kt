package com.pasiflon.mobile

import com.google.mlkit.nl.translate.TranslateLanguage
import com.google.mlkit.nl.translate.Translation
import com.google.mlkit.nl.translate.TranslatorOptions

object TranslationManager {
    fun translateToHebrew(text: String, sourceLang: String = TranslateLanguage.ARABIC, callback: (String) -> Unit) {
        val options = TranslatorOptions.Builder()
            .setSourceLanguage(sourceLang)
            .setTargetLanguage(TranslateLanguage.HEBREW)
            .build()
        
        val translator = Translation.getClient(options)
        
        // הורדת המודל אם הוא לא קיים (קורה פעם אחת בלבד)
        translator.downloadModelIfNeeded()
            .addOnSuccessListener {
                translator.translate(text)
                    .addOnSuccessListener { translatedText -> callback(translatedText) }
                    .addOnFailureListener { callback("שגיאה בתרגום") }
            }
            .addOnFailureListener { callback("הורדת מודל שפה...") }
    }
}
