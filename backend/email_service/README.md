# AeroCrop.ai Email Microservice

This microservice receives crop diagnostic and advisory telemetry from AeroCrop.ai, dynamically generates a high-fidelity, visually stunning 3-section PDF report (मराठी Marathi, English, हिंदी Hindi) with pure Devanagari font rendering, and dispatches it directly to the farmer's email address via Gmail SMTP.


## Prerequisites & Installation

1. Open a terminal inside this directory:
   ```bash
   cd email_service
   npm install
   ```

2. Edit `.env` file with your email credentials:
   ```env
   PORT=5000
   FROM=your_email@gmail.com
   PASS=your_16_character_app_password
   ```

> **How to get a Gmail App Password:**
> 1. Go to your [Google Account](https://myaccount.google.com/) > **Security**.
> 2. Ensure **2-Step Verification** is turned ON.
> 3. Go to **App passwords** (search "App passwords" in the search bar).
> 4. Create a new app named `AeroCrop` and copy the generated 16-character code into `PASS`.

## Running the Service

- Production:
  ```bash
  npm start
  ```
- Development (auto-reloads on edit):
  ```bash
  npm run dev
  ```

## Endpoints

- `GET /health` : Verifies service status and SMTP configuration.
- `POST /send-email` : Generates the advisory PDF and emails it to the farmer.
