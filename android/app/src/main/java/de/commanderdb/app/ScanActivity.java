package de.commanderdb.app;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import android.media.AudioManager;
import android.media.Image;
import android.media.ToneGenerator;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.webkit.CookieManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.activity.ComponentActivity;
import androidx.annotation.OptIn;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ExperimentalGetImage;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.ImageProxy;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.content.ContextCompat;

import com.google.common.util.concurrent.ListenableFuture;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.Text;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Dauerscan: Kameravorschau mit Rahmen, Texterkennung (ML Kit, auf dem Gerät) laufend auf jedem
 * Kamerabild; der Kartenname wird über /api/scan_match des Servers zugeordnet.
 * Eine Karte zählt, wenn sie in zwei aufeinanderfolgenden Lesungen sicher erkannt wurde.
 * Dieselbe Karte zählt erst wieder, nachdem sie aus dem Bild war – oder per „+1“.
 * Ergebnis (Extra "result"): {"cards":[{"name":…, "qty":…}]}
 */
public class ScanActivity extends ComponentActivity {
    public static final String EXTRA_BASE = "base";
    public static final String EXTRA_LANG = "lang";
    public static final String EXTRA_RESULT = "result";
    private static final int REQ_CAMERA = 2001;
    private static final long MIN_INTERVAL_MS = 350;

    private final Map<String, Integer> cards = new LinkedHashMap<>();
    private final ExecutorService analysisExec = Executors.newSingleThreadExecutor();
    private final ExecutorService netExec = Executors.newSingleThreadExecutor();
    private final Handler ui = new Handler(Looper.getMainLooper());

    private String base;
    private String lang;
    private PreviewView preview;
    private FrameOverlay overlay;
    private TextView status;
    private TextView list;
    private Button plus;
    private TextRecognizer recognizer;
    private ToneGenerator tone;

    // Zustand des Dauerscans (nur im Analyse-Thread verändert)
    private volatile boolean busy = false;
    private long lastRun = 0;
    private String candidate = null;   // zuletzt sicher gelesene Karte
    private String lastAdded = null;   // zuletzt gezählte Karte
    private int missing = 0;           // Lesungen ohne die zuletzt gezählte Karte

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        base = getIntent().getStringExtra(EXTRA_BASE);
        lang = getIntent().getStringExtra(EXTRA_LANG);
        if (lang == null || lang.isEmpty()) lang = "eng";
        recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
        try {
            tone = new ToneGenerator(AudioManager.STREAM_NOTIFICATION, 70);
        } catch (Exception ignored) {
            tone = null;
        }
        buildUi();
        if (Build.VERSION.SDK_INT >= 23
                && checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.CAMERA}, REQ_CAMERA);
        } else {
            startCamera();
        }
    }

    private int dp(int v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, getResources().getDisplayMetrics());
    }

    private Button button(String text, boolean primary) {
        Button b = new Button(this);
        b.setText(text);
        b.setAllCaps(false);
        b.setTextColor(primary ? Color.parseColor("#1a130e") : Color.parseColor("#f1e3c6"));
        b.setBackgroundColor(primary ? Color.parseColor("#d4a24c") : Color.parseColor("#3a2c20"));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        lp.setMargins(dp(4), 0, dp(4), 0);
        b.setLayoutParams(lp);
        return b;
    }

    private void buildUi() {
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        preview = new PreviewView(this);
        preview.setScaleType(PreviewView.ScaleType.FILL_CENTER);
        root.addView(preview, new FrameLayout.LayoutParams(-1, -1));
        overlay = new FrameOverlay(this);
        root.addView(overlay, new FrameLayout.LayoutParams(-1, -1));

        status = new TextView(this);
        status.setTextColor(Color.WHITE);
        status.setTextSize(16);
        status.setBackgroundColor(Color.parseColor("#B0140f0b"));
        status.setPadding(dp(12), dp(10), dp(12), dp(10));
        status.setText("Karte so in den Rahmen legen, dass der Name im oberen Bereich liegt.");
        root.addView(status, new FrameLayout.LayoutParams(-1, -2, Gravity.TOP));

        LinearLayout bottom = new LinearLayout(this);
        bottom.setOrientation(LinearLayout.VERTICAL);
        bottom.setBackgroundColor(Color.parseColor("#D0140f0b"));
        bottom.setPadding(dp(8), dp(8), dp(8), dp(12));
        list = new TextView(this);
        list.setTextColor(Color.parseColor("#f1e3c6"));
        list.setTextSize(14);
        list.setMaxLines(4);
        list.setText("Noch keine Karte erfasst.");
        bottom.addView(list);
        LinearLayout row = new LinearLayout(this);
        row.setPadding(0, dp(8), 0, 0);
        plus = button("+1 gleiche Karte", false);
        plus.setEnabled(false);
        Button done = button("✓ Fertig", true);
        Button cancel = button("Abbrechen", false);
        row.addView(plus);
        row.addView(done);
        row.addView(cancel);
        bottom.addView(row);
        root.addView(bottom, new FrameLayout.LayoutParams(-1, -2, Gravity.BOTTOM));

        plus.setOnClickListener(v -> {
            if (lastAdded != null) add(lastAdded, false);
        });
        done.setOnClickListener(v -> finishWithResult());
        cancel.setOnClickListener(v -> {
            setResult(RESULT_CANCELED);
            finish();
        });
        setContentView(root);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQ_CAMERA) return;
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            startCamera();
        } else {
            Intent r = new Intent();
            r.putExtra(EXTRA_RESULT, "{\"error\":\"Kein Kamerazugriff erlaubt. Bitte in den Android-Einstellungen für Commander-DB freigeben.\"}");
            setResult(RESULT_OK, r);
            finish();
        }
    }

    private void startCamera() {
        ListenableFuture<ProcessCameraProvider> f = ProcessCameraProvider.getInstance(this);
        f.addListener(() -> {
            try {
                ProcessCameraProvider provider = f.get();
                Preview pv = new Preview.Builder().build();
                pv.setSurfaceProvider(preview.getSurfaceProvider());
                ImageAnalysis analysis = new ImageAnalysis.Builder()
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build();
                analysis.setAnalyzer(analysisExec, this::analyze);
                provider.unbindAll();
                provider.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA, pv, analysis);
            } catch (Exception e) {
                setStatus("Kamera konnte nicht gestartet werden: " + e.getMessage());
            }
        }, ContextCompat.getMainExecutor(this));
    }

    /** Ein Kamerabild auswerten (höchstens etwa alle 350 ms, nie zwei gleichzeitig) */
    @OptIn(markerClass = ExperimentalGetImage.class)
    private void analyze(ImageProxy proxy) {
        long now = System.currentTimeMillis();
        Image media = proxy.getImage();
        if (busy || media == null || now - lastRun < MIN_INTERVAL_MS) {
            proxy.close();
            return;
        }
        busy = true;
        lastRun = now;
        int rot = proxy.getImageInfo().getRotationDegrees();
        final int w = (rot == 90 || rot == 270) ? proxy.getHeight() : proxy.getWidth();
        final int h = (rot == 90 || rot == 270) ? proxy.getWidth() : proxy.getHeight();
        InputImage img = InputImage.fromMediaImage(media, rot);
        recognizer.process(img)
                .addOnSuccessListener(text -> {
                    List<String> lines = nameLines(text, w, h);
                    proxy.close();
                    if (lines.isEmpty()) {
                        handleMatch(null);
                        return;
                    }
                    netExec.execute(() -> handleMatch(match(lines)));
                })
                .addOnFailureListener(e -> {
                    proxy.close();
                    busy = false;
                });
    }

    /** Textzeilen im Kartenrahmen, von oben nach unten; die Namenszeile steht oben im Rahmen */
    private List<String> nameLines(Text text, int w, int h) {
        RectF fr = FrameOverlay.frameIn(w, h);
        float nameBottom = fr.top + fr.height() * 0.22f;
        List<Text.Line> top = new ArrayList<>();
        List<Text.Line> rest = new ArrayList<>();
        for (Text.TextBlock b : text.getTextBlocks()) {
            for (Text.Line l : b.getLines()) {
                Rect r = l.getBoundingBox();
                if (r == null) continue;
                float cx = r.exactCenterX(), cy = r.exactCenterY();
                float tol = fr.width() * 0.15f;
                if (cx < fr.left - tol || cx > fr.right + tol || cy < fr.top - fr.height() * 0.05f || cy > fr.bottom) continue;
                if (cy <= nameBottom) top.add(l); else rest.add(l);
            }
        }
        Collections.sort(top, (a, b) -> a.getBoundingBox().top - b.getBoundingBox().top);
        Collections.sort(rest, (a, b) -> a.getBoundingBox().top - b.getBoundingBox().top);
        List<String> out = new ArrayList<>();
        for (Text.Line l : top) out.add(l.getText());
        for (Text.Line l : rest) {
            if (out.size() >= 8) break;
            out.add(l.getText());
        }
        return out;
    }

    /** Kartenname über den Server zuordnen; liefert den Namen nur bei sicherer Erkennung */
    private String match(List<String> lines) {
        HttpURLConnection c = null;
        try {
            String body = "lines=" + URLEncoder.encode(new JSONArray(lines).toString(), "UTF-8")
                    + "&lang=" + URLEncoder.encode(lang, "UTF-8");
            c = (HttpURLConnection) new URL(base + "/api/scan_match").openConnection();
            c.setConnectTimeout(5000);
            c.setReadTimeout(10000);
            c.setRequestMethod("POST");
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
            String cookie = CookieManager.getInstance().getCookie(base);
            if (cookie != null) c.setRequestProperty("Cookie", cookie);
            try (OutputStream o = c.getOutputStream()) {
                o.write(body.getBytes(StandardCharsets.UTF_8));
            }
            if (c.getResponseCode() != 200) {
                setStatus("Server antwortet nicht (" + c.getResponseCode() + ").");
                return null;
            }
            ByteArrayOutputStream buf = new ByteArrayOutputStream();
            try (InputStream in = c.getInputStream()) {
                byte[] b = new byte[8192];
                int n;
                while ((n = in.read(b)) > 0) buf.write(b, 0, n);
            }
            JSONObject r = new JSONObject(buf.toString("UTF-8"));
            if (!r.optBoolean("sure") || r.optJSONObject("best") == null) return null;
            return r.getJSONObject("best").optString("name", null);
        } catch (Exception e) {
            setStatus("Server nicht erreichbar: " + e.getMessage());
            return null;
        } finally {
            if (c != null) c.disconnect();
        }
    }

    /** Gleiche Logik wie der Dauerscan im Browser */
    private void handleMatch(String name) {
        try {
            if (name == null) {
                candidate = null;
                if (lastAdded != null && ++missing >= 2) lastAdded = null;
                return;
            }
            if (name.equals(lastAdded)) {
                missing = 0;
                candidate = null;
                return;
            }
            if (name.equals(candidate)) {
                candidate = null;
                missing = 0;
                add(name, true);
            } else {
                candidate = name;
            }
        } finally {
            busy = false;
        }
    }

    private void add(String name, boolean auto) {
        ui.post(() -> {
            Integer q = cards.get(name);
            cards.put(name, q == null ? 1 : q + 1);
            lastAdded = name;
            plus.setEnabled(true);
            plus.setText("+1 " + shorten(name));
            int total = 0;
            StringBuilder sb = new StringBuilder();
            List<String> names = new ArrayList<>(cards.keySet());
            for (int i = names.size() - 1; i >= 0; i--) {
                String n = names.get(i);
                total += cards.get(n);
                if (sb.length() < 400) sb.append(cards.get(n)).append("× ").append(n).append('\n');
            }
            list.setText(total + " Karte(n) erfasst – zuletzt oben:\n" + sb.toString().trim());
            status.setText("✓ " + name + (auto ? "" : " (+1)") + " – nächste Karte in den Rahmen legen.");
            overlay.flash();
            feedback();
        });
    }

    private static String shorten(String s) {
        return s.length() > 18 ? s.substring(0, 17) + "…" : s;
    }

    private void feedback() {
        try {
            if (tone != null) tone.startTone(ToneGenerator.TONE_PROP_BEEP, 120);
        } catch (Exception ignored) {
        }
        try {
            Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
            if (v == null) return;
            if (Build.VERSION.SDK_INT >= 26) v.vibrate(VibrationEffect.createOneShot(60, VibrationEffect.DEFAULT_AMPLITUDE));
            else v.vibrate(60);
        } catch (Exception ignored) {
        }
    }

    private void setStatus(String s) {
        ui.post(() -> status.setText(s));
    }

    private void finishWithResult() {
        try {
            JSONArray arr = new JSONArray();
            for (Map.Entry<String, Integer> e : cards.entrySet()) {
                arr.put(new JSONObject().put("name", e.getKey()).put("qty", e.getValue()));
            }
            Intent r = new Intent();
            r.putExtra(EXTRA_RESULT, new JSONObject().put("cards", arr).toString());
            setResult(RESULT_OK, r);
        } catch (Exception e) {
            setResult(RESULT_CANCELED);
        }
        finish();
    }

    @Override
    public void onBackPressed() {
        // Zurück-Taste übernimmt das bisher Erfasste, damit nichts verloren geht
        finishWithResult();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        analysisExec.shutdown();
        netExec.shutdown();
        try {
            recognizer.close();
        } catch (Exception ignored) {
        }
        if (tone != null) tone.release();
    }

    /** Halbtransparente Abdunklung mit Kartenrahmen (Seitenverhältnis 63:88) und Namensbereich */
    static class FrameOverlay extends View {
        private final Paint dim = new Paint();
        private final Paint line = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Paint name = new Paint(Paint.ANTI_ALIAS_FLAG);
        private long flashUntil = 0;

        FrameOverlay(Context c) {
            super(c);
            dim.setColor(Color.parseColor("#88000000"));
            line.setStyle(Paint.Style.STROKE);
            line.setStrokeWidth(6f);
            name.setStyle(Paint.Style.FILL);
            name.setColor(Color.parseColor("#33d4a24c"));
        }

        /** Rahmen relativ zur Bildgröße – dieselbe Rechnung für Vorschau und Kamerabild */
        static RectF frameIn(float w, float h) {
            float fh = h * 0.72f, fw = fh * 63f / 88f;
            if (fw > w * 0.9f) {
                fw = w * 0.9f;
                fh = fw * 88f / 63f;
            }
            float l = (w - fw) / 2f, t = (h - fh) / 2f;
            return new RectF(l, t, l + fw, t + fh);
        }

        void flash() {
            flashUntil = System.currentTimeMillis() + 450;
            invalidate();
            postInvalidateDelayed(460);
        }

        @Override
        protected void onDraw(Canvas c) {
            float w = getWidth(), h = getHeight();
            RectF f = frameIn(w, h);
            c.drawRect(0, 0, w, f.top, dim);
            c.drawRect(0, f.bottom, w, h, dim);
            c.drawRect(0, f.top, f.left, f.bottom, dim);
            c.drawRect(f.right, f.top, w, f.bottom, dim);
            c.drawRect(f.left, f.top, f.right, f.top + f.height() * 0.12f, name);
            boolean fl = System.currentTimeMillis() < flashUntil;
            line.setColor(fl ? Color.parseColor("#5fd17a") : Color.parseColor("#d4a24c"));
            c.drawRoundRect(f, 18f, 18f, line);
        }
    }
}
