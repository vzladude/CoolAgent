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
