# 🌌 Axiom Antigravity - Powered Development Environment
{ pkgs, ... }: {
  
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_20
    pkgs.nodePackages.npm
    pkgs.git
    pkgs.curl
    pkgs.redis
  ];
  
  idx = {
    extensions = [
      "ms-python.python"
      "ms-python.vscode-pylance"
      "dbaeumer.vscode-eslint"
      "esbenp.prettier-vscode"
      "bradlc.vscode-tailwindcss"
      "github.copilot"
    ];
    
    workspace = {
      onCreate = {
        install-deps = ''
          echo "🚀 Installing dependencies..."
          pip install -r requirements.txt 2>/dev/null || true
          cd frontend && npm install 2>/dev/null || true
        '';
        
        default.openFiles = [
          "README.md"
          ".idx/airules.md"
        ];
      };
      
      onStart = {
        welcome = ''
          clear
          echo "🌌━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━🌌"
          echo ""
          echo "    ⚡ AXIOM ANTIGRAVITY - Trading Bot System ⚡"
          echo ""
          echo "    From Signals to Execution — Powered by AI"
          echo ""
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          echo ""
          echo "✅ Python 3.11 ready"
          echo "✅ Node.js 20 ready"
          echo "✅ AI Rules loaded"
          echo "✅ Extensions activated"
          echo ""
          echo "💡 Quick Start:"
          echo "   cd frontend && npm run dev    → Start frontend"
          echo "   wrangler dev                  → Start backend"
          echo "   pytest                        → Run tests"
          echo ""
          echo "🧠 Ask Gemini: 'What should we build today?'"
          echo ""
          echo "🌌━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━🌌"
        '';
      };
    };
  };
}
