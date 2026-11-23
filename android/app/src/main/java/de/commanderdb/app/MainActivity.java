package de.commanderdb.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Message;
import android.provider.MediaStore;
import android.text.InputType;
import android.view.View;
import android.view.Window;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.Toast;

import androidx.core.content.FileProvider;

import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.Text;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Commander-DB für Android: zeigt die Oberfläche des eigenen Servers an (gleiche Inhalte wie im Browser).
 * Ergänzt das, was eine reine Webseite auf Android nicht kann: Dateien in „Downloads“ speichern,
 * Zwischenablage, Datei-Import, externe Links (Moxfield, Scryfall …) im Browser öffnen,
 * Kartenscanner: Foto mit der Kamera-App, Texterkennung direkt auf dem Gerät (Google ML Kit),
 * Dauerscan mit eigener Kameraansicht (ScanActivity, CameraX).
 */
public class MainActivity extends Activity {
    private static final String PREFS = "cdb";
    private static final String KEY_URL = "server_url";
    private static final int REQ_FILE = 1001;
    private static final int REQ_SCAN = 1002;
    private static final int REQ_FILE_CAMERA = 1003;
    private static final int REQ_LIVE = 1004;
    private Uri scanUri;

    private WebView web;
    private ValueCallback<Uri[]> fileCallback;
    private String serverUrl;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Window w = getWindow();
        w.setStatusBarColor(Color.parseColor("#1a130e"));
        w.setNavigationBarColor(Color.parseColor("#140f0b"));

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#140f0b"));
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setSupportMultipleWindows(true);
        s.setJavaScriptCanOpenWindowsAutomatically(true);
        s.setMediaPlaybackRequiresUserGesture(true);
        s.setAllowFileAccess(false);
        s.setUserAgentString(s.getUserAgentString() + " CommanderDB-Android/51");

        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(web, false);

        web.addJavascriptInterface(new Bridge(), "AndroidBridge");
        web.setWebViewClient(new Client());
        web.setWebChromeClient(new Chrome());

        serverUrl = getSharedPreferences(PREFS, MODE_PRIVATE).getString(KEY_URL, "");
        if (serverUrl.isEmpty()) {
            askServer(false);
        } else if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(serverUrl);
        }
    }

    /** Fragt die Adresse des Servers ab, z. B. https://commander.example.de */
    private void askServer(boolean cancelable) {
        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        input.setHint("https://commander.deine-domain.de");
        input.setText(serverUrl.isEmpty() ? "https://" : serverUrl);
        input.setSelection(input.getText().length());
        AlertDialog.Builder b = new AlertDialog.Builder(this)
                .setTitle("Server-Adresse")
                .setMessage("Adresse deiner Commander-Datenbank eingeben (wie im Browser).")
                .setView(input)
                .setCancelable(cancelable)
                .setPositiveButton("Verbinden", (d, which) -> {
                    String u = input.getText().toString().trim();
                    if (!u.startsWith("http://") && !u.startsWith("https://")) u = "https://" + u;
                    while (u.endsWith("/")) u = u.substring(0, u.length() - 1);
                    if (u.length() < 12) {
                        Toast.makeText(this, "Bitte eine gültige Adresse eingeben.", Toast.LENGTH_LONG).show();
                        askServer(cancelable);
                        return;
                    }
                    serverUrl = u;
                    getSharedPreferences(PREFS, MODE_PRIVATE).edit().putString(KEY_URL, u).apply();
                    web.loadUrl(u);
                });
        if (cancelable) b.setNegativeButton("Abbrechen", null);
        b.show();
    }

    private boolean isOwnServer(Uri uri) {
        if (serverUrl.isEmpty() || uri == null || uri.getHost() == null) return false;
        Uri srv = Uri.parse(serverUrl);
        return uri.getHost().equalsIgnoreCase(srv.getHost()) && uri.getPort() == srv.getPort();
    }

    private void openExternal(Uri uri) {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
        } catch (Exception e) {
            Toast.makeText(this, "Keine App zum Öffnen gefunden.", Toast.LENGTH_SHORT).show();
        }
    }

    private class Client extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            if (isOwnServer(uri)) return false;   // eigene Seiten in der App
            openExternal(uri);                    // Scryfall, Moxfield, Wizards … im Browser
            return true;
        }

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            if (!request.isForMainFrame()) return;
            new AlertDialog.Builder(MainActivity.this)
                    .setTitle("Keine Verbindung")
                    .setMessage("Der Server " + serverUrl + " ist nicht erreichbar.\n(" + error.getDescription() + ")")
                    .setPositiveButton("Erneut versuchen", (d, w) -> web.loadUrl(serverUrl))
                    .setNeutralButton("Server ändern", (d, w) -> askServer(true))
                    .setCancelable(false)
                    .show();
        }

        @Override
        public void onPageFinished(WebView view, String url) {
            CookieManager.getInstance().flush();
        }
    }

    private class Chrome extends WebChromeClient {
        /** window.open(...) – z. B. „→ Moxfield“: Ziel im externen Browser öffnen */
        @Override
        public boolean onCreateWindow(WebView view, boolean isDialog, boolean isUserGesture, Message resultMsg) {
            WebView temp = new WebView(MainActivity.this);
            temp.setWebViewClient(new WebViewClient() {
                @Override
                public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest request) {
                    Uri uri = request.getUrl();
                    if (isOwnServer(uri)) web.loadUrl(uri.toString()); else openExternal(uri);
                    v.destroy();
                    return true;
                }
            });
            WebView.WebViewTransport transport = (WebView.WebViewTransport) resultMsg.obj;
            transport.setWebView(temp);
            resultMsg.sendToTarget();
            return true;
        }

        /** <input type=file> beim Deck-Import; mit capture (Kartenscanner im Browser-Modus) direkt die Kamera */
        @Override
        public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
            if (fileCallback != null) fileCallback.onReceiveValue(null);
            fileCallback = callback;
            if (params != null && params.isCaptureEnabled()) {
                try {
                    startActivityForResult(cameraIntent(), REQ_FILE_CAMERA);
                    return true;
                } catch (Exception e) {
                    // keine Kamera-App: normale Dateiauswahl
                }
            }
            Intent i = new Intent(Intent.ACTION_GET_CONTENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("*/*");
            try {
                startActivityForResult(Intent.createChooser(i, "Deckliste wählen"), REQ_FILE);
            } catch (Exception e) {
                fileCallback = null;
                return false;
            }
            return true;
        }
    }

    /** Kamera-App mit Ausgabedatei im App-Cache (über FileProvider freigegeben) */
    private Intent cameraIntent() throws Exception {
        File dir = new File(getCacheDir(), "scan");
        if (!dir.exists() && !dir.mkdirs()) throw new Exception("Cache nicht beschreibbar");
        File f = new File(dir, "karte.jpg");
        scanUri = FileProvider.getUriForFile(this, getPackageName() + ".scanfiles", f);
        Intent i = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        i.putExtra(MediaStore.EXTRA_OUTPUT, scanUri);
        i.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
        return i;
    }

    /** Ergebnis an die Webseite melden: window.onNativeScan({lines:[{text, top, height}], width, height} oder {error}) */
    private void sendScan(JSONObject result) {
        String js = "window.onNativeScan && window.onNativeScan(" + JSONObject.quote(result.toString()) + ")";
        runOnUiThread(() -> web.evaluateJavascript(js, null));
    }

    private void scanError(String msg) {
        try {
            sendScan(new JSONObject().put("error", msg));
        } catch (Exception ignored) {
        }
    }

    /** Foto mit ML Kit auswerten (läuft vollständig auf dem Gerät) */
    private void recognize(Uri uri) {
        try {
            InputImage img = InputImage.fromFilePath(this, uri);
            TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS).process(img)
                    .addOnSuccessListener(text -> {
                        try {
                            JSONArray lines = new JSONArray();
                            for (Text.TextBlock b : text.getTextBlocks()) {
                                for (Text.Line l : b.getLines()) {
                                    JSONObject o = new JSONObject().put("text", l.getText());
                                    if (l.getBoundingBox() != null) {
                                        o.put("top", l.getBoundingBox().top).put("height", l.getBoundingBox().height());
                                    } else {
                                        o.put("top", 0).put("height", 0);
                                    }
                                    lines.put(o);
                                }
                            }
                            sendScan(new JSONObject().put("lines", lines).put("width", img.getWidth()).put("height", img.getHeight()));
                        } catch (Exception e) {
                            scanError("Auswertung fehlgeschlagen: " + e.getMessage());
                        }
                    })
                    .addOnFailureListener(e -> scanError("Texterkennung fehlgeschlagen: " + e.getMessage()));
        } catch (Exception e) {
            scanError("Foto nicht lesbar: " + e.getMessage());
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == REQ_SCAN) {
            if (resultCode == RESULT_OK && scanUri != null) recognize(scanUri);
            else scanError("Kein Foto aufgenommen.");
            return;
        }
        if (requestCode == REQ_LIVE) {
            String r = data != null ? data.getStringExtra(ScanActivity.EXTRA_RESULT) : null;
            if (r == null) r = "{\"cards\":[]}";
            String js = "window.onNativeScanList && window.onNativeScanList(" + JSONObject.quote(r) + ")";
            web.evaluateJavascript(js, null);
            return;
        }
        if (requestCode == REQ_FILE_CAMERA && fileCallback != null) {
            fileCallback.onReceiveValue(resultCode == RESULT_OK && scanUri != null ? new Uri[]{scanUri} : null);
            fileCallback = null;
            return;
        }
        if (requestCode == REQ_FILE && fileCallback != null) {
            Uri[] result = null;
            if (resultCode == RESULT_OK && data != null && data.getData() != null) result = new Uri[]{data.getData()};
            fileCallback.onReceiveValue(result);
            fileCallback = null;
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    /** Wird von der Webseite aufgerufen (window.AndroidBridge.…) */
    private class Bridge {
        @JavascriptInterface
        public void saveFile(String name, String text) {
            final String safe = name.replaceAll("[\\\\/:*?\"<>|]", "_");
            runOnUiThread(() -> {
                try {
                    String where = writeDownload(safe, text);
                    Toast.makeText(MainActivity.this, "Gespeichert: " + where, Toast.LENGTH_LONG).show();
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this, "Speichern fehlgeschlagen: " + e.getMessage(), Toast.LENGTH_LONG).show();
                }
            });
        }

        @JavascriptInterface
        public void copyText(String text) {
            runOnUiThread(() -> {
                ClipboardManager cb = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                cb.setPrimaryClip(ClipData.newPlainText("Deckliste", text));
                Toast.makeText(MainActivity.this, "In die Zwischenablage kopiert", Toast.LENGTH_SHORT).show();
            });
        }

        @JavascriptInterface
        public void changeServer() {
            runOnUiThread(() -> askServer(true));
        }

        /** Die Webseite fragt, ob der eingebaute Scanner verfügbar ist */
        @JavascriptInterface
        public boolean hasScanner() {
            return getPackageManager().hasSystemFeature(android.content.pm.PackageManager.FEATURE_CAMERA_ANY);
        }

        /** Kartenscanner: Kamera-App öffnen, danach Texterkennung; Ergebnis kommt über window.onNativeScan */
        @JavascriptInterface
        public void scanCard() {
            runOnUiThread(() -> {
                try {
                    startActivityForResult(cameraIntent(), REQ_SCAN);
                } catch (Exception e) {
                    scanError("Kamera konnte nicht geöffnet werden: " + e.getMessage());
                }
            });
        }

        /** Dauerscan mit eigener Kameraansicht verfügbar? (benötigt eine Kamera auf der Rückseite) */
        @JavascriptInterface
        public boolean hasLiveScanner() {
            return getPackageManager().hasSystemFeature(android.content.pm.PackageManager.FEATURE_CAMERA_ANY);
        }

        /** Dauerscan öffnen; erfasste Karten kommen beim Schließen über window.onNativeScanList({cards:[{name, qty}]}) */
        @JavascriptInterface
        public void scanLive(String lang) {
            runOnUiThread(() -> {
                try {
                    Uri u = Uri.parse(web.getUrl() != null ? web.getUrl() : serverUrl);
                    String base = u.getScheme() + "://" + u.getEncodedAuthority();
                    Intent i = new Intent(MainActivity.this, ScanActivity.class);
                    i.putExtra(ScanActivity.EXTRA_BASE, base);
                    i.putExtra(ScanActivity.EXTRA_LANG, lang);
                    CookieManager.getInstance().flush();
                    startActivityForResult(i, REQ_LIVE);
                } catch (Exception e) {
                    String js = "window.onNativeScanList && window.onNativeScanList(" + JSONObject.quote("{\"error\":\"Dauerscan nicht startbar\"}") + ")";
                    web.evaluateJavascript(js, null);
                }
            });
        }

        @JavascriptInterface
        public String appVersion() {
            return "51";
        }
    }

    private String writeDownload(String name, String text) throws Exception {
        byte[] data = text.getBytes(StandardCharsets.UTF_8);
        if (Build.VERSION.SDK_INT >= 29) {
            ContentValues v = new ContentValues();
            v.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            v.put(MediaStore.MediaColumns.MIME_TYPE, name.endsWith(".csv") ? "text/csv" : "text/plain");
            v.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/Commander-DB");
            Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
            if (uri == null) throw new Exception("kein Zugriff auf Downloads");
            try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                out.write(data);
            }
            return "Downloads/Commander-DB/" + name;
        }
        File dir = new File(getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), "Commander-DB");
        if (!dir.exists() && !dir.mkdirs()) throw new Exception("Ordner nicht anlegbar");
        File f = new File(dir, name);
        try (FileOutputStream out = new FileOutputStream(f)) {
            out.write(data);
        }
        return f.getAbsolutePath();
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack(); else super.onBackPressed();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }

    @Override
    protected void onPause() {
        super.onPause();
        CookieManager.getInstance().flush();
    }
}
