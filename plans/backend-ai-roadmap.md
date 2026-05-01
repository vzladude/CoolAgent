# CoolAgent - Backend AI Roadmap

**Estado actual:** Backend base funcional con Claude Haiku API, PostgreSQL/pgvector, Redis, MinIO y RAG probado end-to-end.
**Fecha de corte:** 30 de abril de 2026
**Uso de esta carpeta:** `plans/` contiene planes temporales de la tarea activa. La fuente central de verdad vive en `documentation/CoolAgent_Documentacion_Maestra.docx`.
**Nota:** No se planea pasar a staging/produccion pronto. Alembic se agrega ahora para que ese futuro paso sea mas simple y seguro.

---

## Fase A - RAG Pipeline - EN CIERRE

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

### Pendiente para cerrar formalmente el milestone

1. Ejecutar y mantener en verde la suite de tests unitarios e integracion.
2. Revisar cambios sin trackear relacionados al RAG.
3. Hacer commit del backend RAG como hito estable.

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

### Tareas

1. Cache de respuestas identicas o semanticamente similares con TTL.
2. Tracking de tokens por respuesta, modelo y conversacion.
3. Endpoint de uso/costos para monitoreo.
4. Politica clara de invalidacion cuando cambie la knowledge base.

### Archivos esperados

- `backend/app/services/cache_service.py`
- `backend/app/routers/usage.py`

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
