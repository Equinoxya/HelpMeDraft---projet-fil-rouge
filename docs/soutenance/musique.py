# -*- coding: utf-8 -*-
"""
Nappe musicale de la vidéo de démonstration.

Synthétisée, donc libre de droits et reproductible — pas de piste téléchargée
dont la licence serait à vérifier avant une diffusion.

Parti pris : rien de mélodique. Une nappe d'accords, un arpège discret et une
pulsation sourde. Une mélodie attirerait l'oreille sur elle alors que l'image
porte le propos ; ici le son ne fait que tenir le rythme des coupes.

    python3 docs/soutenance/musique.py sortie.wav [duree_en_secondes]
"""
import sys, wave
import numpy as np

SR = 44100
BPM = 100
BATTEMENT = 60.0 / BPM          # 0,6 s
MESURE = 4 * BATTEMENT          # 2,4 s
PAR_ACCORD = 2 * MESURE         # 4,8 s

# La Mineur 9 → Fa Maj 9 → Do Maj 9 → Sol Maj. Progression attendue, et c'est
# voulu : elle doit s'oublier.
ACCORDS = [
    [57, 60, 64, 67, 71],   # Am9
    [53, 57, 60, 64, 67],   # Fmaj9
    [48, 52, 55, 59, 64],   # Cmaj9
    [55, 59, 62, 67, 69],   # G
]

def hz(note):
    return 440.0 * 2 ** ((note - 69) / 12.0)

def enveloppe(n, attaque, chute, maintien, relache):
    """Enveloppe ADSR, en échantillons, sans discontinuité."""
    a, d, r = int(attaque * SR), int(chute * SR), int(relache * SR)
    a, d, r = max(1, a), max(1, d), max(1, r)
    s = max(1, n - a - d - r)
    return np.concatenate([
        np.linspace(0, 1, a),
        np.linspace(1, maintien, d),
        np.full(s, maintien),
        np.linspace(maintien, 0, r),
    ])[:n]

def nappe(f, n, detune=0.004):
    """Trois oscillateurs légèrement désaccordés : la battement donne la chaleur."""
    t = np.arange(n) / SR
    v = np.zeros(n)
    for k, d in enumerate((-detune, 0.0, detune)):
        ff = f * (1 + d)
        v += np.sin(2 * np.pi * ff * t) / (k + 1.6)
        v += 0.18 * np.sin(2 * np.pi * 2 * ff * t) / (k + 1.6)
    return v / 3.0

def pluck(f, n):
    t = np.arange(n) / SR
    corps = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return corps * np.exp(-t * 7.0)

def passe_bas(x, coupure):
    """Un pôle, appliqué deux fois : assez doux pour arrondir sans étouffer."""
    a = np.exp(-2 * np.pi * coupure / SR)
    for _ in range(2):
        y = np.empty_like(x)
        acc = 0.0
        for i, v in enumerate(x):
            acc = (1 - a) * v + a * acc
            y[i] = acc
        x = y
    return x

def composer(duree):
    n = int(duree * SR)
    piste = np.zeros(n)
    nb = int(np.ceil(duree / PAR_ACCORD))

    for i in range(nb):
        d0 = int(i * PAR_ACCORD * SR)
        notes = ACCORDS[i % len(ACCORDS)]
        long_n = int(PAR_ACCORD * SR)
        if d0 >= n:
            break
        bloc = np.zeros(long_n)

        # 1. la nappe, qui porte tout
        env = enveloppe(long_n, 0.45, 0.35, 0.78, 0.9)
        for note in notes:
            bloc += nappe(hz(note), long_n) * env * 0.085

        # 2. l'arpège, à partir de la deuxième boucle seulement : l'entrée
        #    doit être nue pour que l'arrivée de l'image se remarque.
        if i >= 4:
            pas = int(BATTEMENT / 2 * SR)
            for j in range(long_n // pas):
                deb = j * pas
                note = notes[(j * 2 + 1) % len(notes)] + 12
                m = min(pas * 3, long_n - deb)
                if m <= 0:
                    break
                bloc[deb:deb + m] += pluck(hz(note), m) * 0.05

        # 3. la pulsation sourde, sur les temps 1 et 3
        if i >= 2:
            for b in (0, 2, 4, 6):
                deb = int(b * BATTEMENT * SR)
                m = int(0.3 * SR)
                if deb + m > long_n:
                    break
                t = np.arange(m) / SR
                f = 80 * np.exp(-t * 26) + 44
                bloc[deb:deb + m] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * 0.22

        m = min(long_n, n - d0)
        piste[d0:d0 + m] += bloc[:m]

    piste = passe_bas(piste, 3200)

    # Entrée et sortie en fondu, plus une retombée sur les trois dernières
    # secondes pour que la fin de l'image ne soit pas coupée net.
    fi, fo = int(1.6 * SR), int(3.0 * SR)
    piste[:fi] *= np.linspace(0, 1, fi)
    piste[-fo:] *= np.linspace(1, 0, fo) ** 1.5

    crete = np.max(np.abs(piste))
    if crete > 0:
        piste = piste / crete * 0.62
    return np.tanh(piste * 1.15) * 0.86

if __name__ == "__main__":
    sortie = sys.argv[1] if len(sys.argv) > 1 else "musique.wav"
    duree = float(sys.argv[2]) if len(sys.argv) > 2 else 80.0
    mono = composer(duree)
    # Stéréo très légèrement élargi : la voie droite est retardée de 12 ms.
    retard = int(0.012 * SR)
    droite = np.concatenate([np.zeros(retard), mono])[:len(mono)]
    stereo = np.stack([mono, 0.5 * mono + 0.5 * droite], axis=1)
    data = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    with wave.open(sortie, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())
    print(f"{sortie} — {duree:.0f} s, {BPM} BPM")
