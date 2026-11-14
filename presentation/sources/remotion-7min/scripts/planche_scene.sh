#!/bin/bash
# Planche de contrôle d'une scène : bash scripts/planche_scene.sh Scene-04b "30,60,..." (12 images)
set -e
FF="$(python -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())' | tr -d '\r')"
d="out/c_$1"; rm -rf "$d"
npx remotion render "$1" "$d" --frames="$2" --image-format=jpeg --muted --is-production=false 2>&1 | grep -i "error\|introuvable" || true
args=""; for f in $(ls "$d"/element-*.jpeg | sort); do args="$args -i $f"; done
"$FF" -v error -y $args -filter_complex "xstack=inputs=12:layout=0_0|w0_0|w0+w1_0|w0+w1+w2_0|0_h0|w0_h0|w0+w1_h0|w0+w1+w2_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1|w0+w1+w2_h0+h1,scale=2560:-1" -q:v 3 "$d/planche.jpg" && echo "ok $d/planche.jpg"
