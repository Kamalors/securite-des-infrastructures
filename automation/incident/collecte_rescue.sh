#!/bin/bash
# Collecte de preuves depuis le MODE RESCUE Dedibox (le système compromis ne tourne pas).
# Monte le disque en LECTURE SEULE et archive les éléments utiles à l'analyse de l'incident.
# Usage : bash collecte_rescue.sh   → produit /root/preuves-PAR861454-<date>.tar.gz (+ .sha256)
set -uo pipefail
M=/mnt/sys-compromis
OUT=/root/preuves-PAR861454-$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$M" "$OUT"

mdadm --assemble --scan 2>/dev/null; cat /proc/mdstat
mount -o ro /dev/md1 "$M" || { echo "Échec du montage de /dev/md1 : vérifier lsblk"; exit 1; }

# Empreintes et fichiers de l'implant
sha256sum "$M/usr/local/lib/sshdd.so" "$M/etc/ld.so.preload" | tee "$OUT/iocs.sha256"
stat "$M/usr/local/lib/sshdd.so" "$M/etc/ld.so.preload" > "$OUT/iocs.stat" 2>&1
cat "$M/etc/ld.so.preload" > "$OUT/ld.so.preload.txt" 2>&1

# Persistance, comptes et accès (lecture seule, copie avec métadonnées)
for p in usr/local/lib etc/ld.so.preload etc/pam.d etc/ssh etc/passwd etc/shadow etc/group etc/sudoers etc/sudoers.d \
         etc/crontab etc/cron.d etc/cron.daily etc/cron.hourly var/spool/cron etc/systemd/system etc/rc.local \
         etc/profile etc/profile.d etc/bash.bashrc etc/environment root/.ssh root/.bash_history root/.profile root/.bashrc \
         etc/pve/user.cfg etc/pve/priv/token.cfg var/log/auth.log var/log/syslog var/log/journal var/log/pve; do
  [ -e "$M/$p" ] && cp -a --parents "$M/$p" "$OUT/" 2>/dev/null
done
cp -a --parents "$M"/home/*/.ssh "$M"/home/*/.bash_history "$OUT/" 2>/dev/null

# Fichiers modifiés autour de la date de l'implant (01/10/2026)
find "$M" -xdev -type f -newermt 2026-09-30 ! -newermt 2026-10-03 -printf '%TY-%Tm-%Td %TT %u %m %s %p\n' 2>/dev/null \
  | sort > "$OUT/fichiers_modifies_30sept-02oct.txt"
ls -la --time-style=full-iso "$M/root" "$M/tmp" > "$OUT/listing_root_tmp.txt" 2>&1

tar -czf "$OUT.tar.gz" -C "$(dirname "$OUT")" "$(basename "$OUT")"
sha256sum "$OUT.tar.gz" | tee "$OUT.tar.gz.sha256"
umount "$M"
echo "Archive : $OUT.tar.gz : à rapatrier puis conserver hors du serveur."
