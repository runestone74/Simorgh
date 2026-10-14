# Simorgh (سیمرغ): plan för santur och dastgah

Simorgh är en fork av [Felucca](https://github.com/hugelton/Felucca) (GPL-3.0) för M-VAVE FM-1, med persisk santur och persiska skalor.

## Hårdvara (kontrollerat i källkoden)
- Skärm: ST7789V, 240 × 240, RGB565 i färg (`firmware/src/lcd.c`, COLMOD 0x55).
- Typsnitt: förrastrerade bitmappar för ASCII och Latin-1 (`tools/gen_aa_font.py`). Arabisk skrift och shaping saknas, så enheten visar dastgah-namnen translittererade och persisk skrift används bara på webben och i dokumentationen.

## Gjort i den här grenen
1. **Startskärm i färg:** en Simorgh-illustration i 120 × 120 med 8 färger och dithering i 3 bpp, ritad 2× till 240 × 240, beskuren ur det godkända konstverket (simorgh_art.jpg): 5 416 B. Den genereras av `tools/gen_simorgh_art.py` till `firmware/src/simorgh_splash.h` och ritas av `draw_splash` (`ui_draw.c`), både i firmware och i emulatorn.
2. **Grafik** i `assets/simorgh/`: illustration, banner, startskärmsförhandsvisning och santur-ikon. Allt är ritat med kod, och den persiska texten är satt i Vazirmatn (OFL), men bara i bannern.
3. **FM6-presets** (egna, inga DX7-ROM-data): `SANTUR FM` (F9), `DULCIMER` (F10) och `HARPSI SNT` (F11).
   OBS: SLOT-index OWN och B1–B32 flyttas tre steg, så sparade projekt från Felucca som använder bank- eller OWN-patchar kan peka fel.
4. **PHYS-modell SANTR** (`eng_phys.c`): kör med huvudsträng + två strängar ±CRSE (upp till ~16 cent, svävning) + oktavsträng som klingar med (SYMP), mezrab-anslag (MZRB, filt..trä) och tämjd ljushet. Preset `SANTUR` (ny standard), `SANTUR OLD` (gamla SYMP-varianten) och `SANTUR STR`.
5. **Emulatorsidan:** lapis, turkos och guld, med banner och titel "Simorgh · سیمرغ".
6. **`firmware/src/dastgah.h`:** dastgah-namnen. De är inte inkopplade än.

## Nästa steg
1. **Santurröst i `eng_phys.c`:** 2–4 lätt avstämda strängar per ton (en kör), mezrab-anslag (kort hård excitation och anslagsposition) och lång avklingning.
2. **Dastgah-skalor:** en "Persian"-grupp med Shur, Segah, Chahargah, Homayoun, Mahur och Nava, plus avaz. Centtabellerna porteras från [Melodee](https://github.com/keremimo/Melodee) (GPL-3.0). Koron och sori ska vara redigerbara, och tabellerna ska granskas av en musiker.
3. **Fler presets:** till exempel Santur Shur, Mahur och Segah, med riz-tremolo och reverb.
4. **Test:** först i `web/emu`, sedan på FM-1 via webbinstalleraren. Ta backup innan. Vägen tillbaka är V15.

## Bygga
```
tools/get_toolchain.sh
git clone --depth 1 --branch AC79NN_SDK_V1.2.1_2023-12-13 https://gitee.com/Jieli-Tech/fw-AC79_AIoT_SDK.git ~/fw-AC79_AIoT_SDK
pip install Pillow fonttools      # + arabic-reshaper/raqm bara för bannern
python3 tools/gen_simorgh_art.py --font Vazirmatn-Bold.ttf
./build.sh && sh web/emu/build.sh
```

## SANTR-modellen: reglage (PHYS, MODEL = SANTR)
| Sida / ratt | Namn | Vad | MIDI CC |
|---|---|---|---|
| BODY E1 | CRSE | Körens avstämning (0 till ~16 cent, svävning) | 76 |
| BODY E2 | BRIT | Ljushet | 74 (standard) |
| BODY E3 | RING | Klangtid, visas som T60 i sekunder (2,2–16 s, uppmätt på D4) | 77 |
| BODY E4 | SYMP | Medklingande strängar (kör och oktav) | 78 |
| EXCT E5 | VELO | Velocitykänslighet: anslagsstyrka och mezrab-hårdhet (0 = fast) | 79 |
| EXCT E6 | MZRB | Mezrab: filt till trä (ljus attack) | 80 |
| EXCT E7 | DMPR | Dämpare vid tangent upp: 0 = klingar ut, 127 = dämpas direkt | 81 |
| – | Pedal | CC64 håller tangenterna, så DMPR väntar (dämparlyft) | 64 |

- **Velocity:** ett mjukt anslag ger en svagare och mörkare ton (filtkänsla), ett hårt ett starkare anslag med ljusare träklick.
- **Lagring:** värdena sparas i presets och projekt som vanliga E-parametrar.
- **MODEL-värde:** SANTR har värdet 5. Värdet 4 är reserverat eftersom gamla sparfiler tolkar PHYS MODEL 4 som DRUM.
