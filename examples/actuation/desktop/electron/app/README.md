# Task Manager Electron App

Minimal Electron app used as a test target for the Nova Act integration example. Launches with Chrome DevTools Protocol enabled on port 9222.

## Repository Structure

```
├── src/
│   ├── main.ts              # Electron main process
│   └── renderer/
│       ├── index.html       # Task manager markup
│       ├── app.js           # Task manager UI logic
│       └── styles.css       # Task manager styles
├── package.json
└── tsconfig.json
```

## Prerequisites

- [Node.js](https://nodejs.org/) 24+

## Usage

```bash
npm install
npm start
```

The app opens a task manager window and exposes a CDP endpoint at `http://localhost:9222`.
