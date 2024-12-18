# Beregningstjeneste

## Introduktion
Denne mikroservice er designet til at beregne samlede priser for skader og abonnementer i forbindelse med et biludlejningssystem. Den integrerer med eksterne tjenester for at hente data om skader og abonnementer og kombinerer disse for at give en samlet prisberegning.

## Funktioner
- Hent skadedata fra skadetjenesten.
- Hent abonnementsdata fra abonnementstjenesten.
- Beregn samlede priser baseret på skader og abonnementsperiode.
- Log alle beregninger i en SQLite-database.
- API-endpoints til at få adgang til beregningshistorik og total omsætning.

## Teknologier
- Flask: Webframework til at bygge API'en.
- SQLite: Database til logning af beregningsdata.
- Python-dotenv: Håndtering af miljøvariabler.
- Flask-JWT-Extended: Håndtering af autentificering via JWT-tokens.

## Forudsætninger
Før du starter, skal følgende være installeret:
- Python 3.10 eller nyere
- Docker (hvis du vil køre tjenesten i en container)

## Opsætning

### Lokalt miljø
1. Klon dette repository:
   ```bash
   git clone <repository-url>
   cd <repository-mappen>
   ```
2. Opret et virtuelt miljø og installer afhængigheder:
   ```bash
   python -m venv venv
   source venv/bin/activate  # På Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Opret en `.env`-fil i roden af projektet og angiv miljøvariabler:
   ```env
   DB_PATH=calculation_service.db
   KEY=din_hemmelige_nøgle
   ```
4. Start applikationen:
   ```bash
   python app.py
   ```

### Docker
1. Byg Docker-billedet:
   ```bash
   docker build -t beregningstjeneste .
   ```
2. Kør containeren:
   ```bash
   docker run -d -p 80:80 --env-file .env beregningstjeneste
   ```

## API-dokumentation

### Endpoints

#### `GET /`
Returnerer information om tjenesten.

#### `POST /calculate-total-price`
Beregner den samlede pris for en kunde og en bil.

- **Headers:**
  - `Authorization: Bearer <jwt-token>`
- **Body:**
  ```json
  {
      "customer_id": 1,
      "car_id": 101
  }
  ```
- **Respons:**
  ```json
  {
      "total_damage_cost": 200,
      "total_subscription_cost": 600,
      "total_price": 800
  }
  ```

#### `GET /get-all-calculations`
Henter alle beregninger fra databasen.

- **Headers:**
  - `Authorization: Bearer <jwt-token>`
- **Respons:**
  ```json
  [
      {
          "id": 1,
          "customer_id": 1,
          "car_id": 101,
          "start_date": "2024-01-01",
          "end_date": "2024-03-01",
          "total_damage_cost": 200,
          "total_subscription_cost": 600,
          "total_price": 800,
          "timestamp": "2024-12-18T12:34:56"
      }
  ]
  ```

#### `GET /calculate-total-revenue`
Beregner den samlede omsætning baseret på tidligere beregninger.

- **Headers:**
  - `Authorization: Bearer <jwt-token>`
- **Respons:**
  ```json
  {
      "total_revenue": 10000
  }
  ```

## Database
Tabellen `calculation_requests` oprettes automatisk, hvis den ikke allerede findes. Den indeholder følgende kolonner:

- `id`: Primær nøgle
- `customer_id`: ID for kunden
- `car_id`: ID for bilen
- `start_date`: Startdato for abonnementet
- `end_date`: Slutdato for abonnementet
- `total_damage_cost`: Samlet omkostning for skader
- `total_subscription_cost`: Samlet omkostning for abonnementet
- `total_price`: Samlet pris
- `timestamp`: Tidsstempel for beregningen

## Miljøvariabler
- `DB_PATH`: Stien til SQLite-databasen (standard: `calculation_service.db`).
- `KEY`: JWT-hemmelig nøgle til autentificering.

## Fejlhåndtering
Tjenesten håndterer fejl som f.eks.:
- Problemer med eksterne tjenester (f.eks. skadetjeneste eller abonnementstjeneste).
- Ugyldige inputdata.
- Databasefejl.

## Licens
Dette projekt er licenseret under MIT-licensen.

