# STK czechr

![STK Icon](https://raw.githubusercontent.com/stewe12/STK-czechr/refs/heads/main/custom_components/stk_czechr/www/STK.png)

Tento Home Assistant addon umožňuje sledování technických kontrol vozidel (STK) v České republice. K tomu používá veřejně dostupná data o vozidlech z [Data o vozidlech](https://www.dataovozidlech.cz). Umožňuje sledovat platnost STK, zbývající dny do vypršení, a další údaje o vozidlech pomocí VIN.

## Funkce

- Sledování platnosti STK a zbývajících dní do vypršení platnosti.
- Zobrazení stavu STK vozidla.
- Možnost konfigurace více vozidel.
- Podpora několika jazyků (čeština, angličtina).
- Integrace s Home Assistant pomocí platformy `sensor`.
- **NOVÉ v 0.3.1**: Opravena ikona pro HACS a integrace, vylepšené logging.

## Instalace

1. Stáhněte si addon do vašeho Home Assistant.
2. Přejděte do **Configuration > Integrations** v Home Assistant.
3. Klikněte na **+** pro přidání nové integrace.
4. Vyhledejte **STK czechr** a klikněte na **Install**.

## Konfigurace

Po instalaci bude potřeba zadat informace o vozidle. Pro každý záznam budete potřebovat VIN číslo vozidla a pojmenování vozidla. Na základě VIN bude addon automaticky stahovat data o STK.

## Bezpečný přístup (verze 0.3.1)

**Důležité**: Addon používá pouze web scraping s přísným rate limiting pro bezpečnost:

### Rate Limiting:
- **Maximálně jednou za 24 hodin** - addon si pamatuje čas posledního požadavku
- **Automatické zpoždění** - mezi požadavky jsou 2-3 sekundové pauzy
- **Respektování serveru** - používá realistické HTTP hlavičky

### Jak to funguje:

1. **První spuštění** - addon stáhne data okamžitě
2. **Následné spuštění** - kontroluje, zda uplynulo 24 hodin od posledního požadavku
3. **Rate limiting** - pokud neuplynulo 24 hodin, použije poslední data
4. **Bezpečné požadavky** - simuluje reálné prohlížeče s proper headers

### Výhody nového přístupu:

- **Bezpečný** - nehrozí ban nebo blokování
- **Respektující** - nezatěžuje server častými požadavky
- **Spolehlivý** - data jsou aktualizována jednou denně
- **Automatický** - nevyžaduje manuální zásahy

## Řešení problémů

### Addon nefunguje nebo neukazuje data:

1. **Zkontrolujte logy** - v Home Assistant jděte do Developer Tools > Logs
2. **Ověřte VIN** - ujistěte se, že VIN je správně zadaný (17 znaků)
3. **Zkuste restart** - restartujte Home Assistant
4. **Zkontrolujte internet** - addon potřebuje přístup k dataovozidlech.cz

### Časté chyby:

- `"Rate limited"` - normální chování, data se aktualizují jednou denně
- `"Web scraping failed"` - problém s přístupem k webové stránce
- `"Invalid VIN"` - špatně zadané VIN číslo

### Rate Limiting:

Pokud vidíte zprávu "Rate limited", je to normální chování:
- Addon si pamatuje čas posledního požadavku
- Nová data se stáhnou až po 24 hodinách
- Mezitím se používají poslední dostupná data

### Debugging:

Pro detailnější informace o tom, co se děje:
1. Povolte debug logging v `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.stk_czechr: debug
```

2. Restartujte Home Assistant
3. Zkontrolujte logy v Developer Tools > Logs

## Podporované senzory

### Základní (povolené ve výchozím nastavení):
- **Platnost STK** - datum vypršení technické kontroly
- **Dní do konce platnosti** - počet dní do vypršení
- **Stav STK** - validní/vypršená/varování

### Další (vypnuté ve výchozím nastavení):
- Značka, model, VIN
- Číslo TP, číslo ORV
- Barva, hmotnost, rozměry
- Výkon motoru, palivo, spotřeba
- Datum první registrace
- A mnoho dalších...

## Technické detaily

### Rate Limiting:
- **Interval**: 24 hodin (86400 sekund)
- **Zpoždění**: 2-3 sekundy mezi požadavky
- **Headers**: Realistické prohlížeče (Chrome, Firefox)

### Web Scraping:
- **URL**: https://dataovozidlech.cz/vyhledavani
- **Metoda**: POST request s VIN
- **Parsing**: HTML tabulka s daty vozidla

## Podpora

Pro problémy nebo dotazy:
1. Zkontrolujte logy v Home Assistant
2. Ověřte, že VIN je správně zadané
3. Zkuste restartovat Home Assistant
4. Pokud problém přetrvává, vytvořte issue na GitHub

## Verze

- **0.3.1** - Opravena ikona pro HACS a integrace, vylepšené logging pro debugging
- **0.3.0** - Přechod na bezpečný web scraping s rate limiting (maximálně jednou za den)
- **0.2.0** - Přidána podpora web scraping, více API endpointů, lepší error handling
- **0.1.0** - První verze s základní funkcionalitou
