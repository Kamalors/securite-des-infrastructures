# Connexion à la maquette du projet RAO (interfaces web d'EVE-NG et de Proxmox), pour les membres du groupe.
# Lancer : clic droit > « Exécuter avec PowerShell »
#      ou : powershell -ExecutionPolicy Bypass -File connexion_rao.ps1
# 1er lancement : crée ta clé SSH et la copie dans le presse-papiers ; envoie-la au responsable du serveur (Maxime).
# Une fois ta clé autorisée, relance : EVE s'ouvre dans le navigateur, Proxmox est sur https://localhost:8006.
# Fermer la fenêtre coupe l'accès. Aucun secret ici : ta clé privée ne quitte pas ton PC, et l'accès se limite
# aux deux interfaces web (chacune demande ensuite ton compte personnel).

$Hote = '163.172.105.87'
$Port = 8443
$PortPve = 8006
$Cle  = "$HOME\.ssh\id_ed25519_rao"

function Fin($msg) { Write-Host $msg; Read-Host 'Entrée pour fermer'; exit }

if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Fin 'Client OpenSSH absent : Paramètres > Système > Fonctionnalités facultatives > ajouter « Client OpenSSH ».'
}
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    Start-Process "https://localhost:$Port"
    Fin "Port $Port déjà utilisé : tunnel déjà ouvert dans une autre fenêtre ? EVE ouvert dans le navigateur."
}

New-Item -ItemType Directory -Force "$HOME\.ssh" | Out-Null
if (-not (Test-Path $Cle)) {
    Write-Host 'Création de ta clé SSH (phrase de passe conseillée, ou Entrée pour aucune)'
    ssh-keygen -t ed25519 -f $Cle -C "rao-$env:USERNAME"
}
# Clé de l'hôte épinglée (SHA256:ITO0NZL0m0eAnTKFksTLPeN5n9G1hztAxHGE15upBDY) : refuse un serveur usurpé
Set-Content -Encoding Ascii "$HOME\.ssh\known_hosts_rao" "$Hote ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEa+UjCM+SCZmbK/t5uUPcbtBymYv95cq+upONupR+64"

# Proxmox en plus, sauf si son port local est déjà pris (un autre tunnel ouvert)
$Fwd = "-L ${Port}:10.99.0.10:443"
$AvecPve = -not (Get-NetTCPConnection -LocalPort $PortPve -State Listen -ErrorAction SilentlyContinue)
if ($AvecPve) { $Fwd += " -L ${PortPve}:127.0.0.1:8006" }
# Chemins en ~ : ssh les développe lui-même, pas de souci d'espaces dans le nom d'utilisateur Windows
$p = Start-Process ssh -NoNewWindow -PassThru -ArgumentList "-N $Fwd -i ~/.ssh/id_ed25519_rao -o UserKnownHostsFile=~/.ssh/known_hosts_rao -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 camarade@$Hote"
# ssh n'ouvre le port local qu'une fois authentifié
while (-not $p.HasExited -and -not (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)) { Start-Sleep -Milliseconds 300 }

if ($p.HasExited) {
    Get-Content "$Cle.pub" | Set-Clipboard
    Write-Host "`nConnexion impossible (message ssh ci-dessus)."
    Write-Host 'Si c''est « Permission denied » : ta clé n''est pas encore autorisée. Envoie cette ligne (déjà copiée) au responsable du serveur (Maxime) :'
    Fin (Get-Content "$Cle.pub")
}
Start-Process "https://localhost:$Port"
Write-Host "Connecté (certificats auto-signés : accepter l'avertissement du navigateur) :"
Write-Host "  EVE-NG  : https://localhost:$Port, lab RAO"
if ($AvecPve) { Write-Host "  Proxmox : https://localhost:$PortPve, royaume « Proxmox VE authentication server »" }
Write-Host 'Identifiants : ton compte personnel, transmis en privé par le responsable du serveur. Fermer cette fenêtre coupe l''accès.'
$p.WaitForExit()
Fin 'Connexion coupée.'
