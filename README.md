[![Generate Firmware Decryption JSON File](https://github.com/Mai19930513/SamsungTestFirmwareVersionDecrypt/actions/workflows/python-app.yml/badge.svg)](https://github.com/Mai19930513/SamsungTestFirmwareVersionDecrypt/actions/workflows/python-app.yml)

# Samsung Test Firmware Version Decryption

## 🌐 Live Demo
Visit the [GitHub Pages site](https://eduardoa3677.github.io/SamsungTestFirmwareVersionDecrypt/) to query Samsung test firmware versions.

## Main Features
Decrypts Samsung test firmware version numbers by generating serial numbers, calculating their MD5 hashes, and comparing with the official website.

Samsung test firmware website: `https://fota-cloud-dn.ospserver.net/firmware/[RegionCode]/[DeviceModel]/version.test.xml`

Example: [China S24 Ultra](https://fota-cloud-dn.ospserver.net/firmware/CHC/SM-S9280/version.test.xml)

## Quick Start

### How to Add Your Own Device
1. `Fork` this project or `git clone` the code locally
2. Modify `models.txt`, add entries in the format: `DeviceName,DeviceModel,RegionCode` (multiple regions separated by `|`)
3. Change `getModelDictsFromDB` to `getModelDicts` at the bottom of the `samsung_test_firmware_decrypt.py` file
4. Re-run the script

### View Results
- [View Test Firmware Changelog](https://github.com/Mai19930513/SamsungTestFirmwareVersionDecrypt/blob/master/test_firmware_changelog.txt)
- [View Decoded Firmware Versions](https://github.com/Mai19930513/SamsungTestFirmwareVersionDecrypt/blob/master/firmware.json)

> **Note:** The recorded firmware version numbers may not be complete, limited by the added device models and regions, as well as the script's MD5 decryption percentage.

---

## 📖 Documentación Detallada (Español)

# ¿Cómo Obtener Información de los Números de Versión del Firmware de Samsung?
Tomando como ejemplo el modelo S24 Ultra "S9280ZCU4BXKV/S9280CHC4BXKV/S9280ZCU4BXKV",
primero divide el número de versión en 3 partes usando "/" como separador, representando `número de versión interna`, `número de versión CSC`, `número de versión de banda base` (la versión wifi no tiene número de versión de banda base)
## Tomando como ejemplo el número de versión interna "S9280ZCU4BXKV":
1. Primera parte: Los primeros 4 caracteres (`S928`) representan el modelo del teléfono:
    - `S`: El primer carácter representa la serie, como "S" representa la serie S. Además, están las series que comienzan con F (dispositivos plegables), A (serie A), E, y anteriormente N (serie Note), etc. (Nota: la serie S21 y anteriores usaban G al inicio, a partir de la serie S22 cambiaron a "S");
    - `9`: El segundo carácter "9" representa la serie de gama alta. Cuanto menor es el número, más baja es la gama. Por ejemplo, la versión S23 FE es S711;
    - `2`: El tercer carácter representa la generación de la serie (comenzando desde **0**). S24 Ultra (S928) es 2, S23 Ultra (S918) es 1, S25 Ultra (S938) es 3;
    - `8`: El cuarto carácter representa diferentes modelos de la misma serie y el estándar de red soportado. Por ejemplo, S24 Ultra es "S928", S24+ es "S926", S24 es "S921". Cuanto mayor es el número, mayor es el tamaño del dispositivo y mejores las especificaciones. Para soporte 4G/LTE o 5G, usualmente el cuarto dígito "0" o "5" representa solo soporte 4G, "1", "6" o "8" representan soporte 5G. Así que "S928" representa un dispositivo de tercera generación de la serie S con soporte 5G
2. Segunda parte: Los caracteres 5 a 7 (`0ZC`) o caracteres 5 a 8 (especiales como: versión desbloqueada de EE.UU. u otras variantes de código) representan información relacionada con la región objetivo:
   - `0`: El primer `0` representa China continental y Hong Kong, `U` representa EE.UU. (`U1` representa versión desbloqueada), `W` representa Canadá, `N` representa Corea, `B` representa otras regiones del mundo (a veces Samsung usa `E` en lugar de `B` para ciertos dispositivos, para versiones 4G/LTE, usan `F` en lugar de `B` o `E`). Algunos modelos tienen uso limitado de `G, M, B2, FG, S, V, VL y otras variantes`.
   - `ZC`: El segundo y tercer carácter también están relacionados con la región. Los modelos bloqueados por operador de EE.UU. son `SG`, y los modelos desbloqueados son `UE`; Canadá es `VL`, China continental es `ZC`, Hong Kong es `ZH`, otras regiones del mundo son `XX`; Samsung no usa tantas variantes para estos dos caracteres como para el primer identificador de región
> Normalmente, los primeros 7 caracteres de la versión del firmware (8 caracteres para dispositivos desbloqueados de EE.UU. y otras variantes) no cambiarán después de la fabricación con las actualizaciones. Si los primeros 7/8 caracteres del nuevo número de versión del firmware no coinciden con el número de versión interna actual, no debes actualizar este firmware. Estos caracteres definen el modelo del dispositivo y la región objetivo de la actualización del firmware. Aunque existen métodos para instalar actualizaciones de diferentes regiones, esto no es una práctica segura y debe evitarse.

3. Tercera parte: Los caracteres 8 a 10 `U4B` o caracteres 9 a 11 (especiales como versión desbloqueada de EE.UU. u otras variantes de código) representan el contenido de la actualización:
   - `U`: Representa el contenido de la actualización, usualmente `U` o `S` estos dos caracteres. `U` indica nuevas funciones o actualizaciones de funciones principales, `S` indica actualización de parche de seguridad, solo las últimas correcciones de seguridad de Samsung y Google se representan con `S`.
   - `4`: Representa el número de bootloader. Este carácter limita la versión a la que puedes degradar, por lo que no puedes degradar a firmware con un número inferior a este. Por ejemplo, no puedes degradar de firmware con bootloader número `4` a `3`. Este carácter se incrementa en el orden `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ`.
   - `A`: Representa la versión principal de actualización, incluidas las actualizaciones del SO. Comienza con `A` y se incrementa en el orden `ABCDEFGHIJKLMNOPQRSTUVWXYZ`. Por ejemplo, el S24 Ultra actual es Android 14, la próxima versión será Android 15, este carácter cambiará a `B`, y así sucesivamente.

4. Cuarta parte: Los últimos tres caracteres `XKV` representan la fecha de compilación del firmware:
   - `X`: Representa el año en la fecha de compilación del firmware. Comienza con `A` representando el año `2021`, `B` representa `2022`, y así sucesivamente, `X` representa `2024`. (La pregunta es: después de usar `Z` para 2026, ¿qué letra se usará para `2027`? ¿Volverá a comenzar desde `A`? 😆)
   - `K`: Representa el mes en la fecha de compilación del firmware. Comienza con `A` representando `enero`, `B` representa `febrero`, y así sucesivamente, `K` representa `noviembre`. Los valores son `ABCDEFGHIJKL`
   - `v`: Representa el identificador interno de la compilación del firmware, considerémoslo como el identificador para cada firmware de prueba interno. Samsung tiene múltiples firmwares de prueba cada mes, `123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ`. Samsung puede usar hasta `Z`, es impresionante. Por ejemplo, el firmware de prueba de la versión coreana S24 Ultra ya llega a `Y` (número de versión del firmware de prueba: `S928NKSU4ZXKY/S928NOKR4ZXKY/S928NKSU4BXKY`)

Si quieres ver el historial de nuevas adiciones del servidor de firmware de prueba de Samsung, haz clic en [Ver registro de firmware de prueba de Samsung](https://github.com/Mai19930513/SamsungTestFirmwareVersionDecrypt/blob/master/test_firmware_changelog.txt). Si quieres ver los números de versión del firmware de Samsung ya decodificados, haz clic en [Ver números de versión del firmware de prueba de Samsung](https://github.com/Mai19930513/SamsungTestFirmwareVersionDecrypt/blob/master/firmware.json)
> Nota: Los números de versión del firmware registrados no están completos, limitados por los modelos de dispositivos agregados y las regiones, así como el porcentaje de MD5 del script que decodifica los números de versión del firmware, algunos números de versión del firmware de prueba no están decodificados.


El contenido anterior proviene de [sammyguru](https://sammyguru.com/how-to-read-firmware-version-of-your-samsung-galaxy-device/)

# Conocimientos relacionados con CSC
## ¿Qué es el archivo CSC de Samsung?
CSC significa Código de Producto Específico de País/Operador o Personalización de Software del Consumidor, es parte del archivo de firmware de Samsung. Al extraer el firmware, obtendrás varios archivos como `AP, BL, CP, CSC` y `Home CSC` (Nota: los dispositivos con versión Wifi no tienen archivo de banda base `CP`).
El archivo CSC contiene principalmente información relacionada con tu operador de red, ubicación, configuración de idioma del dispositivo, configuración de red y servidor de actualización de firmware.
> Algunos ejemplos de CSC incluyen ATT (AT&T) para EE.UU., TMB (T-Mobile), ATL (Vodafone) para España e IND, INA, INS (sin marca) para India.
## ¿Cómo elegir entre `Home CSC` y `CSC`?
  1. Si quieres conservar los datos al actualizar el firmware, elige el archivo CSC que comienza con `Home CSC`
  2. Si quieres restablecer el teléfono, elige el archivo CSC que comienza con `CSC`

## ¿Qué es el firmware OXM Multi-CSC?
OXM es un superconjunto que contiene internamente muchos sub-CSC. Si tu dispositivo Samsung tiene firmware multi-CSC, entonces puedes cambiar fácilmente la región.
OXM Multi-CSC contiene los siguientes CSC:
> ACR AFG AFR ARO ATO AUT BGL BNG BRI BTC BTU CAC CAM CHO COO DBT DKR ECT EGY EON ETL EUR GLB ILO INS ITV KSA LAO LUX LYS MID MM1 MWD MYM NEE NPL ORX OXM PAK PHE PHN ROM SEB SEE SEK SER SIN SKZ SLK SMA STH THL THR TMC TPA TPH TTT TUN TUR WTL XEF XEH XEO XEU XFE XME XSG XSP XTC XXV ZTO 

Además de OXM, hay muchos más multi-CSC, incluyendo:
> ODD, ODM, OJK, OJP, OJV, OLB, OLC, OMC, OSW, OWO, OXA, OXE, OXF, OXI, OXX, OYA, OYM, OYN, OYV y OZS, VFG, VFR, YXY.

Los siguientes son firmwares CSC únicos:
> BTC BTU CPW EMP GLB LYS MAT MM1 MTL NZC OPS PAN PNG PRO SIN SMA SMP STH TEB TEL TMC TNZ VAU VFJ VNZ WTL XFA XNF XNX XNZ XSA

Ciertas regiones recibirán actualizaciones del sistema primero, otras regiones pueden tardar días, semanas o incluso meses en recibir la actualización. Si tu dispositivo tiene firmware OXM Multi CSC, entonces puedes descargar e instalar fácilmente el archivo de firmware de la región donde está la actualización. Esto no afectará tu CSC original.
## ¿Por qué necesitas cambiar el archivo CSC?
Cambiar el CSC en tu dispositivo Samsung es principalmente para desbloquear restricciones específicas de la región. Un ejemplo perfecto es la función de grabación de llamadas, que no está disponible en muchos países.
Sin embargo, puedes habilitar fácilmente esta función simplemente cambiando el CSC a una de las regiones compatibles (como INS) o cualquiera de las siguientes regiones listadas a continuación.

|Código de Región|Región|
|---|---|
|EGY | Egipto |
|ILO | Israel |
|INS | India |
|LYS | Libia |
|NPB | Nepal (Nepal Telecom, NCELL) |
|SLK | Sri Lanka |
|THL | Tailandia |
|TUN | Túnez |
|XXV | Vietnam|

Además de esto, también puedes desbloquear otras funciones, incluyendo

- Faster OTA updates(Actualizaciones OTA más rápidas)
- Spam Blocking(Bloqueo de spam)
- Google Wallet(Cartera de Google)
- Samsung Pay(Pago de Samsung)
- ECG and Blood Pressure monitor(Monitor de ECG y presión arterial)
- VoLTE(Llamadas de voz de alta definición)
- WiFi Calling(Llamadas WiFi)

> Nota: Ningún CSC puede obtener todas las funciones, hay que elegir. Obtener ciertas funciones también puede causar que otras funciones no estén disponibles, cada uno decide.

## Cómo obtener tu información CSC
### Método uno: Código de marcación
Abre la aplicación de teléfono, ingresa `*#1234#`, la tercera línea que comienza con CSC es la información CSC. Como se muestra en la imagen a continuación, `CHC` después del modelo de teléfono `S9280` es la información CSC, representando la versión de China continental, `TGY` es el CSC usado en la región de Hong Kong, China
![](media/CSCinfo.jpg)

### Método dos: Interfaz de configuración del teléfono
Abre la configuración del teléfono, ve a `Acerca del teléfono->Información del software`, mira la tercera línea desde abajo `Versión del software del operador`, por ejemplo, lo siguiente `CHC/CHC,CHC/CHC`
![](media/CSCinfo2.png)
> Nota, el orden de división correcto de `CHC/CHC,CHC/CHC` debería ser: primera parte `CHC`, segunda parte `CHC,CHC`, tercera parte `CHC`, a continuación se explica el significado de cada parte:
>  - Primera parte `CHC`: Representa el CSC actualmente en uso, `CHC` representa China continental
>  - Segunda parte `CHC,CHC`: Esta parte tiene dos, indicando que es para dual SIM, `CHC,CHC` representa soporte para dual SIM de China continental
>  - Tercera parte `CHC`: Representa la región de fabricación del dispositivo, `CHC` representa China continental, si es `TGY` representa fabricado en Hong Kong, China. Algunos teléfonos de Hong Kong con firmware de China continental, esta posición seguirá siendo `TGY`, por lo tanto, puedes ver esta información de región de fabricación para distinguir si el dispositivo es versión de China continental.

## Cómo cambiar CSC
### Usar SamFW para cambiar CSC
Descarga el software SamFw Tool del [sitio web oficial de SamFW](https://samfw.com/blog/samfw-frp-tool-1-0-remove-samsung-frp-one-click), y descomprime, luego sigue estos pasos:
1. Primero retira la tarjeta SIM, conecta al PC a través del cable de datos USB
2. Haz clic derecho en SamFwFRPTool.exe, selecciona `Ejecutar como administrador`
3. Verifica si el teléfono está detectado, si está reconocido cambia a la opción `MTP`
4. Entra en `Configuración->Opciones de desarrollador del teléfono`, habilita `Depuración USB`
5. Abre el software de `Teléfono`, ingresa `*#0*#` para abrir el modo de prueba
6. Haz clic en la opción `Cambiar CSC` en la pestaña de SamFwFRPTool.
7. Mostrará una lista de todos los CSC compatibles, selecciona el nuevo CSC de la lista, luego haz clic en `Change` para confirmar el cambio.
8. SamFwFRPTool comenzará a cambiar el CSC, después de tener éxito reiniciará automáticamente el teléfono.

### Usar la herramienta Odin para cambiar CSC
Descargando firmware Samsung específico de multi-CSC (OXM), selecciona los archivos AP BL CP CSC en orden.
> Nota: Esta operación borrará todos los datos del dispositivo, invalidará su garantía y activará el contador Knox a 1.

El contenido anterior proviene de [droidwin](https://droidwin.com/change-csc-codes-samsung/)

## Lista CSC de Samsung
Abre Google, busca "Samsung CSC code list", puedes ver la información CSC de Samsung.
La siguiente tabla proviene del archivo `CSC-list.csv` del repositorio de Github `cslfiu`, [dirección del repositorio](https://github.com/cslfiu/Android-Security-Updates)

| **CSC** | **国家/运营商**                 | **国家**                | **运营商**           | **ISO国家代码** | **区域** | **子区域**                   |
|:-------:|:-----------------------------------:|:--------------------------:|:---------------------:|:------------:|:----------:|:-------------------------------:|
| 3IE     | Ireland (Three)                     | Ireland                    | Three                 | IRL          | Europe     | Northern Europe                 |
| ACG     | USA (Nextech / C-Spire)             | USA                        | Nextech / C-Spire     | USA          | Americas   | Northern America                |
| ACR     | Saudi Arabia                        | Saudi Arabia               | No-carrier            | SAU          | Asia       | Western Asia                    |
| AFG     | Afghanistan                         | Afghanistan                | No-carrier            | AFG          | Asia       | Southern Asia                   |
| AFR     | Kenya                               | Kenya                      | No-carrier            | KEN          | Africa     | Sub-Saharan Africa              |
| AIO     | USA (Cricket)                       | USA                        | Cricket               | USA          | Americas   | Northern America                |
| ALE     | Ecuador                             | Ecuador                    | No-carrier            | ECU          | Americas   | Latin America and the Caribbean |
| AMN     | Spain (Orange)                      | Spain                      | Orange                | ESP          | Europe     | Southern Europe                 |
| AMO     | Spain (Orange)                      | Spain                      | Orange                | ESP          | Europe     | Southern Europe                 |
| ANC     | Argentina                           | Argentina                  | No-carrier            | ARG          | Americas   | Latin America and the Caribbean |
| ANP     | Ireland                             | Ireland                    | No-carrier            | IRL          | Europe     | Northern Europe                 |
| ARO     | Argentina                           | Argentina                  | No-carrier            | ARG          | Americas   | Latin America and the Caribbean |
| ATL     | Spain (Vodafone)                    | Spain                      | Vodafone              | ESP          | Europe     | Southern Europe                 |
| ATO     | Austria (Open)                      | Austria                    | Open                  | AUT          | Europe     | Western Europe                  |
| ATT     | USA (AT&T)                          | USA                        | AT&T                  | USA          | Americas   | Northern America                |
| AUT     | Switzerland                         | Switzerland                | No-carrier            | CHE          | Europe     | Western Europe                  |
| AVF     | Albania (Vodafone)                  | Albania                    | Vodafone              | ALB          | Europe     | Southern Europe                 |
| BAT     | Mexico                              | Mexico                     | No-carrier            | MEX          | Americas   | Latin America and the Caribbean |
| BGL     | Bulgaria                            | Bulgaria                   | No-carrier            | BGR          | Europe     | Eastern Europe                  |
| BHT     | Bosnia and Herzegovina (BH TELECOM) | Bosnia and Herzegovina     | BH TELECOM            | BIH          | Europe     | Southern Europe                 |
| BMC     | Canada (Bell Mobile)                | Canada                     | Bell Mobile           | CAN          | Americas   | Northern America                |
| BNG     | Bangladesh                          | Bangladesh                 | No-carrier            | BGD          | Asia       | Southern Asia                   |
| BOG     | France (Bouygues)                   | France                     | Bouygues              | FRA          | Europe     | Western Europe                  |
| BRI     | Taiwan                              | Taiwan                     | No-carrier            | TWN          | Asia       | Eastern Asia                    |
| BST     | USA (Boost Mobile)                  | USA                        | Boost Mobile          | USA          | Americas   | Northern America                |
| BTC     | Libya                               | Libya                      | No-carrier            | LBY          | Africa     | Northern Africa                 |
| BTU     | United Kingdom                      | United Kingdom             | No-carrier            | GBR          | Europe     | Northern Europe                 |
| BVO     | Bolivia                             | Bolivia                    | No-carrier            | BOL          | Americas   | Latin America and the Caribbean |
| BVT     | Bolivia                             | Bolivia                    | No-carrier            | BOL          | Americas   | Latin America and the Caribbean |
| BVV     | Bolivia                             | Bolivia                    | No-carrier            | BOL          | Americas   | Latin America and the Caribbean |
| BWA     | Canada (SaskTel)                    | Canada                     | SaskTel               | CAN          | Americas   | Northern America                |
| CAC     | Uzbekistan                          | Uzbekistan                 | No-carrier            | UZB          | Asia       | Central Asia                    |
| CAM     | Cambodia                            | Cambodia                   | No-carrier            | KHM          | Asia       | South-eastern Asia              |
| CAU     | Caucasus Countries                  | Caucasus Countries         | No-carrier            |              |            |                                 |
| CCT     | USA (Xfinity Mobile)                | USA                        | Xfinity Mobile        | USA          | Americas   | Northern America                |
| CDR     | Dominican Republic                  | Dominican Republic         | No-carrier            | DOM          | Americas   | Latin America and the Caribbean |
| CEL     | Israel (Cellcom)                    | Israel                     | Cellcom               | ISR          | Asia       | Western Asia                    |
| CGU     | Guatemala (Tigo)                    | Guatemala                  | Tigo                  | GTM          | Americas   | Latin America and the Caribbean |
| CHA     | USA (Spectrum Mobile)               | USA                        | Spectrum Mobile       | USA          | Americas   | Northern America                |
| CHC     | China (Open China)                  | China                      | Open China            | CHN          | Asia       | Eastern Asia                    |
| CHE     | Chile (Entel PCS)                   | Chile                      | Entel PCS             | CHL          | Americas   | Latin America and the Caribbean |
| CHL     | Chile (Claro)                       | Chile                      | Claro                 | CHL          | Americas   | Latin America and the Caribbean |
| CHM     | China (China Mobile)                | China                      | China Mobile          | CHN          | Asia       | Eastern Asia                    |
| CHN     | China                               | China                      | No-carrier            | CHN          | Asia       | Eastern Asia                    |
| CHO     | Chile                               | Chile                      | No-carrier            | CHL          | Americas   | Latin America and the Caribbean |
| CHR     | Canada (Chatr Mobile)               | Canada                     | Chatr Mobile          | CAN          | Americas   | Northern America                |
| CHT     | Chile (Telefonica)                  | Chile                      | Telefonica            | CHL          | Americas   | Latin America and the Caribbean |
| CHV     | Chile (VTR)                         | Chile                      | VTR                   | CHL          | Americas   | Latin America and the Caribbean |
| CHX     | Chile (Nextel)                      | Chile                      | Nextel                | CHL          | Americas   | Latin America and the Caribbean |
| CNX     | Romania (Vodafone)                  | Romania                    | Vodafone              | ROU          | Europe     | Eastern Europe                  |
| COA     | Romania (Cosmote)                   | Romania                    | Cosmote               | ROU          | Europe     | Eastern Europe                  |
| COB     | Colombia (Movistar)                 | Colombia                   | Movistar              | COL          | Americas   | Latin America and the Caribbean |
| COE     | Colombia (ETB)                      | Colombia                   | ETB                   | COL          | Americas   | Latin America and the Caribbean |
| COL     | Colombia                            | Colombia                   | No-carrier            | COL          | Americas   | Latin America and the Caribbean |
| COM     | Colombia (Comcel)                   | Colombia                   | Comcel                | COL          | Americas   | Latin America and the Caribbean |
| COO     | Colombia                            | Colombia                   | No-carrier            | COL          | Americas   | Latin America and the Caribbean |
| COS     | Greece (Cosmote)                    | Greece                     | Cosmote               | GRC          | Europe     | Southern Europe                 |
| CPA     | Panama (Claro)                      | Panama                     | Claro                 | PAN          | Americas   | Latin America and the Caribbean |
| CPW     | United Kingdom (Carphone Warehouse) | United Kingdom             | Carphone Warehouse    | GBR          | Europe     | Northern Europe                 |
| CRC     | Chile                               | Chile                      | No-carrier            | CHL          | Americas   | Latin America and the Caribbean |
| CRG     | Croatia                             | Croatia                    | No-carrier            | HRV          | Europe     | Southern Europe                 |
| CRM     | South America (Moviestar)           | South America              | Moviestar             |              |            |                                 |
| CRO     | Croatia (T-Mobile)                  | Croatia                    | T-Mobile              | HRV          | Europe     | Southern Europe                 |
| CTC     | China (China Telecom)               | China                      | China Telecom         | CHN          | Asia       | Eastern Asia                    |
| CTE     | Honduras                            | Honduras                   | No-carrier            | HND          | Americas   | Latin America and the Caribbean |
| CTI     | Argentina (Claro)                   | Argentina                  | Claro                 | ARG          | Americas   | Latin America and the Caribbean |
| CTP     | Paraguay (Claro)                    | Paraguay                   | Claro                 | PRY          | Americas   | Latin America and the Caribbean |
| CTU     | Uruguay (Claro)                     | Uruguay                    | Claro                 | URY          | Americas   | Latin America and the Caribbean |
| CWT     | Taiwan                              | Taiwan                     | No-carrier            | TWN          | Asia       | Eastern Asia                    |
| CWW     | Jamaica                             | Jamaica                    | No-carrier            | JAM          | Americas   | Latin America and the Caribbean |
| CYO     | Cyprus (Cytamobile Vodafone)        | Cyprus                     | Cytamobile Vodafone   | CYP          | Asia       | Western Asia                    |
| CYV     | Cyprus (Vodafone)                   | Cyprus                     | Vodafone              | CYP          | Asia       | Western Asia                    |
| DBT     | Germany                             | Germany                    | No-carrier            | DEU          | Europe     | Western Europe                  |
| DDE     | Germany (Congstar)                  | Germany                    | Congstar              | DEU          | Europe     | Western Europe                  |
| DHR     | Croatia (Bonbon)                    | Croatia                    | Bonbon                | HRV          | Europe     | Southern Europe                 |
| DNL     | Netherlands (Ben NL)                | Netherlands                | Ben NL                | NLD          | Europe     | Western Europe                  |
| DOO     | Dominican Republic                  | Dominican Republic         | No-carrier            | DOM          | Americas   | Latin America and the Caribbean |
| DOR     | Dominican Republic (Orange)         | Dominican Republic         | Orange                | DOM          | Americas   | Latin America and the Caribbean |
| DPL     | Poland (Heyah)                      | Poland                     | Heyah                 | POL          | Europe     | Eastern Europe                  |
| DRE     | Austria (3 Hutchison)               | Austria                    | 3 Hutchison           | AUT          | Europe     | Western Europe                  |
| DTM     | Germany (T-Mobile)                  | Germany                    | T-Mobile              | DEU          | Europe     | Western Europe                  |
| EBE     | Ecuador                             | Ecuador                    | No-carrier            | ECU          | Americas   | Latin America and the Caribbean |
| ECO     | Ecuador                             | Ecuador                    | No-carrier            | ECU          | Americas   | Latin America and the Caribbean |
| ECT     | Nigeria                             | Nigeria                    | No-carrier            | NGA          | Africa     | Sub-Saharan Africa              |
| EGY     | Egypt                               | Egypt                      | No-carrier            | EGY          | Africa     | Northern Africa                 |
| EIR     | Ireland (eMobile)                   | Ireland                    | eMobile               | IRL          | Europe     | Northern Europe                 |
| EON     | Trinidad and Tobago                 | Trinidad and Tobago        | No-carrier            | TTO          | Americas   | Latin America and the Caribbean |
| EPL     | Germany (E-Plus)                    | Germany                    | E-Plus                | DEU          | Europe     | Western Europe                  |
| ERA     | Poland (T-Mobile)                   | Poland                     | T-Mobile              | POL          | Europe     | Eastern Europe                  |
| ERO     | Bosnia and Herzegovina              | Bosnia and Herzegovina     | No-carrier            | BIH          | Europe     | Southern Europe                 |
| ESK     | Canada (EastLink)                   | Canada                     | EastLink              | CAN          | Americas   | Northern America                |
| ETE     | El Salvador                         | El Salvador                | No-carrier            | SLV          | Americas   | Latin America and the Caribbean |
| ETL     | Czech Republic                      | Czech Republic             | No-carrier            | CZE          | Europe     | Eastern Europe                  |
| ETR     | Bangladesh                          | Bangladesh                 | No-carrier            | BGD          | Asia       | Southern Asia                   |
| EUR     | Greece                              | Greece                     | No-carrier            | GRC          | Europe     | Southern Europe                 |
| EVR     | United Kingdom (EE)                 | United Kingdom             | EE                    | GBR          | Europe     | Northern Europe                 |
| FMC     | Canada (Fido Mobile)                | Canada                     | Fido Mobile           | CAN          | Americas   | Northern America                |
| FOP     | Spain                               | Spain                      | No-carrier            | ESP          | Europe     | Southern Europe                 |
| FTB     | France                              | France                     | No-carrier            | FRA          | Europe     | Western Europe                  |
| FTM     | France (Orange)                     | France                     | Orange                | FRA          | Europe     | Western Europe                  |
| GBL     | Bulgaria                            | Bulgaria                   | No-carrier            | BGR          | Europe     | Eastern Europe                  |
| GCF     | Global Certification Forum          | Global Certification Forum | No-carrier            |              |            |                                 |
| GLB     | Philippines (Globe)                 | Philippines                | Globe                 | PHL          | Asia       | South-eastern Asia              |
| GLW     | Canada (Globalive Wind Mobile)      | Canada                     | Globalive Wind Mobile | CAN          | Americas   | Northern America                |
| H3G     | United Kingdom (H3G)                | United Kingdom             | H3G                   | GBR          | Europe     | Northern Europe                 |
| HAT     | Romania                             | Romania                    | No-carrier            | ROU          | Europe     | Eastern Europe                  |
| HTS     | Sweden (Tre)                        | Sweden                     | Tre                   | SWE          | Europe     | Northern Europe                 |
| HUI     | Italy (H3G)                         | Italy                      | H3G                   | ITA          | Europe     | Southern Europe                 |
| HUT     | Australia (Three/Vodafone)          | Australia                  | Three/Vodafone        | AUS          | Oceania    | Australia and New Zealand       |
| ICE     | Costa Rica                          | Costa Rica                 | No-carrier            | CRI          | Americas   | Latin America and the Caribbean |
| IDE     | Poland (Orange)                     | Poland                     | Orange                | POL          | Europe     | Eastern Europe                  |
| ILO     | Israel                              | Israel                     | No-carrier            | ISR          | Asia       | Western Asia                    |
| INS     | India                               | India                      | No-carrier            | IND          | Asia       | Southern Asia                   |
| INU     | India                               | India                      | No-carrier            | IND          | Asia       | Southern Asia                   |
| IRD     | Slovakia (Orange)                   | Slovakia                   | Orange                | SVK          | Europe     | Eastern Europe                  |
| ITV     | Italy                               | Italy                      | No-carrier            | ITA          | Europe     | Southern Europe                 |
| IUS     | Mexico                              | Mexico                     | No-carrier            | MEX          | Americas   | Latin America and the Caribbean |
| JDI     | Jamaica                             | Jamaica                    | No-carrier            | JAM          | Americas   | Latin America and the Caribbean |
| JED     | Saudi Arabia                        | Saudi Arabia               | No-carrier            | SAU          | Asia       | Western Asia                    |
| KDO     | Canada (Koodo Mobile)               | Canada                     | Koodo Mobile          | CAN          | Americas   | Northern America                |
| KEN     | Kenya                               | Kenya                      | No-carrier            | KEN          | Africa     | Sub-Saharan Africa              |
| KPN     | Netherlands (KPN)                   | Netherlands                | KPN                   | NLD          | Europe     | Western Europe                  |
| KSA     | Saudi Arabia                        | Saudi Arabia               | No-carrier            | SAU          | Asia       | Western Asia                    |
| KTC     | Korea (KT Corporation)              | Korea                      | KT Corporation        | KOR          | Asia       | Eastern Asia                    |
| LRA     | USA (Bluegrass Cellular)            | USA                        | Bluegrass Cellular    | USA          | Americas   | Northern America                |
| LUC     | Korea (LG Uplus)                    | Korea                      | LG Uplus              | KOR          | Asia       | Eastern Asia                    |
| LUX     | Luxembourg                          | Luxembourg                 | No-carrier            | LUX          | Europe     | Western Europe                  |
| LYS     | Libya                               | Libya                      | No-carrier            | LBY          | Africa     | Northern Africa                 |
| MAT     | Morocco (MAT)                       | Morocco                    | MAT                   | MAR          | Africa     | Northern Africa                 |
| MAX     | Austria (T-Mobile)                  | Austria                    | T-Mobile              | AUT          | Europe     | Western Europe                  |
| MBM     | Macedonia (T-Mobile)                | Macedonia                  | T-Mobile              | MKD          | Europe     | Southern Europe                 |
| MED     | Morocco                             | Morocco                    | No-carrier            | MAR          | Africa     | Northern Africa                 |
| MEO     | Portugal                            | Portugal                   | No-carrier            | PRT          | Europe     | Southern Europe                 |
| MET     | Ireland (Meteor)                    | Ireland                    | Meteor                | IRL          | Europe     | Northern Europe                 |
| MID     | Iraq                                | Iraq                       | No-carrier            | IRQ          | Asia       | Western Asia                    |
| MM1     | Singapore                           | Singapore                  | No-carrier            | SGP          | Asia       | South-eastern Asia              |
| MOB     | Austria (A1)                        | Austria                    | A1                    | AUT          | Europe     | Western Europe                  |
| MOT     | Slovenia (Mobitel)                  | Slovenia                   | Mobitel               | SVN          | Europe     | Southern Europe                 |
| MOZ     | Switzerland                         | Switzerland                | No-carrier            | CHE          | Europe     | Western Europe                  |
| MRU     | Mauritius                           | Mauritius                  | No-carrier            | MUS          | Africa     | Sub-Saharan Africa              |
| MSR     | Serbia (Telenor)                    | Serbia                     | Telenor               | SRB          | Europe     | Southern Europe                 |
| MTB     | Canada (Belarus)                    | Canada                     | Belarus               | CAN          | Americas   | Northern America                |
| MTL     | Bulgaria (MTL)                      | Bulgaria                   | MTL                   | BGR          | Europe     | Eastern Europe                  |
| MTZ     | Zambia (MTN Zambia)                 | Zambia                     | MTN Zambia            | ZMB          | Africa     | Sub-Saharan Africa              |
| MWD     | Morocco (MWD)                       | Morocco                    | MWD                   | MAR          | Africa     | Northern Africa                 |
| MXO     | Mexico                              | Mexico                     | No-carrier            | MEX          | Americas   | Latin America and the Caribbean |
| NBS     | South America (Open Line)           | South America              | Open Line             |              |            |                                 |
| NEE     | Nordic countries                    | Nordic countries           | No-carrier            |              |            |                                 |
| NPL     | Nepal                               | Nepal                      | No-carrier            | NPL          | Asia       | Southern Asia                   |
| NRJ     | France                              | France                     | No-carrier            | FRA          | Europe     | Western Europe                  |
| NZC     | New Zealand                         | New Zealand                | No-carrier            | NZL          | Oceania    | Australia and New Zealand       |
| O2C     | Czech Republic (O2C)                | Czech Republic             | O2C                   | CZE          | Europe     | Eastern Europe                  |
| O2I     | Ireland (O2)                        | Ireland                    | O2                    | IRL          | Europe     | Northern Europe                 |
| O2U     | United Kingdom (O2)                 | United Kingdom             | O2                    | GBR          | Europe     | Northern Europe                 |
| OMN     | Italy (Vodafone)                    | Italy                      | Vodafone              | ITA          | Europe     | Southern Europe                 |
| ONE     | Austria                             | Austria                    | No-carrier            | AUT          | Europe     | Western Europe                  |
| OPS     | Australia (Optus)                   | Australia                  | Optus                 | AUS          | Oceania    | Australia and New Zealand       |
| OPT     | Portugal (Optimus)                  | Portugal                   | Optimus               | PRT          | Europe     | Southern Europe                 |
| ORA     | United Kingdom (Orange)             | United Kingdom             | Orange                | GBR          | Europe     | Northern Europe                 |
| ORC     | France                              | France                     | No-carrier            | FRA          | Europe     | Western Europe                  |
| ORG     | Switzerland                         | Switzerland                | No-carrier            | CHE          | Europe     | Western Europe                  |
| ORN     | France                              | France                     | No-carrier            | FRA          | Europe     | Western Europe                  |
| ORO     | Romania (Orange)                    | Romania                    | Orange                | ROU          | Europe     | Eastern Europe                  |
| ORS     | Slovakia                            | Slovakia                   | No-carrier            | SVK          | Europe     | Eastern Europe                  |
| ORX     | Slovakia                            | Slovakia                   | No-carrier            | SVK          | Europe     | Eastern Europe                  |
| PAK     | Pakistan (PAK)                      | Pakistan                   | PAK                   | PAK          | Asia       | Southern Asia                   |
| PAN     | Hungary (Telenor)                   | Hungary                    | Telenor               | HUN          | Europe     | Eastern Europe                  |
| PBS     | Panama                              | Panama                     | No-carrier            | PAN          | Americas   | Latin America and the Caribbean |
| PCL     | Israel (Pelephone)                  | Israel                     | Pelephone             | ISR          | Asia       | Western Asia                    |
| PCT     | Puerto Rico                         | Puerto Rico                | No-carrier            | PRI          | Americas   | Latin America and the Caribbean |
| PCW     | Panama (Cable & Wireless)           | Panama                     | Cable & Wireless      | PAN          | Americas   | Latin America and the Caribbean |
| PET     | Peru                                | Peru                       | No-carrier            | PER          | Americas   | Latin America and the Caribbean |
| PGU     | Guatemala                           | Guatemala                  | No-carrier            | GTM          | Americas   | Latin America and the Caribbean |
| PHB     | Belgium                             | Belgium                    | No-carrier            | BEL          | Europe     | Western Europe                  |
| PHE     | Spain                               | Spain                      | No-carrier            | ESP          | Europe     | Southern Europe                 |
| PHN     | Netherlands                         | Netherlands                | No-carrier            | NLD          | Europe     | Western Europe                  |
| PLS     | Poland (PLUS)                       | Poland                     | PLUS                  | POL          | Europe     | Eastern Europe                  |
| PNG     | Papua New Guinea                    | Papua New Guinea           | No-carrier            | PNG          | Oceania    | Melanesia                       |
| PNT     | Peru (Nextel)                       | Peru                       | Nextel                | PER          | Americas   | Latin America and the Caribbean |
| PRO     | Belgium (Proximus)                  | Belgium                    | Proximus              | BEL          | Europe     | Western Europe                  |
| PRT     | Poland (Play)                       | Poland                     | Play                  | POL          | Europe     | Eastern Europe                  |
| PSN     | Argentina (Personal)                | Argentina                  | Personal              | ARG          | Americas   | Latin America and the Caribbean |
| PSP     | Paraguay (Personal)                 | Paraguay                   | Personal              | PRY          | Americas   | Latin America and the Caribbean |
| PTR     | Israel (Orange/Partner)             | Israel                     | Orange/Partner        | ISR          | Asia       | Western Asia                    |
| PVT     | Peru (Viettel)                      | Peru                       | Viettel               | PER          | Americas   | Latin America and the Caribbean |
| ROM     | Romania                             | Romania                    | No-carrier            | ROU          | Europe     | Eastern Europe                  |
| RWC     | Canada (Rogers)                     | Canada                     | Rogers                | CAN          | Americas   | Northern America                |
| SAM     | Peru (SAM)                          | Peru                       | SAM                   | PER          | Americas   | Latin America and the Caribbean |
| SEB     | Baltic                              | Baltic                     | No-carrier            |              |            |                                 |
| SEE     | South East Europe                   | South East Europe          | No-carrier            |              |            |                                 |
| SEK     | Ukraine (Kyivstar)                  | Ukraine                    | Kyivstar              | UKR          | Europe     | Eastern Europe                  |
| SER     | Russia                              | Russia                     | No-carrier            | RUS          | Europe     | Eastern Europe                  |
| SFR     | France (SFR)                        | France                     | SFR                   | FRA          | Europe     | Western Europe                  |
| SIM     | Slovenia (Si)                       | Slovenia                   | Si                    | SVN          | Europe     | Southern Europe                 |
| SIN     | Singapore (SingTel)                 | Singapore                  | SingTel               | SGP          | Asia       | South-eastern Asia              |
| SIO     | Slovakia                            | Slovakia                   | No-carrier            | SVK          | Europe     | Eastern Europe                  |
| SKC     | Korea (SK Telecom)                  | Korea                      | SK Telecom            | KOR          | Asia       | Eastern Asia                    |
| SKZ     | Kazakhstan                          | Kazakhstan                 | No-carrier            | KAZ          | Asia       | Central Asia                    |
| SLK     | Sri Lanka                           | Sri Lanka                  | No-carrier            | LKA          | Asia       | Southern Asia                   |
| SMA     | Philippines (Smart)                 | Philippines                | Smart                 | PHL          | Asia       | South-eastern Asia              |
| SMO     | Serbia                              | Serbia                     | No-carrier            | SRB          | Europe     | Southern Europe                 |
| SPR     | USA (Sprint)                        | USA                        | Sprint                | USA          | Americas   | Northern America                |
| STH     | Singapore (StarHub)                 | Singapore                  | StarHub               | SGP          | Asia       | South-eastern Asia              |
| SUN     | Switzerland                         | Switzerland                | No-carrier            | CHE          | Europe     | Western Europe                  |
| SWC     | Switzerland (Swisscom)              | Switzerland                | Swisscom              | CHE          | Europe     | Western Europe                  |
| TCE     | Mexico (Telcel)                     | Mexico                     | Telcel                | MEX          | Americas   | Latin America and the Caribbean |
| TCL     | Portugal (Vodafone)                 | Portugal                   | Vodafone              | PRT          | Europe     | Southern Europe                 |
| TDC     | Denmark                             | Denmark                    | No-carrier            | DNK          | Europe     | Northern Europe                 |
| TEB     | Bosnia and Herzegovina              | Bosnia and Herzegovina     | No-carrier            | BIH          | Europe     | Southern Europe                 |
| TEL     | Australia (Telstra)                 | Australia                  | Telstra               | AUS          | Oceania    | Australia and New Zealand       |
| TEN     | Norway (Telenor)                    | Norway                     | Telenor               | NOR          | Europe     | Northern Europe                 |
| TFN     | USA (Tracfone)                      | USA                        | Tracfone              | USA          | Americas   | Northern America                |
| TGP     | Paraguay (Tigo)                     | Paraguay                   | Tigo                  | PRY          | Americas   | Latin America and the Caribbean |
| TGU     | Guatemala                           | Guatemala                  | No-carrier            | GTM          | Americas   | Latin America and the Caribbean |
| TGY     | Hong Kong                           | Hong Kong                  | No-carrier            | HKG          | Asia       | Eastern Asia                    |
| THL     | Thailand                            | Thailand                   | No-carrier            | THA          | Asia       | South-eastern Asia              |
| THR     | Iran                                | Iran                       | No-carrier            | IRN          | Asia       | Southern Asia                   |
| TIM     | Italy (TIM)                         | Italy                      | TIM                   | ITA          | Europe     | Southern Europe                 |
| TLS     | Canada (Telus)                      | Canada                     | Telus                 | CAN          | Americas   | Northern America                |
| TMB     | USA (T-Mobile)                      | USA                        | T-Mobile              | USA          | Americas   | Northern America                |
| TMC     | Algeria                             | Algeria                    | No-carrier            | DZA          | Africa     | Northern Africa                 |
| TMH     | Hungary (T-mobile)                  | Hungary                    | T-mobile              | HUN          | Europe     | Eastern Europe                  |
| TMK     | USA (MetroPCS)                      | USA                        | MetroPCS              | USA          | Americas   | Northern America                |
| TML     | Bangladesh                          | Bangladesh                 | No-carrier            | BGD          | Asia       | Southern Asia                   |
| TMM     | Mexico (Movistar)                   | Mexico                     | Movistar              | MEX          | Americas   | Latin America and the Caribbean |
| TMN     | Portugal (TMN)                      | Portugal                   | TMN                   | PRT          | Europe     | Southern Europe                 |
| TMS     | Slovakia                            | Slovakia                   | No-carrier            | SVK          | Europe     | Eastern Europe                  |
| TMT     | Montenegro                          | Montenegro                 | No-carrier            | MNE          | Europe     | Southern Europe                 |
| TMU     | United Kingdom (T-Mobile)           | United Kingdom             | T-Mobile              | GBR          | Europe     | Northern Europe                 |
| TMZ     | Czech Republic (T-Mobile)           | Czech Republic             | T-Mobile              | CZE          | Europe     | Eastern Europe                  |
| TNL     | Netherlands (T-Mobile)              | Netherlands                | T-Mobile              | NLD          | Europe     | Western Europe                  |
| TNZ     | New Zealand                         | New Zealand                | No-carrier            | NZL          | Oceania    | Australia and New Zealand       |
| TOP     | Serbia (VIP)                        | Serbia                     | VIP                   | SRB          | Europe     | Southern Europe                 |
| TPA     | Panama                              | Panama                     | No-carrier            | PAN          | Americas   | Latin America and the Caribbean |
| TPD     | Netherlands                         | Netherlands                | No-carrier            | NLD          | Europe     | Western Europe                  |
| TPH     | Portugal (TPH)                      | Portugal                   | TPH                   | PRT          | Europe     | Southern Europe                 |
| TPL     | Poland (T-mobile)                   | Poland                     | T-mobile              | POL          | Europe     | Eastern Europe                  |
| TRA     | Croatia                             | Croatia                    | No-carrier            | HRV          | Europe     | Southern Europe                 |
| TRC     | Turkey                              | Turkey                     | No-carrier            | TUR          | Asia       | Western Asia                    |
| TRG     | Austria (Telering)                  | Austria                    | Telering              | AUT          | Europe     | Western Europe                  |
| TSI     | Ireland                             | Ireland                    | No-carrier            | IRL          | Europe     | Northern Europe                 |
| TSR     | Serbia (Telekom)                    | Serbia                     | Telekom               | SRB          | Europe     | Southern Europe                 |
| TTR     | Austria                             | Austria                    | No-carrier            | AUT          | Europe     | Western Europe                  |
| TTT     | Trinidad and Tobago                 | Trinidad and Tobago        | No-carrier            | TTO          | Americas   | Latin America and the Caribbean |
| TUN     | Tunisia                             | Tunisia                    | No-carrier            | TUN          | Africa     | Northern Africa                 |
| TUR     | Turkey                              | Turkey                     | No-carrier            | TUR          | Asia       | Western Asia                    |
| TWO     | Croatia (TELE2)                     | Croatia                    | TELE2                 | HRV          | Europe     | Southern Europe                 |
| UFN     | Argentina (Movistar)                | Argentina                  | Movistar              | ARG          | Americas   | Latin America and the Caribbean |
| UFU     | Uruguay                             | Uruguay                    | No-carrier            | URY          | Americas   | Latin America and the Caribbean |
| UPO     | Uruguay                             | Uruguay                    | No-carrier            | URY          | Americas   | Latin America and the Caribbean |
| USC     | USA (US Cellular)                   | USA                        | US Cellular           | USA          | Americas   | Northern America                |
| UYO     | Uruguay                             | Uruguay                    | No-carrier            | URY          | Americas   | Latin America and the Caribbean |
| VAU     | Australia (Vodafone)                | Australia                  | Vodafone              | AUS          | Oceania    | Australia and New Zealand       |
| VD2     | Germany (Vodafone)                  | Germany                    | Vodafone              | DEU          | Europe     | Western Europe                  |
| VDC     | Czech Republic (Vodafone)           | Czech Republic             | Vodafone              | CZE          | Europe     | Eastern Europe                  |
| VDF     | Netherlands (Vodafone)              | Netherlands                | Vodafone              | NLD          | Europe     | Western Europe                  |
| VDH     | Hungary (Vodafone)                  | Hungary                    | Vodafone              | HUN          | Europe     | Eastern Europe                  |
| VDI     | Ireland (Vodafone)                  | Ireland                    | Vodafone              | IRL          | Europe     | Northern Europe                 |
| VDS     | Sweden                              | Sweden                     | No-carrier            | SWE          | Europe     | Northern Europe                 |
| VFJ     | Fiji (Vodafone)                     | Fiji                       | Vodafone              | FJI          | Oceania    | Melanesia                       |
| VGF     | France                              | France                     | No-carrier            | FRA          | Europe     | Western Europe                  |
| VGR     | Greece (Vodafone)                   | Greece                     | Vodafone              | GRC          | Europe     | Southern Europe                 |
| VIA     | Germany (O2)                        | Germany                    | O2                    | DEU          | Europe     | Western Europe                  |
| VIM     | Macedonia                           | Macedonia                  | No-carrier            | MKD          | Europe     | Southern Europe                 |
| VIP     | Croatia (VIPNET)                    | Croatia                    | VIPNET                | HRV          | Europe     | Southern Europe                 |
| VIR     | United Kingdom                      | United Kingdom             | No-carrier            | GBR          | Europe     | Northern Europe                 |
| VMC     | Canada (Virgin Mobile)              | Canada                     | Virgin Mobile         | CAN          | Americas   | Northern America                |
| VMU     | USA (Virgin Mobile)                 | USA                        | Virgin Mobile         | USA          | Americas   | Northern America                |
| VNZ     | New Zealand (Vodafone)              | New Zealand                | Vodafone              | NZL          | Oceania    | Australia and New Zealand       |
| VOD     | United Kingdom (Vodafone)           | United Kingdom             | Vodafone              | GBR          | Europe     | Northern Europe                 |
| VTR     | Canada (Videotron)                  | Canada                     | Videotron             | CAN          | Americas   | Northern America                |
| VVT     | Bulgaria (VVT)                      | Bulgaria                   | VVT                   | BGR          | Europe     | Eastern Europe                  |
| VZW     | USA (Verizon)                       | USA                        | Verizon               | USA          | Americas   | Northern America                |
| WAN     | Taiwan                              | Taiwan                     | No-carrier            | TWN          | Asia       | Eastern Asia                    |
| WIN     | Italy (Wind)                        | Italy                      | Wind                  | ITA          | Europe     | Southern Europe                 |
| WTL     | Saudi Arabia                        | Saudi Arabia               | No-carrier            | SAU          | Asia       | Western Asia                    |
| XAA     | USA (Unbranded/Unlocked)            | USA                        | Unbranded/Unlocked    | USA          | Americas   | Northern America                |
| XAC     | Canada (Unbranded)                  | Canada                     | Unbranded             | CAN          | Americas   | Northern America                |
| XAG     | USA (Tracfone)                      | USA                        | Tracfone              | USA          | Americas   | Northern America                |
| XAR     | USA (Cellular South)                | USA                        | Cellular South        | USA          | Americas   | Northern America                |
| XAS     | USA (Unbranded/Unlocked)            | USA                        | Unbranded/Unlocked    | USA          | Americas   | Northern America                |
| XEB     | Belgium                             | Belgium                    | No-carrier            | BEL          | Europe     | Western Europe                  |
| XEC     | Spain (Movistar)                    | Spain                      | Movistar              | ESP          | Europe     | Southern Europe                 |
| XEE     | Sweden                              | Sweden                     | No-carrier            | SWE          | Europe     | Northern Europe                 |
| XEF     | France                              | France                     | No-carrier            | FRA          | Europe     | Western Europe                  |
| XEG     | Germany (1&1)                       | Germany                    | 1&1                   | DEU          | Europe     | Western Europe                  |
| XEH     | Hungary                             | Hungary                    | No-carrier            | HUN          | Europe     | Eastern Europe                  |
| XEN     | Netherlands                         | Netherlands                | No-carrier            | NLD          | Europe     | Western Europe                  |
| XEO     | Poland                              | Poland                     | No-carrier            | POL          | Europe     | Eastern Europe                  |
| XEU     | Ireland                             | Ireland                    | No-carrier            |              |            |                                 |
| XEZ     | Czech Republic                      | Czech Republic             | No-carrier            | CZE          | Europe     | Eastern Europe                  |
| XFA     | South Africa                        | South Africa               | No-carrier            | ZAF          | Africa     | Sub-Saharan Africa              |
| XFC     | South Africa                        | South Africa               | No-carrier            | ZAF          | Africa     | Sub-Saharan Africa              |
| XFE     | South Africa                        | South Africa               | No-carrier            | ZAF          | Africa     | Sub-Saharan Africa              |
| XFM     | South Africa                        | South Africa               | No-carrier            | ZAF          | Africa     | Sub-Saharan Africa              |
| XFU     | Saudi Arabia (STC)                  | Saudi Arabia               | STC                   | SAU          | Asia       | Western Asia                    |
| XFV     | South Africa (Vodafone)             | South Africa               | Vodafone              | ZAF          | Africa     | Sub-Saharan Africa              |
| XID     | Indonesia                           | Indonesia                  | No-carrier            | IDN          | Asia       | South-eastern Asia              |
| XME     | Malaysia                            | Malaysia                   | No-carrier            | MYS          | Asia       | South-eastern Asia              |
| XSA     | Australia                           | Australia                  | No-carrier            | AUS          | Oceania    | Australia and New Zealand       |
| XSE     | Indonesia                           | Indonesia                  | No-carrier            | IDN          | Asia       | South-eastern Asia              |
| XSG     | United Arab Emirates                | United Arab Emirates       | No-carrier            | ARE          | Asia       | Western Asia                    |
| XSO     | Singapor (Singtel)                  | Singapor                   | Singtel               | SGP          | Asia       | South-eastern Asia              |
| XSP     | Singapore                           | Singapore                  | No-carrier            | SGP          | Asia       | South-eastern Asia              |
| XSS     | United Arab Emirates                | United Arab Emirates       | No-carrier            | ARE          | Asia       | Western Asia                    |
| XTC     | Philippines (Open Line)             | Philippines                | Open Line             | PHL          | Asia       | South-eastern Asia              |
| XTE     | Philippines (Sun Cellular)          | Philippines                | Sun Cellular          | PHL          | Asia       | South-eastern Asia              |
| XXV     | Vietnam                             | Vietnam                    | No-carrier            | VNM          | Asia       | South-eastern Asia              |
| YOG     | Spain (Yoigo)                       | Spain                      | Yoigo                 | ESP          | Europe     | Southern Europe                 |
| ZTA     | Brazil (Claro)                      | Brazil                     | Claro                 | BRA          | Americas   | Latin America and the Caribbean |
| ZTM     | Brazil (TIM)                        | Brazil                     | TIM                   | BRA          | Americas   | Latin America and the Caribbean |
| ZTO     | Brazil                              | Brazil                     | No-carrier            | BRA          | Americas   | Latin America and the Caribbean |
| ZTR     | Brazil (Oi)                         | Brazil                     | Oi                    | BRA          | Americas   | Latin America and the Caribbean |
| ZVV     | Brazil (VIVO)                       | Brazil                     | VIVO                  | BRA          | Americas   | Latin America and the Caribbean |
