package com.pasiflon.mobile

import android.content.Context
import android.util.Log
import org.drinkless.td.libcore.telegram.Client
import org.drinkless.td.libcore.telegram.TdApi
import java.io.File

object TelegramManager {
    private var client: Client? = null
    private var authState: TdApi.AuthorizationState? = null
    
    // ממשק כדי שה-MainActivity ידע מתי להקפיץ דיאלוגים
    interface AuthListener {
        fun onNeedPhone()
        fun onNeedCode()
        fun onLoginSuccess()
        fun onError(msg: String)
    }
    
    var listener: AuthListener? = null
    private var apiId: Int = 0
    private var apiHash: String = ""

    fun initClient(context: Context, strApiId: String, strApiHash: String) {
        if (client != null) return // כבר רץ
        
        try {
            apiId = strApiId.toInt()
        } catch (e: NumberFormatException) {
            listener?.onError("API ID חייב להיות מספר")
            return
        }
        apiHash = strApiHash

        // אתחול הלקוח של טלגרם
        client = Client.create(
            { update ->
                if (update is TdApi.UpdateAuthorizationState) {
                    authState = update.authorizationState
                    handleAuthState(context)
                }
            },
            { e -> listener?.onError("TDLib Error: ${e.localizedMessage}") },
            { e -> listener?.onError("TDLib Exception: ${e.localizedMessage}") }
        )
    }

    private fun handleAuthState(context: Context) {
        when (authState) {
            is TdApi.AuthorizationStateWaitTdlibParameters -> {
                // שליחת הגדרות ראשוניות לטלגרם
                val params = TdApi.TdlibParameters()
                params.databaseDirectory = File(context.filesDir, "tdlib").absolutePath
                params.useMessageDatabase = true
                params.useSecretChats = true
                params.apiId = apiId
                params.apiHash = apiHash
                params.systemLanguageCode = "en"
                params.deviceModel = "Pasiflon Cyber"
                params.applicationVersion = "1.0"
                params.enableStorageOptimizer = true

                client?.send(TdApi.SetTdlibParameters(params)) { }
            }
            is TdApi.AuthorizationStateWaitPhoneNumber -> {
                // טלגרם מחכה למספר - נקרא לממשק
                listener?.onNeedPhone()
            }
            is TdApi.AuthorizationStateWaitCode -> {
                // טלגרם שלח SMS ומחכה לקוד - נקרא לממשק
                listener?.onNeedCode()
            }
            is TdApi.AuthorizationStateReady -> {
                // מחובר!
                listener?.onLoginSuccess()
            }
        }
    }

    fun sendPhoneNumber(phone: String) {
        val settings = TdApi.PhoneNumberAuthenticationSettings()
        client?.send(TdApi.SetAuthenticationPhoneNumber(phone, settings)) { result ->
            if (result is TdApi.Error) {
                listener?.onError("שגיאה בשליחת מספר: ${result.message}")
            }
        }
    }

    fun sendCode(code: String) {
        client?.send(TdApi.CheckAuthenticationCode(code)) { result ->
            if (result is TdApi.Error) {
                listener?.onError("קוד שגוי: ${result.message}")
            }
        }
    }
    
    // פונקציה לשליחת הודעה (נשתמש בה אחר כך)
    fun sendMessage(chatId: Long, text: String) {
        // מימוש בהמשך
    }
}
