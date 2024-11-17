# STK czechr

![STK Icon](https://raw.githubusercontent.com/stewe12/STK-czechr/refs/heads/main/custom_components/stk_czechr/www/STK.png)

Tento Home Assistant addon umožňuje sledování technických kontrol vozidel (STK) v České republice. K tomu používá veřejně dostupná data o vozidlech z [Data o vozidlech](https://www.dataovozidlech.cz). Umožňuje sledovat platnost STK, zbývající dny do vypršení, a další údaje o vozidlech pomocí VIN.

## Funkce

- Sledování platnosti STK a zbývajících dní do vypršení platnosti.
- Zobrazení stavu STK vozidla.
- Možnost konfigurace více vozidel.
- Podpora několika jazyků (čeština, angličtina).
- Integrace s Home Assistant pomocí platformy `sensor`.

## Instalace

1. Stáhněte si addon do vašeho Home Assistant.
2. Přejděte do **Configuration > Integrations** v Home Assistant.
3. Klikněte na **+** pro přidání nové integrace.
4. Vyhledejte **STK czechr** a klikněte na **Install**.

## Konfigurace

Po instalaci bude potřeba zadat informace o vozidle. Pro každý záznam budete potřebovat VIN číslo vozidla a pojmenování vozidla. Na základě VIN bude addon automaticky stahovat data o STK.
