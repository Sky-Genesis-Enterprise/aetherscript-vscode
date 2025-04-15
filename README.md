# 🧠 AetherScript VS Code Extension

Welcome to the official **Visual Studio Code Extension for AetherScript**, the universal, modern programming language developed by **Sky Genesis Enterprise**.

This extension brings full support for AetherScript development to your favorite IDE, including syntax highlighting, IntelliSense, inline diagnostics, formatting, and more — all powered by the AetherScript Language Server.

---

## 🚀 Features

- 🔍 **Syntax Highlighting**
  Full grammar support for `.as` files with rich token classification.

- ✨ **Auto-Completion**
  Smart code suggestions for variables, functions, types, and modules.

- 🔧 **Code Formatting**
  Format AetherScript code automatically or on save using the official formatter.

- 🛡 **Real-time Diagnostics**
  See syntax and type errors directly in the editor as you code.

- 📚 **Hover Tooltips & Signature Help**
  Get instant documentation and function signatures inline.

- 📦 **Build and Run AetherScript Files**
  Run or compile `.as` files directly from the editor using Aether Build (if installed).

---

## 📦 Installation

You can install this extension from the **Visual Studio Code Marketplace** or via CLI:

```bash
code --install-extension skygenesisenterprise.aetherscript
```

> _Requires Node.js v18+ and VS Code v1.75+._

---

## ⚙️ Requirements

- [Node.js](https://nodejs.org/) (v18+)
- [AetherScript CLI](https://github.com/Sky-Genesis-Enterprise/aetherscript)
- [Aether Build](https://github.com/Sky-Genesis-Enterprise/aether-build) (optional for `as:build` integration)

---

## 🛠 Usage

1. Create a file with the `.as` extension.
2. Start coding in AetherScript!
3. Use `Ctrl+Shift+P` and search for:
   - `AetherScript: Build File`
   - `AetherScript: Run File`
   - `Format Document`

> You can also configure formatter and compiler settings in your workspace `settings.json`.

---

## 🧪 Development

To work on this extension locally:

```bash
git clone https://github.com/Sky-Genesis-Enterprise/aetherscript-vscode
cd aetherscript-vscode
npm install
npm run watch
```

Then open the folder in VS Code and run the `Launch Extension` task.

---

### Running and Debugging

- Press F5 to start debugging
- This will:
  - Start the Python language server
  - Launch a new VS Code window with the extension loaded
  - Connect to the language server

---

## 🤝 Contributing

We welcome contributions!
Please see the [`CONTRIBUTING.md`](./CONTRIBUTING.md) and our [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md) before submitting a pull request.

---

## 🌐 Related Projects

- [AetherScript (Language Core)](https://github.com/Sky-Genesis-Enterprise/aetherscript-vscode)
- [Aether Build](https://github.com/Sky-Genesis-Enterprise/aether-build)
- [Aether Packet Manager (APM)](https://github.com/Sky-Genesis-Enterprise/apm)

---

## ✨ About

This extension is developed and maintained by **Sky Genesis Enterprise**
Our mission is to deliver developer-first tools that are **open, elegant, and efficient**.

## 📄 License

This project is licensed under the **Apache License 2.0**.

See [`LICENSE`](./LICENSE) for more details.
