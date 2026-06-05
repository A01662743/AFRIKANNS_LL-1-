import nltk
from nltk import CFG

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

grammar = CFG.fromstring("""
    S -> Oracion
    Oracion -> Suj V Oracion_Fin

    Oracion_Fin -> punk
    Oracion_Fin -> Sus Oracion_Fin2

    Oracion_Fin2 -> punk
    Oracion_Fin2 -> Conj_en Oracion

    Suj -> Pron_Per
    Suj -> Sus

    Pron_Per -> 'ek'
    Pron_Per -> 'jy'
    Pron_Per -> 'hy'

    V -> 'eet'
    V -> 'loop'
    V -> 'lees'
    V -> 'koop'
    V -> 'drink'
    V -> 'slaap'

    Sus -> 'koek'
    Sus -> 'water'
    Sus -> 'boek'
    Sus -> 'hond'
    Sus -> 'melk'

    Conj_en -> 'en'
    punk    -> '.'
""")

parser = nltk.ChartParser(grammar)

casos_prueba = [
    # ── ORACIONES QUE DEBEN ACEPTARSE ──────────────────────────────────────
    # Yo compro un libro y tú bebes leche y él come pastel.
    ("ek koop boek en jy drink melk en hy eet koek .",       "ACEPTADA"),
    # El perro come pastel y yo bebo agua y tú lees un libro.
    ("hond eet koek en ek drink water en jy lees boek .",    "ACEPTADA"),
    # Tú lees un libro y él compra leche y yo duermo.
    ("jy lees boek en hy koop melk en ek slaap .",           "ACEPTADA"),
    # Él bebe leche y el pastel compra agua.
    ("hy drink melk en koek koop water .",                   "ACEPTADA"),
    # Yo leo un libro y tú compras un perro.
    ("ek lees boek en jy koop hond .",                       "ACEPTADA"),
    # Tú bebes agua y él duerme.
    ("jy drink water en hy slaap .",                         "ACEPTADA"),
    # El perro camina y yo bebo un libro.
    ("hond loop melk en ek drink water .",                   "ACEPTADA"),
    # Él compra un libro.
    ("hy koop boek .",                                       "ACEPTADA"),
    # Tú duermes.
    ("jy slaap .",                                           "ACEPTADA"),
    # Yo bebo agua.
    ("ek drink water .",                                     "ACEPTADA"),

    # ── ORACIONES QUE DEBEN RECHAZARSE ─────────────────────────────────────
    # sin segunda oración tras 'en'.
    ("ek koop boek en jy drink melk en .",                   "RECHAZADA"),
    # 'en' sin verbo ni objeto antes.
    ("ek lees boek en jy en hy drink water .",               "RECHAZADA"),
    # Dos objetos seguidos (melk boek).
    ("jy drink melk boek en hy slaap .",                     "RECHAZADA"),
    # Dos sujetos seguidos (ek jy).
    ("ek jy drink water .",                                  "RECHAZADA"),
    # Empieza con verbo, falta sujeto.
    ("koop boek en jy slaap .",                              "RECHAZADA"),
    # Dos objetos seguidos (boek koek).
    ("hy lees boek koek .",                                  "RECHAZADA"),
    # Dos objetos seguidos (boek hond).
    ("hond eet boek hond .",                                 "RECHAZADA"),
    # Objeto faltante antes de 'en'.
    ("ek drink en jy slaap .",                               "RECHAZADA"),
    # Falta verbo.
    ("boek .",                                               "RECHAZADA"),
    # 'en' al final.
    ("ek eet water en .",                                    "RECHAZADA"),
]

print("=" * 72)
print(f"{'ORACIÓN':<47} {'ESPERADO':<12} {'RESULTADO'}")
print("=" * 72)

correctas = 0
fallidas  = 0

for oracion, esperado in casos_prueba:
    if oracion.strip() == "":
        resultado = "RECHAZADA"
    else:
        try:
            tokens = oracion.split()
            arboles = list(parser.parse(tokens))
            resultado = "ACEPTADA" if arboles else "RECHAZADA"
        except Exception:
            resultado = "RECHAZADA"

    estado = "OK" if resultado == esperado else "FALLO"
    if resultado == esperado:
        correctas += 1
    else:
        fallidas += 1

    corta = oracion[:44] + "..." if len(oracion) > 44 else oracion
    print(f"{corta:<47} {esperado:<12} {estado}")

print("=" * 72)
print(f"Resultado: {correctas} correctas, {fallidas} fallidas de {len(casos_prueba)} pruebas")
print("=" * 72)