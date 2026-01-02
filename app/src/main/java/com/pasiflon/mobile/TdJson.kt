package com.pasiflon.mobile

class TdJson {
    companion object {
        @JvmStatic
        external fun receive(timeout: Double): String?
        @JvmStatic
        external fun send(query: String)
        @JvmStatic
        external fun init(apiId: Int, apiHash: String, dbPath: String)
    }
    
    init {
        System.loadLibrary("tdjni")
    }
}
