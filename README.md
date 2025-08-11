# STK czechr

![STK Icon](https://raw.githubusercontent.com/stewe12/STK-czechr/refs/heads/main/custom_components/stk_czechr/www/STK.png)

Tento Home Assistant addon umožňuje sledování technických kontrol vozidel (STK) v České republice. K tomu používá veřejně dostupná data o vozidlech z [Data o vozidlech](https://www.dataovozidlech.cz). Umožňuje sledovat platnost STK, zbývající dny do vypršení, a další údaje o vozidlech pomocí VIN.

## ⚠️ DŮLEŽITÉ - Verze 0.4.8

**Web scraping již není podporován** kvůli změnám na dataovozidlech.cz. Addon nyní vyžaduje **oficiální API klíč**.

### Co potřebujete udělat:

1. **Zaregistrujte se pro API** na [dataovozidlech.cz/registraceApi](https://dataovozidlech.cz/registraceApi)
2. **Získejte API klíč** podle dokumentace
3. **Zadejte API klíč** při konfiguraci addonu (bezpečně uložen v Home Assistant)

### Proč se to změnilo:

- Web scraping přestal fungovat (chyba 405)
- dataovozidlech.cz má oficiální API
- API je spolehlivější a bezpečnější

## Funkce

- Sledování platnosti STK a zbývajících dní do vypršení platnosti.
- Zobrazení stavu STK vozidla.
- Možnost konfigurace více vozidel.
- Podpora několika jazyků (čeština, angličtina).
- Integrace s Home Assistant pomocí platformy `sensor`.
- **NOVÉ v 0.4.8**: Opraveno skákání hodnot mezi nedostupný a skutečnou hodnotou, vylepšené caching.

## Instalace

1. Stáhněte si addon do vašeho Home Assistant.
2. Přejděte do **Configuration > Integrations** v Home Assistant.
3. Klikněte na **+** pro přidání nové integrace.
4. Vyhledejte **STK czechr** a klikněte na **Install**.

## Konfigurace

Po instalaci budete potřebovat:

1. **Název vozidla** - libovolný název pro identifikaci
2. **VIN číslo** - 17místné identifikační číslo vozidla
3. **API klíč** - klíč získaný z dataovozidlech.cz

### Bezpečnost API klíče:

- **API klíč se ukládá bezpečně** v Home Assistant konfiguraci
- **Není viditelný** v GitHub repozitáři
- **Můžete ho změnit** v options flow integrace
- **Je šifrovaný** v Home Assistant storage

## Debug stránka

Pro testování API a diagnostiku problémů je k dispozici debug stránka:

### Jak použít:
1. **Restartujte Home Assistant** po instalaci
2. **Otevřete**: `http://vaše-ha-ip:8123/local/custom_components/stk_czechr/www/debug.html`
3. **Zadejte VIN a API klíč**
4. **Klikněte na "Testovat API"**

### Co debug stránka ukazuje:
- ✅ **HTTP status** a response headers
- ✅ **JSON data** z API
- ✅ **Raw response** pro diagnostiku
- ✅ **Chyby** a jejich detaily

## API Registrace

### Krok 1: Registrace
1. Jděte na [dataovozidlech.cz/registraceApi](https://dataovozidlech.cz/registraceApi)
2. Vyplňte registrační formulář
3. Počkejte na schválení

### Krok 2: Dokumentace
- Stáhněte si [API dokumentaci](https://dataovozidlech.cz/data/RSV_Verejna_API_DK_v1_0.pdf)
- Přečtěte si podmínky použití

### Krok 3: Použití
- Zadejte API klíč při konfiguraci addonu
- Addon automaticky použije klíč pro API volání

## Řešení problémů

### Addon ukazuje "API key required":

**Zkontrolujte konfiguraci** - API klíč musí být zadán při konfiguraci.

### "Vehicle not found" chyba:

**Zkontrolujte VIN** - ujistěte se, že VIN je správně zadané a existuje v databázi.

### Problémy s JSON parsingem:

**Použijte debug stránku** - otevřete debug stránku a zkontrolujte raw response.

### "Failed to fetch" chyba v debug stránce:

**Restartujte Home Assistant** - HTTP endpoint se registruje při startu.

### Jak získat API klíč:

1. **Registrace**: [dataovozidlech.cz/registraceApi](https://dataovozidlech.cz/registraceApi)
2. **Dokumentace**: [API dokumentace](https://dataovozidlech.cz/data/RSV_Verejna_API_DK_v1_0.pdf)
3. **Podmínky**: Přečtěte si podmínky použití API

### Časté dotazy:

- **"Kde zadám API klíč?"** - Při konfiguraci integrace v Home Assistant
- **"Je API klíč bezpečný?"** - Ano, ukládá se šifrovaně v Home Assistant
- **"Můžu změnit API klíč?"** - Ano, v options flow integrace
- **"Je API zdarma?"** - Zkontrolujte podmínky na dataovozidlech.cz
- **"Jak testovat API?"** - Použijte debug stránku

## Podporované senzory

### Základní (povolené ve výchozím nastavení):
- **Platnost STK** - datum vypršení technické kontroly
- **Dní do konce platnosti** - počet dní do vypršení
- **Stav STK** - validní/vypršená/varování
- **Značka, model, VIN** - identifikace vozidla
- **Barva, hmotnost** - fyzické vlastnosti
- **Rozměry** - délka, šířka, výška
- **Výkon, rychlost, palivo** - technické parametry

### Další (vypnuté ve výchozím nastavení):
- Číslo TP, číslo ORV
- Datum první registrace
- Spotřeba, emise
- Hluk, stav vozidla
- A mnoho dalších...

## Technické detaily

### API:
- **URL**: https://api.dataovozidlech.cz/api/vehicletechnicaldata/v2
- **Registrace**: https://dataovozidlech.cz/registraceApi
- **Dokumentace**: https://dataovozidlech.cz/data/RSV_Verejna_API_DK_v1_0.pdf

### Rate Limiting:
- **API limit**: 27 dotazů za minutu
- **Addon limit**: 1 dotaz za minutu (pro více vozidel)

### Bezpečnost:
- **API klíč**: Šifrovaně uložen v Home Assistant
- **Komunikace**: HTTPS s API_KEY header autentifikací
- **Rate limiting**: Respektuje API omezení

### Debug:
- **Debug stránka**: `/local/custom_components/stk_czechr/www/debug.html`
- **HTTP endpoint**: `/api/stk_czechr/debug`

## Podpora

Pro problémy nebo dotazy:
1. Zkontrolujte logy v Home Assistant
2. Ověřte, že VIN je správně zadané
3. **Použijte debug stránku** pro testování API
4. Zkuste restartovat Home Assistant
5. Pokud problém přetrvává, vytvořte issue na GitHub

## Verze

- **0.4.8** - Opraveno skákání hodnot mezi nedostupný a skutečnou hodnotou, vylepšené caching
- **0.4.7** - Vylepšené formátování dat, optimalizované výchozí senzory, stabilní hodnoty
- **0.4.6** - Opraveny senzory a přidány chybějící hodnoty (rozměry, hluk, stav vozidla)
- **0.4.5** - Opraveno zpracování API dat podle skutečné struktury odpovědi
- **0.4.4** - Opravena registrace HTTP endpointu pro debug stránku
- **0.4.3** - Přidána debug stránka pro testování API, optimalizovaný rate limiting (1 call/min)
- **0.4.2** - Správná implementace oficiálního API podle dokumentace
- **0.4.1** - Přidáno bezpečné zadávání API klíče v konfiguraci
- **0.4.0** - Přechod na oficiální API (vyžaduje registraci), web scraping odstraněn
- **0.3.2** - Opravena HTTP metoda pro web scraping (GET místo POST), vyřešena chyba 405
- **0.3.1** - Opravena ikona pro HACS a integrace, vylepšené logging pro debugging
- **0.3.0** - Přechod na bezpečný web scraping s rate limiting (maximálně jednou za den)
- **0.2.0** - Přidána podpora web scraping, více API endpointů, lepší error handling
- **0.1.0** - První verze s základní funkcionalitou
