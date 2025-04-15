import * as path from 'path';
import * as vscode from 'vscode';
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient | undefined;

export function activate(context: vscode.ExtensionContext) {
  const serverModule = findLanguageServerPath(context);

  // If the server module is not found, show an error message
  if (!serverModule) {
    vscode.window.showErrorMessage('Cannot find AetherScript language server. Please check your settings.');
    return;
  }

  // Set up server options
  const serverOptions: ServerOptions = {
    command: 'python',
    args: [serverModule],
    transport: TransportKind.stdio,
    options: {
      env: {
        ...process.env,
        PYTHONPATH: path.join(path.dirname(serverModule), '..'),
      }
    }
  };

  // Set up client options
  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: 'file', language: 'aetherscript' }],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher('**/*.aether')
    }
  };

  // Create the language client
  client = new LanguageClient(
    'aetherscript',
    'AetherScript Language Server',
    serverOptions,
    clientOptions
  );

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('aetherscript.restart.server', () => {
      if (client) {
        client.stop();
        client.start();
        vscode.window.showInformationMessage('AetherScript Language Server restarted.');
      }
    })
  );

  // Start the client
  client.start();
}

export function deactivate(): Thenable<void> | undefined {
  if (!client) {
    return undefined;
  }
  return client.stop();
}

function findLanguageServerPath(context: vscode.ExtensionContext): string | undefined {
  // Get the server path from settings
  const config = vscode.workspace.getConfiguration('aetherscript');
  let serverPath = config.get<string>('server.path');

  // If server path is not set, use the default path
  if (!serverPath) {
    serverPath = path.join(context.extensionPath, '..', 'server', 'aetherscript', 'lsp', 'server.py');
  }

  // Check if the server path exists
  try {
    return serverPath;
  } catch (err) {
    console.error('Failed to find language server:', err);
    return undefined;
  }
}
