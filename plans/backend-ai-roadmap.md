# CoolAgent - Backend AI Roadmap

**Estado actual:** Backend base funcional con Claude Haiku API, PostgreSQL/pgvector, Redis, MinIO, RAG probado end-to-end, guardrails de dominio, usage/cache exacto, streaming WebSocket, casos tecnicos con contexto robusto y catalogo de codigos de error derivado de Knowledge.
**Fecha de corte:** 3 de mayo de 2026
**Uso de esta carpeta:** `plans/` contiene planes temporales de la tarea activa. La fuente central de verdad vive en `documentation/CoolAgent_Documentacion_Maestra.docx`.
**Nota:** No se planea pasar a staging/produccion pronto. Alembic se agrega ahora para que ese futuro paso sea mas simple y seguro.

---

## Fase A - RAG Pipeline - CERRADA

**Prioridad:** ALTA  
**Impacto:** Diferencia a CoolAgent de un chat generico.

### Resultado

El pipeline RAG ya esta implementado y probado localmente con Claude:

1. **EmbeddingProvider local:** `sentence-transformers` con `all-MiniLM-L6-v2` y embeddings de 384 dimensiones.
2. **Ingesta:** endpoints para texto y PDF con chunking, embeddings y almacenamiento en pgvector.
3. **Busqueda semantica:** endpoint de busqueda con filtros opcionales por fabricante, modelo y categoria.
4. **Chat con contexto:** `ChatService` recupera contexto RAG y lo inyecta en el prompt del provider Claude.
5. **Validacion real:** se ingesto un documento de prueba `Carrier 38AKS`; la busqueda recupero el chunk esperado y Claude respondio citando la fuente.
6. **Base de migraciones:** Alembic queda como historial oficial de cambios de schema para evitar depender de `create_all()` en entornos futuros.
7. **Glosario RAG:** `/api/v1/knowledge/glossary` permite revisar que documentos alimentan el RAG sin exponer chunks completos.
8. **Tests:** suite inicial unit + integration con provider AI mockeado y base `coolagent_test`.

### Archivos principales

- `backend/app/ai/providers/local_embedding_provider.py`
- `backend/app/services/rag_service.py`
- `backend/app/routers/knowledge.py`
- `backend/app/services/chat_service.py`
- `backend/app/ai/prompts.py`
- `backend/app/models/knowledge.py`
- `backend/alembic/versions/20260430_0001_initial_rag_baseline.py`
- `backend/tests/`

### Cierre formal

1. Migraciones Alembic agregadas y aplicadas localmente sin borrar datos RAG.
2. Tests unitarios e integracion corriendo en verde con provider AI mockeado.
3. Glosario RAG disponible para revisar documentos ingeridos.
4. Hito estable confirmado en git.

---

## Fase B0 - Guardrails y prompt de refrigeracion general

**Prioridad:** ALTA  
**Impacto:** Evita cachear respuestas que no respeten el dominio del asistente.

### Resultado esperado

1. System prompt actualizado para refrigeracion general, no solo HVAC/R industrial.
2. `DomainGuard` bloquea consultas claramente fuera del dominio sin llamar a Claude ni RAG.
3. Temas auxiliares se permiten cuando estan conectados al trabajo tecnico: electricidad aplicada, seguridad, herramientas, normativa, mediciones y diagnostico.
4. Se define `PROMPT_POLICY_VERSION` para que el cache futuro no reutilice respuestas de politicas antiguas.
5. Tests unitarios cubren consultas permitidas, rechazadas y prompt injection.

### Archivos principales

- `backend/app/ai/prompts.py`
- `backend/app/services/domain_guard.py`
- `backend/app/services/chat_service.py`
- `backend/tests/unit/test_domain_guard.py`

---

## Fase B - Cache con Redis

**Prioridad:** MEDIA  
**Impacto:** Reducir costo y latencia.

### Estado actual

Fase B esta iniciada. Ya existe una primera capa segura: tracking de uso/tokens y cache exacto con Redis. No se implemento cache semantico todavia para evitar devolver respuestas viejas cuando cambie el contexto tecnico.

### Implementado

1. Tabla `usage_events` con migracion Alembic `20260501_0002`.
2. `UsageService` registra llamadas reales al provider, cache hits y bloqueos de dominio.
3. Endpoint `GET /api/v1/usage/summary` resume eventos, tokens y cache.
4. `ResponseCache` guarda respuestas exactas en Redis con TTL.
5. La llave de cache incluye provider, modelo, `PROMPT_POLICY_VERSION`, pregunta normalizada, huella del historial, hash del contexto RAG y huella global de la knowledge base.
6. Si Redis falla, el chat sigue funcionando y llama al provider normalmente.
7. `RAGService.knowledge_fingerprint()` cambia cuando se ingieren o borran documentos/chunks, por lo que respuestas antiguas dejan de coincidir.
8. Migracion Alembic `20260501_0003` agrega costo estimado por evento y ahorro estimado por cache.
9. `/api/v1/usage/summary` acepta filtros por caso tecnico, fechas y modelo. `conversation_id` queda como alias temporal.
10. Los precios son configurables por `USAGE_PRICING_JSON` o por variables simples de input/output por 1M tokens. No se fijan precios reales en codigo.

### Pendiente

1. Cache semantico con criterios estrictos de similitud.
2. Invalidacion explicita de Redis si mas adelante se quiere limpiar memoria inmediatamente, no solo cambiar llaves.
3. Rate limiting, cuotas y proteccion de creditos antes de uso real multiusuario. Este punto queda documentado como pendiente, pero se pospone porque debe disenarse junto con usuarios, planes, costo por usuario y monetizacion.

### Decision sobre rate limiting

No se implementa rate limiting en este momento. Aunque seria util como cinturon de seguridad de costos, conviene esperar hasta definir autenticacion, usuarios, planes comerciales y como se calculara el costo por usuario. Implementarlo ahora probablemente obligaria a rehacerlo cuando se disene la monetizacion.

Queda pendiente para una fase futura:

1. Limites por usuario, no solo limites globales.
2. Limites separados para chat, vision, ingesta RAG y busqueda.
3. Contadores por ventana de tiempo usando Redis.
4. Politica de respuesta `429 Too Many Requests`.
5. Relacion con planes pagos, pruebas gratis, creditos internos o cuotas mensuales.
6. Reportes de costo por usuario/caso tecnico/modelo para tomar decisiones de precio.

### Archivos esperados

- `backend/app/services/cache_service.py`
- `backend/app/routers/usage.py`
- `backend/app/services/usage_service.py`
- `backend/app/models/usage.py`

---

## Fase C - WebSocket Streaming - IMPLEMENTADA

**Prioridad:** MEDIA  
**Impacto:** Mejora UX del chat.

### Resultado

El backend ya tiene streaming por WebSocket para chat:

1. Endpoint oficial `WebSocket /api/v1/chat/cases/{case_id}/messages/stream`.
2. Endpoint legacy temporal `WebSocket /api/v1/chat/conversations/{conversation_id}/messages/stream` se conserva como alias.
3. El cliente envia `{ "content": "..." }` al abrir el socket.
4. El backend envia eventos JSON:
   - `delta`: fragmentos de texto mientras Claude responde.
   - `done`: metadata final del mensaje guardado, modelo, tokens y estado de cache.
   - `error`: payload invalido o caso tecnico no encontrado.
5. El flujo conserva el mismo orden seguro: `DomainGuard -> contexto del caso -> RAG -> cache exacto -> provider stream -> persistencia -> usage`.
6. Si hay cache hit o bloqueo de dominio, responde por el mismo canal sin llamar a Claude.
7. Al terminar el stream, guarda el mensaje completo del asistente, actualiza cache y registra usage/costos.
8. `ClaudeProvider.chat_stream()` ahora captura metadata final de tokens cuando Anthropic la envia.

### Archivos esperados

- `backend/app/routers/chat.py`
- `backend/app/services/chat_service.py`
- `backend/app/ai/providers/base.py`
- `backend/app/ai/providers/claude_provider.py`
- `backend/tests/unit/test_chat_router_stream.py`

---

## Fase C2 - Technical Cases y contexto robusto - IMPLEMENTADA

**Prioridad:** ALTA  
**Impacto:** Evita que el chat sea una conversacion infinita sin estructura.

### Resultado

El dominio oficial del chat pasa de `Conversation` a `TechnicalCase`. Un caso tecnico representa un equipo, falla o trabajo especifico, y dentro vive el historial de mensajes. Esto prepara el frontend para una UX tipo lista de casos + chat activo + panel editable de datos del caso.

### Implementado

1. Tabla oficial `technical_cases` con metadata opcional: fabricante, modelo, categoria, estado, resumen tecnico y datos de compactacion.
2. Migraciones Alembic `20260501_0004` y `20260501_0005` migran `conversations` a `technical_cases` sin perder mensajes existentes.
3. La base local quedo validada: 3 casos migrados, 4 mensajes conservados, 1 documento RAG y 1 chunk RAG intactos.
4. API nueva oficial:
   - `POST /api/v1/chat/cases`
   - `GET /api/v1/chat/cases`
   - `GET /api/v1/chat/cases/{case_id}`
   - `PATCH /api/v1/chat/cases/{case_id}`
   - `GET /api/v1/chat/cases/{case_id}/messages`
   - `POST /api/v1/chat/cases/{case_id}/messages`
   - `WebSocket /api/v1/chat/cases/{case_id}/messages/stream`
5. Endpoints legacy `/conversations` siguen funcionando como aliases temporales, pero quedan deprecados internamente.
6. `TechnicalCaseContextService` compacta contexto cuando hay mas de 30 mensajes no resumidos o mas de 16,000 tokens estimados, conservando siempre los ultimos 10 mensajes completos.
7. La compactacion usa Claude y guarda un resumen tecnico de maximo aproximado 1,500 tokens. Si falla, el chat sigue con resumen existente + mensajes recientes + RAG.
8. La llave de cache ahora incluye `technical_case_id`, fingerprint del resumen/contexto, ultimos mensajes, contexto RAG y huella de knowledge base.
9. Las llamadas de compactacion se registran en usage como `event_type="context_compaction"`.
10. Tests Docker: `51 passed`.

### Frontend recomendado

1. Lista de casos tecnicos en vez de un chat central infinito.
2. Chat activo con streaming.
3. Panel editable de metadata del caso: fabricante, modelo, categoria y estado.
4. Sugerencia de nuevo caso si el usuario cambia claramente de equipo o falla, sin bloquearlo.

### Pendiente

1. No implementar todavia usuarios/customer accounts.
2. No implementar monetizacion todavia.
3. No implementar rate limiting hasta disenar usuarios, planes y costo por usuario.
4. No implementar cache semantico hasta comprobar ahorro real suficiente.

### Archivos principales

- `backend/app/models/technical_case.py`
- `backend/app/services/technical_case_context_service.py`
- `backend/app/services/chat_service.py`
- `backend/app/routers/chat.py`
- `backend/alembic/versions/20260501_0004_technical_cases.py`
- `backend/alembic/versions/20260501_0005_merge_legacy_conversations.py`
- `backend/tests/integration/test_technical_cases_api.py`
- `backend/tests/unit/test_technical_case_context_service.py`

---

## Fase D - Codigos de error derivados de Knowledge - IMPLEMENTADA

**Prioridad:** MEDIA  
**Impacto:** Feature util para modo offline y diagnostico rapido.

### Estado actual

La base tecnica ya esta implementada. `knowledge_documents` y `knowledge_chunks` siguen siendo la fuente de verdad. `error_codes` funciona como un indice estructurado y revisado derivado de esos documentos, no como una base de conocimiento paralela.

Nota de validacion pendiente: el flujo tecnico esta cubierto por tests automaticos, pero aun falta probarlo con un manual real de codigos de error. El usuario espera recibir ese documento en los proximos dias. Hasta completar esa prueba, no asumir que el extractor simple es suficiente para tablas complejas de fabricantes.

### Implementado

1. Migracion Alembic `20260501_0006` agrega `source`, `updated_at` e indices por fabricante/modelo.
2. `GET /api/v1/error-codes/` busca por codigo, fabricante y modelo con paginacion `limit`/`offset`.
3. `GET /api/v1/error-codes/manufacturers` lista fabricantes con conteos reales de modelos y codigos.
4. `backend/scripts/seed_error_codes.py` crea fabricantes prioritarios de forma idempotente: Carrier, Trane, Daikin, LG, Samsung, Copeland, Danfoss y Bitzer.
5. El seed no inventa codigos. El arreglo `TRUSTED_ERROR_CODES` queda listo para agregar codigos solo cuando provengan de manuales, boletines o fuentes trazables.
6. Validacion local: 8 fabricantes cargados, 0 codigos inventados, RAG intacto.
7. Tests Docker: `54 passed`.
8. Migracion Alembic `20260502_0007` agrega trazabilidad desde `error_codes` hacia `knowledge_documents` y `knowledge_chunks`.
9. Cada codigo derivado guarda `source_document_id`, `source_chunk_id`, `source_page`, `source_excerpt`, `confidence`, `extraction_metadata` y `review_status`.
10. Endpoint `POST /api/v1/error-codes/extract/from-document/{document_id}` extrae candidatos desde un documento ya cargado en RAG.
11. Los candidatos extraidos quedan por defecto en `pending_review`; no aparecen en la busqueda normal del tecnico hasta aprobarlos.
12. Endpoint `PATCH /api/v1/error-codes/{error_code_id}/review` permite aprobar, rechazar o devolver un codigo a pendiente.
13. Endpoint `PATCH /api/v1/error-codes/{error_code_id}` permite corregir un candidato antes de aprobarlo: codigo, descripcion, modelo, severidad, causas probables, solucion sugerida, fuente, pagina y excerpt.
14. `GET /api/v1/error-codes/` y `GET /api/v1/error-codes/manufacturers` filtran por `review_status`, usando `approved` por defecto para proteger la UX mobile.
15. Tests Docker: `59 passed`.

### Pendiente de contenido

1. Probar con un manual real de codigos de error cuando este disponible.
2. Usar Swagger como flujo provisional para extraer, corregir y aprobar codigos hasta que exista un admin/backoffice.
3. Comparar resultados del extractor contra el manual fuente: codigos detectados, descripciones, paginas/excerpts y falsos positivos.
4. Mejorar el extractor con LLM o parser por fabricante si los manuales reales tienen tablas complejas.
5. Definir formato de sync offline para que el frontend movil descargue solo codigos aprobados.
6. Mantener revision humana antes de publicar codigos al tecnico.

### Archivos esperados

- `backend/app/routers/error_codes.py`
- `backend/app/services/error_code_extraction_service.py`
- `backend/scripts/seed_error_codes.py`

---

## Fase E - Frontend MVP

**Prioridad:** DESPUES DE CERRAR RAG  
**Impacto:** Llevar el backend probado a una experiencia movil usable.

### Nota

El frontend ya puede planificarse sobre el contrato oficial de casos tecnicos: lista de casos, chat activo con streaming y panel editable de metadata. Antes de implementarlo conviene decidir si Fase D de codigos de error debe ir primero o si el MVP movil puede arrancar consumiendo solo chat/RAG/usage.
