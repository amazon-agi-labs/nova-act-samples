import { app, BrowserWindow, session } from "electron";
import path from "path";

/**
 * Minimal Electron app for Nova Act CDP integration.
 *
 * Launch with: npm start
 * This enables --remote-debugging-port=9222 via the package.json start script,
 * exposing a CDP endpoint that Nova Act can connect to.
 */

function createWindow(): void {
  // Set CSP via response headers instead of a meta tag.
  // This is the Electron-recommended approach for production apps.
  session.defaultSession.webRequest.onHeadersReceived((_details, callback) => {
    callback({
      responseHeaders: {
        ...(_details.responseHeaders ?? {}),
        "Content-Security-Policy": [
          "default-src 'self'",
        ],
      },
    });
  });

  const win = new BrowserWindow({
    width: 1280,
    height: 900,
  });

  win.loadFile(path.join(__dirname, "renderer", "index.html"));
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  app.quit();
});
