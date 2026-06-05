# Gramática Formal para el Afrikáans — Parser LL(1)

Diseño, limpieza y verificación de una gramática libre de contexto (CFG) para un subconjunto del idioma **Afrikáans**, con eliminación de ambigüedad, eliminación de recursión izquierda y validación mediante un parser LL(1).

## 1. El Afrikáans y su estructura SVO

El Afrikáans es una lengua germánica derivada del neerlandés del siglo XVII, hablada principalmente en Sudáfrica y Namibia. Su estructura oracional sigue el orden **Sujeto–Verbo–Objeto (SVO)**, al igual que el español o el inglés, aunque su estructura general y amplia es conocida como SVTOMPI.

| Afrikáans | Español |
|:----------|:--------|
| `Ek eet koek` | Yo como pastel |
| `Hy koop boek` | Él compra un libro |
| `Jy drink melk` | Tú bebes leche |

La gramática modela oraciones simples con o sin objeto, y oraciones coordinadas con la conjunción `en` (y).

---

## 2. Vocabulario terminal

| Categoría | Tokens |
|:----------|:-------|
| **Pronombres** | `ek` (yo), `jy` (tú), `hy` (él) |
| **Verbos** | `eet` (come), `loop` (camina), `lees` (lee), `koop` (compra), `drink` (bebe), `slaap` (duerme) |
| **Sustantivos** | `koek` (pastel), `water` (agua), `boek` (libro), `hond` (perro), `melk` (leche) |
| **Conjunción** | `en` (y) |
| **Puntuación** | `.` |

---

## 3. Gramática Libre de Contexto (CFG)

Una CFG (Hopcroft et al., *Introduction to Automata Theory*) es una 4-tupla `G = (V, Σ, R, S)`. Para el Afrikáans, el punto de partida fue capturar la estructura básica del idioma: *"una oración es un sujeto seguido de un verbo, opcionalmente con objeto, y puede coordinarse con otras oraciones mediante `en`"*.

### Gramática inicial (borrador intuitivo)

```
Oracion ::= Oracion en Oracion    ← recursión izquierda + ambigüedad
Oracion ::= Suj V
Oracion ::= Suj V Obj
Suj     ::= Pron_Per | Sus
Obj     ::= Sus
...
```

<img width="287" height="531" alt="Captura de pantalla 2026-06-04 230751" src="https://github.com/user-attachments/assets/2ef6f233-fd13-4155-8e4e-fbbc8d7050ee" />


Esta versión es natural de escribir pero introduce **dos problemas** que hacen imposible el parsing determinista: ambigüedad estructural y recursión izquierda. Los siguientes pasos los eliminan uno a uno.

---

## 4. Ambigüedad y su eliminación

### ¿Qué la causa?

La regla `Oracion ::= Oracion en Oracion` permite dos agrupaciones distintas para la misma cadena. Tomando la oración:

> `ek eet koek en jy slaap en hy drink melk`
> *"Yo como pastel y tú duermes y él bebe leche"*

Se generan **dos árboles de derivación diferentes**:

<img width="505" height="428" alt="Captura de pantalla 2026-06-04 230301" src="https://github.com/user-attachments/assets/68ceb967-5cda-4df7-ac62-74588de116a3" />

- **Árbol A** — agrupación izquierda: `(ek eet koek en jy slaap) en hy drink melk`
- **Árbol B** — agrupación derecha: `ek eet koek en (jy slaap en hy drink melk)`

Un parser determinista no puede elegir entre ambos sin información extra. Se establece que ninguna gramática ambigua puede ser LL(k) para ningún k.

### Solución: restringir el lado derecho de `en`

Para eliminar esta ambigüedad, el lado derecho de `en` se convierte en `OracionSimple` — un no-terminal que nunca puede contener otro `en`:

```
Oracion       ::= Oracion en OracionSimple   ← solo OracionSimple a la derecha
Oracion       ::= OracionSimple
OracionSimple ::= Suj V
OracionSimple ::= Suj V Obj
```

Ahora `ek eet koek en jy slaap en hy drink melk` solo puede agruparse como `(... en ...) en ...` — un único árbol posible.

### Segunda ambigüedad: prefijo común en `OracionSimple`

```
OracionSimple ::= Suj V          ← ambas empiezan con Suj V
OracionSimple ::= Suj V Obj
```

Con lookahead en `Suj`, el parser no puede decidir cuál producción aplicar. Se resuelve al extraer el sufijo variable a un nuevo no-terminal:

```
OracionSimple ::= Suj V OracionCola
OracionCola   ::= Obj             ← hay objeto
OracionCola   ::= ϵ               ← no hay objeto
```

`OracionCola` decide con un solo token de lookahead: si es un sustantivo, expande a `Obj`; si es `en` o `.`, expande a `ϵ`.

---

<img width="368" height="629" alt="Captura de pantalla 2026-06-04 230718" src="https://github.com/user-attachments/assets/07f620fc-309c-4862-ad61-dcfb219bebe5" />


## 5. Recursión izquierda y su eliminación

### El problema

```
Oracion ::= Oracion en OracionSimple   ← recursión izquierda directa
Oracion ::= OracionSimple
```

Un parser LL(1) intenta expandir `Oracion` antes de consumir cualquier token, entrando en bucle infinito (Sipser, *Introduction to the Theory of Computation*).

### La fórmula de transformación

Dado el patrón general:

<img width="539" height="104" alt="Captura de pantalla 2026-06-04 230358" src="https://github.com/user-attachments/assets/85fccf5b-76aa-4071-adfb-4f3848492271" />

Aplicando `β = OracionSimple` y `α = en OracionSimple`:

```
Oracion  ::= OracionSimple Oracion'
Oracion' ::= en OracionSimple Oracion'
Oracion' ::= ϵ
```

La recursión desaparece. `Oracion'` captura las repeticiones de `en OracionSimple` iterativamente por la derecha.

---

## 6. De la gramática intermedia a la gramática final

Con la recursión eliminada y la ambigüedad resuelta, la gramática intermedia es:

```
Oracion       ::= OracionSimple Oracion'
Oracion'      ::= en OracionSimple Oracion'
Oracion'      ::= ϵ
OracionSimple ::= Suj V OracionCola
OracionCola   ::= Obj
OracionCola   ::= ϵ
Obj           ::= Sus
```

Se aplican tres simplificaciones sucesivas:

**Paso 1 — Eliminar `Obj` (es idéntico a `Sus`)**

```
OracionCola ::= Sus               ← Obj = Sus, se inlinea directamente
OracionCola ::= ϵ
```

**Paso 2 — "Agrupar" `OracionSimple` en `Oracion` y `Oracion'`**

```
Oracion  ::= Suj V OracionCola Oracion'
Oracion' ::= en Suj V OracionCola Oracion'
Oracion' ::= ϵ
```

**Paso 3 — Fusionar `OracionCola` y `Oracion'` en `Oracion_Fin`**

`OracionCola` seguido de `Oracion'` siempre aparecen juntos. Sus cuatro combinaciones posibles son:

| `OracionCola` | `Oracion'` | Resultado |
|:---:|:---:|:---|
| `ϵ` | `ϵ` | termina → `punk` |
| `Sus` | `ϵ` | objeto y termina → `Sus punk` |
| `Sus` | `en Suj V ...` | objeto y coordina → `Sus Conj_en Oracion` |
| `ϵ` | `en ...` | *(no ocurre: sin objeto no hay coordinación en esta gramática)* |

Esas tres combinaciones válidas se codifican como `Oracion_Fin` y `Oracion_Fin2`:

```
Oracion_Fin  ::= punk
Oracion_Fin  ::= Sus Oracion_Fin2
Oracion_Fin2 ::= punk
Oracion_Fin2 ::= Conj_en Oracion
```

Y `Suj V OracionCola Oracion'` colapsa a `Suj V Oracion_Fin`.

---

## 7. Gramática final limpia

```
Oracion       ::= Suj V Oracion_Fin

Oracion_Fin   ::= punk
Oracion_Fin   ::= Sus Oracion_Fin2

Oracion_Fin2  ::= punk
Oracion_Fin2  ::= Conj_en Oracion

Suj           ::= Pron_Per
Suj           ::= Sus

Pron_Per      ::= ek
Pron_Per      ::= jy
Pron_Per      ::= hy

V             ::= eet
V             ::= loop
V             ::= lees
V             ::= koop
V             ::= drink
V             ::= slaap

Sus           ::= koek
Sus           ::= water
Sus           ::= boek
Sus           ::= hond
Sus           ::= melk

Conj_en       ::= en
punk          ::= .
```

---

<img width="299" height="627" alt="Captura de pantalla 2026-06-04 230738" src="https://github.com/user-attachments/assets/d53151a2-73fa-4806-8efb-a6e6ae2c2399" />

## 8. Justificación LL(1)

Una gramática es **LL(1)** si y solo si, para cada no-terminal, los conjuntos `First` de sus producciones son disjuntos — y cuando una producción puede derivar `ϵ`, su conjunto `First` es disjunto con su `Follow` (Aho et al.).

La verificación se realizó con el parser de Princeton ([cs.princeton.edu/courses/archive/spring20/cos320/LL1](https://www.cs.princeton.edu/courses/archive/spring20/cos320/LL1/)):

<img width="785" height="423" alt="image" src="https://github.com/user-attachments/assets/e32fc55c-cfcf-4130-8184-3b3d1b7b7a5f" />
<img width="1757" height="249" alt="image" src="https://github.com/user-attachments/assets/f7ce7614-f499-4810-956d-d1bdbde70737" />

No hay `ϵ` en ninguna producción de la gramática final — lo que elimina completamente la necesidad de calcular conjuntos `Follow` para detectar conflictos. La gramática es **LL(1) sin conflictos**.

> **Nota sobre el proceso:** Durante el desarrollo se detectaron conflictos por el símbolo de inicio `S` del parser de Princeton, resueltos renombrando el axioma a `Oracion`. También se detectó un conflicto por recursión izquierda en la versión intermedia, resuelto con la transformación descrita en la sección 5.

---

## 9. Implementación y pruebas

El parser se implementó en Python usando `nltk.ChartParser` sobre la CFG final. El único archivo del proyecto es **[`Afrikaans.py`](./Afrikaans.py)**.

### Casos de prueba

#### Oraciones aceptadas

| # | Oración | Traducción |
|:-:|:--------|:-----------|
| 1 | `ek koop boek en jy drink melk en hy eet koek .` | Yo compro un libro y tú bebes leche y él come pastel |
| 2 | `hond eet koek en ek drink water en jy lees boek .` | El perro come pastel y yo bebo agua y tú lees un libro |
| 3 | `jy lees boek en hy koop melk en ek slaap .` | Tú lees un libro y él compra leche y yo duermo |
| 4 | `hy drink melk en koek koop water .` | Él bebe leche y el pastel compra agua |
| 5 | `ek lees boek en jy koop hond .` | Yo leo un libro y tú compras un perro |
| 6 | `jy drink water en hy slaap .` | Tú bebes agua y él duerme |
| 7 | `hond loop melk en ek drink water .` | El perro camina con leche y yo bebo agua |
| 8 | `hy koop boek .` | Él compra un libro |
| 9 | `jy slaap .` | Tú duermes |
| 10 | `ek drink water .` | Yo bebo agua |

#### Oraciones rechazadas

| # | Oración | Razón del rechazo |
|:-:|:--------|:------------------|
| 1 | `ek koop boek en jy drink melk en .` | Coordinación sin segunda oración tras `en` |
| 2 | `ek lees boek en jy en hy drink water .` | `en` sin verbo ni objeto antes de la segunda `en` |
| 3 | `jy drink melk boek en hy slaap .` | Dos objetos seguidos (`melk boek`) |
| 4 | `ek jy drink water .` | Dos sujetos seguidos |
| 5 | `koop boek en jy slaap .` | Empieza con verbo, falta sujeto |
| 6 | `hy lees boek koek .` | Dos objetos seguidos (`boek koek`) |
| 7 | `hond eet boek hond .` | Dos objetos seguidos (`boek hond`) |
| 8 | `ek drink en jy slaap .` | Objeto faltante antes de `en` |
| 9 | `boek .` | Falta verbo |
| 10 | `ek eet water en .` | `en` al final sin oración que siga |

---

## 10. Resultados

```
========================================================================
ORACIÓN                                         ESPERADO     RESULTADO
========================================================================
ek koop boek en jy drink melk en hy eet koek... ACEPTADA     OK
hond eet koek en ek drink water en jy lees b... ACEPTADA     OK
jy lees boek en hy koop melk en ek slaap .      ACEPTADA     OK
hy drink melk en koek koop water .              ACEPTADA     OK
ek lees boek en jy koop hond .                  ACEPTADA     OK
jy drink water en hy slaap .                    ACEPTADA     OK
hond loop melk en ek drink water .              ACEPTADA     OK
hy koop boek .                                  ACEPTADA     OK
jy slaap .                                      ACEPTADA     OK
ek drink water .                                ACEPTADA     OK
ek koop boek en jy drink melk en .              RECHAZADA    OK
ek lees boek en jy en hy drink water .          RECHAZADA    OK
jy drink melk boek en hy slaap .                RECHAZADA    OK
ek jy drink water .                             RECHAZADA    OK
koop boek en jy slaap .                         RECHAZADA    OK
hy lees boek koek .                             RECHAZADA    OK
hond eet boek hond .                            RECHAZADA    OK
ek drink en jy slaap .                          RECHAZADA    OK
boek .                                          RECHAZADA    OK
ek eet water en .                               RECHAZADA    OK
========================================================================
Resultado: 20 correctas, 0 fallidas de 20 pruebas
========================================================================
```

**20/20 pruebas pasadas.** La gramática acepta y rechaza exactamente las cadenas esperadas.

## Ejemplos de pruebas dentro del parcer de Princeton

<img width="1815" height="536" alt="Captura de pantalla 2026-06-04 230454" src="https://github.com/user-attachments/assets/126281d6-09a7-4ceb-bcef-da04181813d5" />
<img width="1809" height="532" alt="Captura de pantalla 2026-06-04 230532" src="https://github.com/user-attachments/assets/6eb82552-5e7f-4379-8a69-038e9250accb" />
<img width="1812" height="530" alt="Captura de pantalla 2026-06-04 230603" src="https://github.com/user-attachments/assets/6f18ef56-398e-4501-bcb2-7e5e5d10d879" />

---

## Referencias

- Aho, Lam, Sethi, Ullman — *Compilers: Principles, Techniques, and Tools* (2nd ed.)
- Sipser, M. — *Introduction to the Theory of Computation* (3rd ed.)
- Hopcroft, Motwani, Ullman — *Introduction to Automata Theory, Languages, and Computation* (3rd ed.)
- Parser LL(1) online — [cs.princeton.edu/courses/archive/spring20/cos320/LL1](https://www.cs.princeton.edu/courses/archive/spring20/cos320/LL1/)
