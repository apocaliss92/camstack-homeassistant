# Fix conflitto button-card (schermo nero)

L'errore `"button-card-action-handler" has already been used` è causato da **risorse duplicate** di button-card in Lovelace.

## Passi per risolvere

### 1. Controlla le risorse Lovelace

1. Vai in **Impostazioni** → **Dashboard** → **Risorse** (in basso)
2. Cerca tutte le voci che contengono `button-card`
3. Dovresti avere **una sola** risorsa button-card

### 2. Rimuovi i duplicati

Se ne trovi più di una:
- Tieni solo quella da **HACS** (es. `/hacsfiles/button-card/button-card.js`)
- Elimina eventuali risorse manuali o URL diversi che puntano a button-card

Esempi di duplicati:
```
❌ /local/button-card.js          (manuale)
❌ /hacsfiles/button-card/...     (HACS)
→ Tieni solo una
```

### 3. Controlla anche in YAML (se usi dashboard YAML)

Se la dashboard è in YAML (`ui-lovelace.yaml` o `configuration.yaml`):

```yaml
# Cerca resources: e verifica che button-card compaia una sola volta
lovelace:
  mode: yaml
  resources:
    - url: /hacsfiles/button-card/button-card.js
      type: module
    # NON avere un'altra riga per button-card
```

### 4. Svuota cache e ricarica

Dopo aver rimosso i duplicati:
- **Ctrl+Shift+R** (o Cmd+Shift+R) per hard refresh
- Oppure: Impostazioni → Sistema → Riavvia Home Assistant

### 5. Se usi browser_mod

browser_mod può caricare risorse aggiuntive. Prova temporaneamente a:
- Disabilitare browser_mod
- Ricaricare e aprire CamStack
- Se funziona, il conflitto è con browser_mod → aggiorna browser_mod o segnala il problema al maintainer
