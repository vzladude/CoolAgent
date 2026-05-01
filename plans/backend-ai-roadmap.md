# CoolAgent - Backend AI Roadmap

**Estado actual:** Backend base funcional con Claude Haiku API, PostgreSQL/pgvector, Redis, MinIO, RAG probado end-to-end, guardrails de dominio y primera capa de usage/cache.
**Fecha de corte:** 1 de mayo de 2026
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
9. `/api/v1/usage/summary` acepta filtros por conversacion, fechas y modelo.
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
6. Reportes de costo por usuario/conversacion/modelo para tomar decisiones de precio.

### Archivos esperados

- `backend/app/services/cache_service.py`
- `backend/app/routers/usage.py`
- `backend/app/services/usage_service.py`
- `backend/app/models/usage.py`

---

## Fase C - WebSocket Streaming

**Prioridad:** MEDIA  
**Impacto:** Mejora UX del chat.

### Tareas

1. Implementar `WebSocket /api/v1/chat/stream`.
2. Conectar con `chat_stream()` del provider Claude.
3. Persistir mensajes al finalizar stream.
4. Manejar errores, reconexion y cancelacion.

### Archivos esperados

- `backend/app/routers/ws_chat.py`

---

## Fase D - Base de datos de codigos de error

**Prioridad:** MEDIA  
**Impacto:** Feature util para modo offline y diagnostico rapido.

### Estado actual

Los modelos, schemas y router base existen, pero los endpoints todavia devuelven listas vacias.

### Tareas

1. Crear seed inicial con fabricantes prioritarios: Carrier, Trane, Daikin, LG, Samsung, Copeland, Danfoss y Bitzer.
2. Implementar busqueda por codigo, fabricante y modelo.
3. Agregar endpoint de fabricantes con conteos reales.
4. Preparar estructura para sincronizacion offline futura.

### Archivos esperados

- `backend/app/routers/error_codes.py`
- `backend/scripts/seed_error_codes.py`

---

## Fase E - Frontend MVP

**Prioridad:** DESPUES DE CERRAR RAG  
**Impacto:** Llevar el backend probado a una experiencia movil usable.

### Nota

No iniciar el frontend hasta cerrar formalmente el milestone RAG con migracion, tests y commit. El frontend depende de contratos de API estables y una documentacion central alineada.
