# 🐍 B7 GAMES • Cobrinha 2.5D Interativa (TikTok Live Edition)

Sistema interativo completo em **Python + Localhost** para transmissão ao vivo no TikTok pelo OBS Studio com conexão via **EulerStream API**.

---

## 🌟 O que foi integrado nesta versão profissional:

1. **Jogo Original 2.5D 100% Preservado:**
   - O tabuleiro isométrico flutuante 16x16, a cobrinha orgânica com curvas perfeitas, olhos dinâmicos 3D que seguem a direção, língua bífida animada, boca que abre para abocanhar a maçã e o piloto automático inteligente (BFS + evasão de bombas) permanecem exatamente iguais ao original.

2. **Efeitos Sonoros Integrados (Web Audio de Alta Fidelidade):**
   - **🍎 Som da Maçã:** Efeito realista e crocante de mordida e mastigação (*crunch orgânico* com ressonância de polpa fresca).
   - **💣 Som da Bomba:** Detonação profunda com impacto de sub-bass (*boom* estrondoso, ruído de estilhaços e rumble).
   - Síntese nativa procedural: **zero arquivos externos, zero delay e compatível 100% com o Navegador do OBS Studio**.

4. **Tela do Jogo 100% Limpa e Sem Joystick (Otimizada para o OBS):**
   - Os botões flutuantes de presentes ("Toque no presente"), o botão "Auto IA", o editor de fotos e o joystick virtual foram completamente removidos da área de jogo.
   - A arena isométrica agora fica 100% desobstruída e cinematográfica em formato 9:16.
   - **Toda a gestão fica centralizada no Painel B7 Games:** ligar/desligar IA, disparar presentes com 1 clique e abrir o Editor de Fotos/Quantidades.

3. **Painel B7 GAMES na Cor Azul (Integrado no Localhost):**
   - Identidade visual oficial B7 GAMES em **Azul Cyberstream** (`#070c18`, `#0b1329`, `#1e3a8a`, `#2563eb`, `#38bdf8`).
   - **🤖 Botão Modo IA:** Indicador chamativo com status em tempo real (LIGADO / DESLIGADO) para ligar ou desligar o piloto automático da cobrinha com 1 clique.
   - **🎁 Grade de Botões de Presente:** Botões clicáveis com todos os presentes cadastrados (Rosa, Buquê, Caixa, Donut, Luvas). Ao clicar em qualquer botão, a ação (maçãs ou bombas) dispara imediatamente na cobrinha ao vivo!
   - **🔊 Controles de Áudio:** Sliders de volume, toggles independentes e botões *"🍎 Testar Som Maçã"* e *"💣 Testar Som Bomba"*.
   - **⚙️ Editor de Presentes:** Altere fotos, nomes, quantidades e alterne entre 🍎 Maçã e 💣 Bomba com salvamento persistente.
   - **💬 Feed em Tempo Real:** Registro visual dos presentes, doadores e comentários recebidos.

4. **Servidor Python com Suporte à API EulerStream:**
   - Conexão em tempo real com a live do TikTok através da API EulerStream (`wss://ws.eulerstream.com` ou biblioteca `TikTokLive`).
   - Sincronização automática via Server-Sent Events (SSE).
   - Rota limpa dedicada para o OBS Studio: `http://localhost:8765/game`.

---

## 🚀 Como Iniciar no Windows:

### 1. Instalar as Dependências (Apenas na 1ª vez):
- Dê um duplo clique no arquivo **`INSTALAR.bat`**.
- Ele irá verificar o Python e instalar as bibliotecas necessárias para conectar ao TikTok e à EulerStream API.

### 2. Iniciar o Jogo e o Painel B7:
- Dê um duplo clique no arquivo **`INICIAR.bat`**.
- O servidor Python iniciará e abrirá automaticamente o navegador em:
  - **Painel B7 + Jogo:** [http://127.0.0.1:8765](http://127.0.0.1:8765)
  - **Modo Limpo para OBS:** [http://127.0.0.1:8765/game](http://127.0.0.1:8765/game)

---

## 📡 Como Conectar com o TikTok Live (EulerStream API):

1. Abra o painel no navegador ([http://127.0.0.1:8765](http://127.0.0.1:8765)).
2. No card **"Conexão TikTok Live (API EulerStream)"**:
   - Digite o seu **@ do TikTok** (ex: `@seunome`).
   - Cole a sua **EulerStream API Key** (se possuir assinatura na eulerstream.com).
   - Clique em **"⚡ Conectar Live"**.
3. O status mudará para 🟢 **AO VIVO**, e todos os presentes enviados pelos espectadores na live farão a cobrinha comer maçãs ou sofrer penalidades com bombas automaticamente!

> **Dica:** Mesmo se você não estiver ao vivo no momento, você pode testar todas as mecânicas usando os **Botões Rápidos de Presente** no painel!

---

## 🎬 Como Configurar no OBS Studio (Transmissão 9:16):

1. No OBS Studio, vá em **Fontes** e clique em **+** -> **Navegador (Browser Source)**.
2. Nomeie como `B7 Cobrinha 2.5D`.
3. Preencha os campos:
   - **URL:** `http://localhost:8765/game`
   - **Largura:** `540` (ou `1080` se sua live for Full HD vertical)
   - **Altura:** `960` (ou `1920`)
   - Marque a caixinha: **"Controlar áudio via OBS"** (para o som da maçã e da bomba sair com perfeição na sua transmissão).
4. Clique em **OK**. A cobrinha 2.5D aparecerá em tela cheia vertical, limpa e pronta para o público interagir!
