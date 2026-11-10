#!/bin/bash
# Durcissement SSH de PAR861454 : clés uniquement, pas de root par mot de passe.
# À lancer avec sudo APRÈS avoir copié sa clé publique. Garder la session ouverte et tester
# une nouvelle connexion par clé dans une autre fenêtre avant de fermer.
set -euo pipefail
U=${SUDO_USER:-administrateur}
AK=$(getent passwd "$U" | cut -d: -f6)/.ssh/authorized_keys

grep -q '^ssh-' "$AK" 2>/dev/null || { echo "Aucune clé dans $AK : rien changé (risque de blocage)"; exit 1; }

cat > /etc/ssh/sshd_config.d/00-durcissement.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
MaxAuthTries 3
EOF
sshd -t                      # valide la syntaxe avant de recharger
systemctl reload ssh
sshd -T | grep -E '^(passwordauthentication|kbdinteractiveauthentication|permitrootlogin|maxauthtries) '
# Retour arrière : rm /etc/ssh/sshd_config.d/00-durcissement.conf && systemctl reload ssh
