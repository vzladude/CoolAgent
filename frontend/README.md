# CoolAgent Mobile Frontend

Expo + React Native MVP mobile app for CoolAgent.

## Current Scope

- Runs with mock data first.
- Production mobile code lives here in `frontend/`.
- Target is phones through Expo/React Native, not a web app.
- Visual reference lives in `documentation/design/CoolAgentDesign/`.
- RAG document upload and manual ingestion are not part of the mobile MVP.

## Screens Included

- Home / tool hub.
- Technical cases and case chat.
- Visual diagnosis flow.
- Error code catalog.
- Technical calculators.
- Guides and procedures.
- Offline / sync states.
- Basic settings.

## Data Approach

Mock data is centralized in `src/mocks/data.ts`. API adapters live in
`src/services/api.ts`, so each screen can be wired to the backend incrementally
without redesigning the UI.

The cases/chat flow already tries the backend first:

- Android emulator default: `http://10.0.2.2:8000/api/v1`.
- iOS simulator default: `http://localhost:8000/api/v1`.
- Physical phone: set `EXPO_PUBLIC_API_URL` to your computer LAN URL, for
  example `http://192.168.1.50:8000/api/v1`.

If the backend is unavailable, the app falls back to mock data so UI work can
continue.

## Run

Start Expo and open the app with Expo Go on a phone, or use an Android/iOS
emulator:

```bash
npm start
npm run android
npm run ios
```

The `web` target is intentionally not part of this MVP because CoolAgent mobile
is being designed for technicians using phones in the field.
