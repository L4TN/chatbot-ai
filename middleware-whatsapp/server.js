// server.js
const wppconnect = require('@wppconnect-team/wppconnect');
const express = require('express');
const { exec } = require('child_process');
const process = require('process');
const axios = require('axios');

const app = express();
const port = 3000;

// Middleware para JSON
app.use(express.json());

// Variáveis de estado
let activeClient = null;
const messageQueue = new Map();

// Mata processos do navegador
async function killBrowserProcesses() {
  return new Promise((resolve) => {
    const cmd = process.platform === 'win32' 
      ? 'taskkill /F /IM chrome.exe /IM msedge.exe /T'
      : 'pkill -f "(chrome|google-chrome|edge|msedge)"';

    exec(cmd, (error) => {
      if (error) console.log('No browsers running or error killing:', error.message);
      resolve();
    });
  });
}

// Endpoint para enviar mensagens via Python
app.post('/send-message', async (req, res) => {
  try {
    const { number, message } = req.body;
    if (!activeClient) throw new Error('WhatsApp client not connected');
    
    await activeClient.sendText(`${number}@c.us`, message);
    res.status(200).json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Inicia o servidor e o bot
async function start() {
  await killBrowserProcesses();
  
  try {
    const client = await wppconnect.create({
      session: 'mySession',
      puppeteerOptions: {
        headless: false,
        userDataDir: './tokens/session',
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-gpu',
          '--disable-dev-shm-usage'
        ]
      },
      disableWelcome: true
    });

    activeClient = client;
    console.log('Client has started!');

    client.onMessage(async (msg) => {
      try {
        // Envia mensagem para o Python
        await axios.post('http://localhost:5000/receive-message', {
          number: msg.from.replace('@c.us', ''),
          message: msg.body
        });
      } catch (error) {
        console.error('Error sending to Python:', error.message);
      }
    });

    app.listen(port, () => {
      console.log(`Node server running on port ${port}`);
    });

    process.on('SIGINT', async () => {
      console.log('\nShutting down...');
      await client.close();
      process.exit();
    });

  } catch (error) {
    console.error('Critical error:', error);
    process.exit(1);
  }
}

start();