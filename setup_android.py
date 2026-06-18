import os, shutil, re, sys

# ── HTML ────────────────────────────────────────────────────────────────────
html_src = os.environ.get('HTML_PATH','')
if not html_src or not os.path.exists(html_src):
    sys.exit("ERREUR : HTML_PATH non défini ou introuvable")

with open(html_src, 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

# Viewport mobile
html = re.sub(
    r'<meta[^>]*name=["\']viewport["\'][^>]*>',
    '<meta name="viewport" content="width=1024, initial-scale=0.5, '
    'minimum-scale=0.2, maximum-scale=5.0, user-scalable=yes, viewport-fit=cover">',
    html)

# CSS compact
css = (
    "<style id='android-fix'>\n"
    ".menubar{min-height:34px!important;height:34px!important;font-size:12px!important;padding:0 4px!important;}\n"
    ".menubar .logo img{height:20px!important;}\n"
    ".menubar .logo .wm{font-size:11px!important;}\n"
    ".menubar .logo .ver{font-size:10px!important;}\n"
    ".menubar .menu>button{padding:4px 8px!important;font-size:11px!important;}\n"
    ".transport{min-height:42px!important;height:42px!important;padding:2px 6px!important;gap:3px!important;}\n"
    ".transport .tbtn,.tbtn{width:32px!important;height:32px!important;font-size:13px!important;padding:0!important;}\n"
    ".transport .tempo,.bpm{font-size:17px!important;}\n"
    "#status{font-size:10px!important;padding:1px 6px!important;min-height:16px!important;line-height:16px!important;}\n"
    ".tabs{min-height:30px!important;height:30px!important;overflow-x:auto!important;-webkit-overflow-scrolling:touch!important;}\n"
    ".tab,.tabs button{padding:3px 10px!important;font-size:11px!important;white-space:nowrap!important;}\n"
    ".patternbar{min-height:28px!important;height:28px!important;padding:1px 6px!important;overflow-x:auto!important;-webkit-overflow-scrolling:touch!important;}\n"
    ".patternbar button,.pchip{font-size:11px!important;padding:2px 7px!important;height:24px!important;}\n"
    ".view{overflow:auto!important;-webkit-overflow-scrolling:touch!important;}\n"
    ".statusbar,#statBar,.stat-bar{font-size:10px!important;padding:1px 6px!important;min-height:16px!important;}\n"
    ".menu{position:relative;}\n"
    ".menu .dropdown{position:fixed!important;top:34px!important;z-index:99999!important;"
    "min-width:180px!important;max-height:80vh!important;overflow-y:auto!important;"
    "-webkit-overflow-scrolling:touch!important;}\n"
    ".menu .dropdown button,.menu .dropdown a{min-height:40px!important;padding:8px 16px!important;"
    "font-size:13px!important;display:flex!important;align-items:center!important;"
    "width:100%!important;text-align:left!important;}\n"
    "</style>"
)

# JS menus touch
js = (
    "<script id='android-menu-fix'>\n"
    "(function(){\n"
    "  function fixMenus(){\n"
    "    document.querySelectorAll('.menu').forEach(function(m){\n"
    "      var btn=m.querySelector(':scope>button');\n"
    "      if(!btn) return;\n"
    "      btn.addEventListener('touchend',function(e){\n"
    "        e.preventDefault();e.stopPropagation();\n"
    "        var wasOpen=m.classList.contains('open');\n"
    "        document.querySelectorAll('.menu.open').forEach(function(x){x.classList.remove('open');});\n"
    "        if(!wasOpen) m.classList.add('open');\n"
    "      },{passive:false});\n"
    "    });\n"
    "    document.addEventListener('touchend',function(e){\n"
    "      if(!e.target.closest('.menu'))\n"
    "        document.querySelectorAll('.menu.open').forEach(function(x){x.classList.remove('open');});\n"
    "    },{passive:true});\n"
    "    document.querySelectorAll('.menu .dropdown button,.menu .dropdown a').forEach(function(item){\n"
    "      item.addEventListener('touchend',function(e){\n"
    "        e.preventDefault();e.stopPropagation();\n"
    "        document.querySelectorAll('.menu.open').forEach(function(x){x.classList.remove('open');});\n"
    "        this.click();\n"
    "      },{passive:false});\n"
    "    });\n"
    "  }\n"
    "  if(document.readyState==='loading'){\n"
    "    document.addEventListener('DOMContentLoaded',fixMenus);\n"
    "  } else { fixMenus(); }\n"
    "})();\n"
    "</script>"
)

if '</head>' in html:
    html = html.replace('</head>', css + '\n</head>', 1)
if '</body>' in html:
    html = html.replace('</body>', js + '\n</body>', 1)

# ── Dossiers Android ─────────────────────────────────────────────────────────
for d in ['mdpi','hdpi','xhdpi','xxhdpi','xxxhdpi']:
    os.makedirs(f'android/app/src/main/res/mipmap-{d}', exist_ok=True)
for p in [
    'android/app/src/main/assets',
    'android/app/src/main/java/com/studiotibo/app',
    'android/app/src/main/res/values',
    'android/gradle/wrapper',
]:
    os.makedirs(p, exist_ok=True)

# ── Logo ──────────────────────────────────────────────────────────────────────
logo_path = os.environ.get('LOGO_PATH','')
if logo_path and os.path.exists(logo_path):
    from PIL import Image
    img = Image.open(logo_path).convert('RGBA')
    for density, size in {'mdpi':48,'hdpi':72,'xhdpi':96,'xxhdpi':144,'xxxhdpi':192}.items():
        r = img.resize((size,size), Image.LANCZOS)
        for name in ['ic_launcher.png','ic_launcher_round.png']:
            r.save(f'android/app/src/main/res/mipmap-{density}/{name}', 'PNG')
        print(f'Icone {density} {size}px OK')
else:
    print('Pas de logo - icone par defaut')

# ── Fichiers projet ───────────────────────────────────────────────────────────
with open('android/app/src/main/assets/index.html','w',encoding='utf-8') as f:
    f.write(html)
print(f"HTML : {os.path.getsize('android/app/src/main/assets/index.html')//1024} Ko")

open('android/settings.gradle','w').write('rootProject.name = "StudioTibo"\ninclude ":app"\n')

open('android/build.gradle','w').write(
    'buildscript {\n'
    '    repositories { google(); mavenCentral() }\n'
    '    dependencies { classpath "com.android.tools.build:gradle:8.2.2" }\n'
    '}\n'
    'allprojects { repositories { google(); mavenCentral() } }\n')

open('android/app/build.gradle','w').write(
    'plugins { id "com.android.application" }\n'
    'android {\n'
    '    namespace "com.studiotibo.app"\n'
    '    compileSdk 34\n'
    '    defaultConfig {\n'
    '        applicationId "com.studiotibo.app"\n'
    '        minSdk 26\n'
    '        targetSdk 34\n'
    '        versionCode 4\n'
    '        versionName "3.8.3"\n'
    '    }\n'
    '    buildTypes { debug { minifyEnabled false } }\n'
    '}\n'
    'dependencies { implementation "androidx.webkit:webkit:1.9.0" }\n')

open('android/gradle.properties','w').write(
    'org.gradle.jvmargs=-Xmx2048m\n'
    'android.useAndroidX=true\n'
    'android.enableJetifier=true\n')

open('android/app/src/main/AndroidManifest.xml','w').write(
    '<?xml version="1.0" encoding="utf-8"?>\n'
    '<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n'
    '    <uses-permission android:name="android.permission.RECORD_AUDIO"/>\n'
    '    <uses-permission android:name="android.permission.INTERNET"/>\n'
    '    <application android:label="Studio Tibo"\n'
    '        android:icon="@mipmap/ic_launcher"\n'
    '        android:roundIcon="@mipmap/ic_launcher_round"\n'
    '        android:theme="@style/AppTheme"\n'
    '        android:hardwareAccelerated="true">\n'
    '        <activity android:name=".MainActivity"\n'
    '            android:exported="true"\n'
    '            android:screenOrientation="user"\n'
    '            android:configChanges="orientation|screenSize|keyboardHidden">\n'
    '            <intent-filter>\n'
    '                <action android:name="android.intent.action.MAIN"/>\n'
    '                <category android:name="android.intent.category.LAUNCHER"/>\n'
    '            </intent-filter>\n'
    '        </activity>\n'
    '    </application>\n'
    '</manifest>\n')

open('android/app/src/main/java/com/studiotibo/app/MainActivity.java','w').write(
    'package com.studiotibo.app;\n'
    'import android.app.Activity;\n'
    'import android.os.Bundle;\n'
    'import android.view.View;\n'
    'import android.webkit.WebSettings;\n'
    'import android.webkit.WebView;\n'
    'import android.webkit.WebViewClient;\n'
    'import android.webkit.WebChromeClient;\n'
    'public class MainActivity extends Activity {\n'
    '    @Override protected void onCreate(Bundle s) {\n'
    '        super.onCreate(s);\n'
    '        WebView wv = new WebView(this);\n'
    '        setContentView(wv);\n'
    '        WebSettings ws = wv.getSettings();\n'
    '        ws.setJavaScriptEnabled(true);\n'
    '        ws.setDomStorageEnabled(true);\n'
    '        ws.setMediaPlaybackRequiresUserGesture(false);\n'
    '        ws.setUseWideViewPort(true);\n'
    '        ws.setLoadWithOverviewMode(true);\n'
    '        ws.setSupportZoom(true);\n'
    '        ws.setBuiltInZoomControls(true);\n'
    '        ws.setDisplayZoomControls(false);\n'
    '        wv.setScrollBarStyle(View.SCROLLBARS_INSIDE_OVERLAY);\n'
    '        wv.setHorizontalScrollBarEnabled(true);\n'
    '        wv.setVerticalScrollBarEnabled(true);\n'
    '        wv.setWebViewClient(new WebViewClient());\n'
    '        wv.setWebChromeClient(new WebChromeClient());\n'
    '        wv.loadUrl("file:///android_asset/index.html");\n'
    '    }\n'
    '}\n')

open('android/app/src/main/res/values/styles.xml','w').write(
    '<?xml version="1.0" encoding="utf-8"?>\n'
    '<resources>\n'
    '    <style name="AppTheme" parent="android:Theme.NoTitleBar.Fullscreen"/>\n'
    '</resources>\n')

open('android/gradle/wrapper/gradle-wrapper.properties','w').write(
    'distributionBase=GRADLE_USER_HOME\n'
    'distributionPath=wrapper/dists\n'
    'distributionUrl=https\\://services.gradle.org/distributions/gradle-8.7-bin.zip\n'
    'zipStoreBase=GRADLE_USER_HOME\n'
    'zipStorePath=wrapper/dists\n')

print("Projet Android pret !")
