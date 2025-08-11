# STK czechr

![STK Icon](https://raw.githubusercontent.com/stewe12/STK-czechr/refs/heads/main/custom_components/stk_czechr/www/STK.png)

Tento Home Assistant addon umožňuje sledování technických kontrol vozidel (STK) v České republice. K tomu používá veřejně dostupná data o vozidlech z [Data o vozidlech](https://www.dataovozidlech.cz). Umožňuje sledovat platnost STK, zbývající dny do vypršení, a další údaje o vozidlech pomocí VIN.

## ⚠️ DŮLEŽITÉ - Verze 0.4.1

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
- **NOVÉ v 0.4.1**: Bezpečné zadávání API klíče v konfiguraci.

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

### Jak získat API klíč:

1. **Registrace**: [dataovozidlech.cz/registraceApi](https://dataovozidlech.cz/registraceApi)
2. **Dokumentace**: [API dokumentace](https://dataovozidlech.cz/data/RSV_Verejna_API_DK_v1_0.pdf)
3. **Podmínky**: Přečtěte si podmínky použití API

### Časté dotazy:

- **"Kde zadám API klíč?"** - Při konfiguraci integrace v Home Assistant
- **"Je API klíč bezpečný?"** - Ano, ukládá se šifrovaně v Home Assistant
- **"Můžu změnit API klíč?"** - Ano, v options flow integrace
- **"Je API zdarma?"** - Zkontrolujte podmínky na dataovozidlech.cz

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

### API:
- **URL**: https://dataovozidlech.cz/api
- **Registrace**: https://dataovozidlech.cz/registraceApi
- **Dokumentace**: https://dataovozidlech.cz/data/RSV_Verejna_API_DK_v1_0.pdf

### Rate Limiting:
- **Interval**: 24 hodin (86400 sekund)
- **Omezení**: Podle podmínek API

### Bezpečnost:
- **API klíč**: Šifrovaně uložen v Home Assistant
- **Komunikace**: HTTPS s Bearer token autentifikací
- **Rate limiting**: Respektuje API omezení

## Podpora

Pro problémy nebo dotazy:
1. Zkontrolujte logy v Home Assistant
2. Ověřte, že VIN je správně zadané
3. Zkuste restartovat Home Assistant
4. Pokud problém přetrvává, vytvořte issue na GitHub

## Verze

- **0.4.1** - Přidáno bezpečné zadávání API klíče v konfiguraci
- **0.4.0** - Přechod na oficiální API (vyžaduje registraci), web scraping odstraněn
- **0.3.2** - Opravena HTTP metoda pro web scraping (GET místo POST), vyřešena chyba 405
- **0.3.1** - Opravena ikona pro HACS a integrace, vylepšené logging pro debugging
- **0.3.0** - Přechod na bezpečný web scraping s rate limiting (maximálně jednou za den)
- **0.2.0** - Přidána podpora web scraping, více API endpointů, lepší error handling
- **0.1.0** - První verze s základní funkcionalitou
