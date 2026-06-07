# Black World News — Android App (Trusted Web Activity)

The Android app is a **TWA**: a thin, Google-endorsed shell that loads the live PWA at
`https://blackworldnews.world`. It **auto-updates** with the website — you never rebuild the
app to publish new stories. You only rebuild to change the app icon, name, splash, or version.

Built with **Bubblewrap** (`@bubblewrap/cli`, already installed globally).

---

## ✅ STATUS: BUILT — and how to rebuild in one click

The app **is built and signed.** `app-release-bundle.aab` (v2: **no Play Billing, no geolocation**,
version code 3) is at `D:\bwn-android\`. To make a new version later, **double-click
`D:\bwn-android\rebuild.bat`** — it bakes in every fix below and only asks for the keystore
password. Output: a fresh signed `app-release-bundle.aab` to upload to Play.

### The working local-build recipe (what `rebuild.bat` does)
Each of these was a separate wall during the first build; all are handled now:
1. **Use Node 20, not 24.** Bubblewrap bundles `inquirer` 8, whose readline crashes on Node 24.
   Portable Node 20 lives at `D:\node-v20.20.2-win-x64` and must go FIRST on PATH.
2. **`.bat` files must be CRLF line-endings, ASCII, no BOM** — or cmd silently mangles them
   (`'bubblewrap' is not recognized`). The Write tool emits LF; convert with PowerShell.
3. **Clear `NoDefaultCurrentDirectoryInExePath`** (this machine has it = 1) or cmd can't find
   `gradlew.bat` in its own folder (`'gradlew.bat' is not recognized`).
4. **Cap Gradle memory: `org.gradle.jvmargs=-Xmx512m`** in `gradle.properties` — the default
   1536m fails to reserve on this low-RAM machine. NOTE: `bubblewrap update` rewrites
   gradle.properties back to 1536m, so re-apply -Xmx512m AFTER update, before build.
5. **Put the JDK `bin` on PATH** so `jarsigner` is found — else the APK signs but the AAB doesn't
   (`'jarsigner' is not recognized`). JDK: `C:\Users\glenn\.bubblewrap\jdk\jdk-17.0.11+9`.

Keystore: `D:\bwn-android\android.keystore` (OUTSIDE this public repo). JDK 17 + Android SDK are
installed under `C:\Users\glenn\.bubblewrap` (junctioned to the D: drive).

---

## ⚠️ Why these steps are not automated

Bubblewrap is **fully interactive** (it prompts for the JDK download, keystore passwords, etc.)
and needs a real terminal — it cannot run inside the agent's non-TTY shell (readline crashes).
So **run the commands below yourself in a normal PowerShell window.** Everything that *could*
be prepared safely already has been (see "Already done").

## 🔐 Two hard rules

1. **The signing keystore NEVER goes in this repo.** `dispatch-agent` is a public GitHub repo.
   A leaked signing key is unrecoverable. Build in a *separate* folder (below).
2. **Back up the keystore + passwords** somewhere safe (password manager). With Play App Signing
   enabled, a lost *upload* key can be reset by Google — but don't rely on it; keep the backup.

---

## ✅ Already done (in this repo)

- PWA manifest verified TWA-ready (standalone, theme `#1a3a2a`, 192/512/maskable-512 icons live).
- `.well-known/assetlinks.json` created with **placeholder** fingerprints (you fill these in step 6).
- `.nojekyll` confirmed present, so GitHub Pages serves the `.well-known/` directory.
- `@bubblewrap/cli` installed globally (159 MB on C:).
- **Low-disk setup:** `~/.bubblewrap` is junctioned to `D:\bwn-android\.bubblewrap`, so the
  JDK + Android SDK download to the external T7 drive (605 GB free), not the C: SSD.

---

## ✅ RECOMMENDED: PWABuilder (cloud — no install, no Node, no SDK)

Build the same TWA on Microsoft's servers. No local toolchain, ~5 MB download — ideal for a
low-disk machine, and it sidesteps the Node-24 crash below.

1. Go to **https://www.pwabuilder.com**, enter **https://blackworldnews.world** → **Start**.
   (Manifest + icons already pass — checked.)
2. **Package For Stores → Android.**
3. Set **Package ID** `world.blackworldnews.twa`, **App name** `Black World News`; leave the rest default.
4. **Download** the zip → it contains `app-release-signed.aab` (upload to Play), the **signing key**
   (BACK IT UP — losing it means you can't update the app), and a ready-made `assetlinks.json`
   with the SHA-256 already filled in.
5. Hand over that `assetlinks.json` (or the SHA-256) to wire into this repo, then continue at
   **step 5 below** (Play Console + Digital Asset Links).

> ⚠️ **Node 24 gotcha (why local build fails here):** `@bubblewrap/cli` 1.24.1 ships
> `inquirer` 8.2.7, whose old `readline` usage crashes on **Node 24** (`readline was closed`) the
> instant it shows a prompt. So `bubblewrap init`/`build` cannot run on this machine as-is.
> PWABuilder avoids it. To build locally you'd first need Node 18/20 (nvm-windows).

## 🛠️ Alternative: build locally with Bubblewrap (needs Node 18 or 20, not 24)

### 1. Go to the build folder on the external drive (D:)
Everything heavy lives on **D:\ (T7 Shield)** to spare the C: SSD:
- `D:\bwn-android\.bubblewrap` — junctioned from `~/.bubblewrap`, so the JDK 17 + Android SDK
  (~1 GB) download here automatically. **Already set up.**
- The TWA project + Gradle cache also go here (below).

```powershell
cd D:\bwn-android
# keep Gradle's cache off C: for this build too:
$env:GRADLE_USER_HOME = "D:\bwn-android\.gradle"
```

### 2. Initialise the TWA from the live manifest
```powershell
bubblewrap init --manifest https://blackworldnews.world/manifest.json
```
- When asked **"Do you want Bubblewrap to install the JDK?"** → **Yes** (we have JDK 21, but
  Bubblewrap wants its own JDK 17 — let it). Same for the **Android SDK** → **Yes**.
- Accept the manifest-derived defaults, except confirm these:

  | Prompt | Answer |
  |---|---|
  | Application ID / package | `world.blackworldnews.twa`  ← **permanent after first publish** |
  | App name | `Black World News` |
  | Launcher name | `Black World News` (or `BWN` if it gets truncated) |
  | Display mode | `standalone` |
  | Status bar / nav / theme color | `#1a3a2a` |
  | Splash background | `#1a3a2a` |
  | Icon URL | `https://blackworldnews.world/icons/icon-512.png` |
  | Maskable icon URL | `https://blackworldnews.world/icons/icon-maskable-512.png` |
  | Include support for Play Billing? | No |
  | Request geolocation? | No |
  | **Signing key — create new?** | Yes. Choose a **strong password**, alias `android`. **Write it down.** |

  > If you want push notifications later ("new stories today"), answer **Yes** to notification
  > delegation now — it's easier than rebuilding for it.

### 3. Build the app bundle
```powershell
bubblewrap build
```
Produces:
- `app-release-bundle.aab`  ← upload this to Play
- `app-release-signed.apk`  ← for sideload testing on your own phone

### 4. (Optional) Test on your phone first
Copy the `.apk` to your Android phone and install it (enable "install unknown apps").
Until step 6 is done, the app will show a **browser address bar** at the top — that's the
Digital Asset Links check failing, and it's expected until assetlinks.json is live with the
real fingerprint.

### 5. Create the Play listing & upload
- Google Play Console developer account: **$25 one-time** → https://play.google.com/console
- Create app → category **News & Magazines**.
- **Enable Play App Signing** (default for new apps — keep it on).
- Upload the `.aab` to an **Internal testing** track first (fastest review, test with your own account).

### 6. Wire up Digital Asset Links (removes the address bar)
This is the step everyone forgets. The fingerprint that matters is **Google's**, not yours.
1. In Play Console → your app → **Setup → App integrity → App signing** → copy the
   **SHA-256 certificate fingerprint** of the *App signing key* (and also the *Upload key* one).
2. Edit [`.well-known/assetlinks.json`](.well-known/assetlinks.json) in this repo — replace:
   - `REPLACE_WITH_PLAY_APP_SIGNING_SHA256` → the **App signing key** SHA-256
   - `REPLACE_WITH_LOCAL_UPLOAD_KEY_SHA256` → the **Upload key** SHA-256
   (Format: colon-separated hex, e.g. `AA:BB:CC:...`)
3. Publish:
   ```powershell
   cd C:\Users\glenn\dispatch-agent
   git add .well-known/assetlinks.json
   git commit -m "Android: add Play signing fingerprints to assetlinks"
   git push origin main      # NOTE: push to origin/main, not the stale origin/master
   ```
4. Verify (~2 min after Pages deploys):
   ```powershell
   curl -L https://blackworldnews.world/.well-known/assetlinks.json
   ```
   Then test with Google's validator:
   https://developers.google.com/digital-asset-links/tools/generator

### 7. Promote to Production
Once internal testing looks right and the address bar is gone, promote the release to Production
in Play Console and complete the store listing (next section).

---

## 📝 Play store listing checklist (Console will block release until these are done)

- **App icon** 512×512 PNG (use `icons/icon-512.png`).
- **Feature graphic** 1024×500 PNG.
- **Phone screenshots** — at least 2 (grab from the live site on a phone, or Chrome DevTools device mode).
- **Short description** (≤80 chars) + **full description**.
- **Privacy policy URL** — **required. DONE:** live at `https://blackworldnews.world/privacy.html`.
  (Change the contact email in `build_privacy()` if `hello@blackworldnews.world` isn't right.)
- **Data safety form** — declare: no account, no personal data collected/shared; only anonymous
  Cloudflare Web Analytics. No ads.
- **Content rating questionnaire** — likely "Everyone." Answer truthfully (no violence/gambling/etc.).
- **Target audience & content** — ⚠️ **the sensitive one.** The site has a kids section. If you
  declare children in the target age range, Google applies the **Families / Designed for Families**
  policy: stricter data rules (which we already meet — no ads, no data, no chat), but it adds review
  scrutiny. Simplest path: target a **mixed/all-ages** audience and ensure the privacy policy and
  data-safety answers are airtight. Decide deliberately before submitting.

---

## 🔁 Updating the app later (rare)
Only needed for icon/name/splash/version changes — **not** for content.
```powershell
cd C:\Users\glenn\bwn-android
# bump appVersionCode in twa-manifest.json, then:
bubblewrap update
bubblewrap build
# upload the new .aab to Play
```

## TODO before submitting
- [x] Add a `/privacy` page to the site — live at /privacy.html.
- [ ] Decide target-audience age range (mixed vs includes-children) — see warning above.
- [ ] Capture phone screenshots + make the 1024×500 feature graphic.
