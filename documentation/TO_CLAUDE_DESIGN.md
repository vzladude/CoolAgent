# TO_CLAUDE_DESIGN - CoolAgent Mobile MVP Screens

## Objetivo de este briefing

Este documento es para Claude Design y debe usarse como mapa de pantallas del MVP mobile de CoolAgent.

No reemplaza el design system visual que ya fue creado. El objetivo es corregir el alcance: CoolAgent no es solo chat. CoolAgent es una app movil de herramientas para tecnicos de refrigeracion general.

## Reglas importantes para Claude Design

1. CoolAgent es una app movil para tecnicos de refrigeracion general: neveras, congeladores, aires acondicionados residenciales/comerciales, refrigeracion comercial e industrial, camaras frigorificas, chillers, bombas de calor, refrigerantes, electricidad aplicada, controles, mantenimiento y diagnostico.
2. El chat es una utilidad, no toda la app.
3. El MVP mobile debe sentirse como una caja de herramientas tecnica, no como una app generica de chat AI.
4. RAG upload no ocurre desde mobile.
5. La ingesta de PDFs, manuales y documentos RAG se administra fuera del MVP mobile, probablemente desde admin/backoffice en una fase futura.
6. La app movil puede mostrar fuentes usadas por RAG, pero no debe disenar un flujo para subir manuales, administrar chunks o gestionar embeddings.
7. Disenar para tecnico de campo: rapido, escaneable, usable con una mano, legible en ambientes de trabajo y con estados claros cuando hay poca conexion.
8. Evitar pantallas de marketing. La primera experiencia debe ser utilitaria y directa.

## Navegacion MVP recomendada

Usar navegacion principal simple, idealmente tabs o bottom navigation:

- Home
- Casos
- Herramientas
- Codigos
- Ajustes

Notas:

- "Casos" contiene el chat por caso tecnico.
- "Herramientas" agrupa diagnostico por imagen, calculadoras y guias/procedimientos.
- "Codigos" es la base de codigos de error.
- "Ajustes" contiene preferencias y estado de la app.

---

# 1. App Shell y Navegacion

## 1.1 Splash / Loading

Proposito:

- Mostrar inicio de CoolAgent mientras carga estado local, sesion futura, conectividad y datos offline.

Debe incluir:

- Marca CoolAgent.
- Estado breve de carga.
- Variante offline si no hay conexion.

## 1.2 Home / Tool Hub

Proposito:

- Ser la entrada principal a las herramientas del tecnico.
- No debe parecer una landing page.

Debe incluir accesos a:

- Nuevo caso tecnico.
- Continuar caso reciente.
- Diagnostico por imagen.
- Codigos de error.
- Calculadoras.
- Guias/procedimientos.
- Estado offline/sync si aplica.

## 1.3 Empty State Inicial Sin Casos

Proposito:

- Mostrar estado inicial cuando el tecnico todavia no ha creado casos.

Debe incluir:

- CTA para crear primer caso tecnico.
- Accesos alternativos a diagnostico por imagen, codigos y calculadoras.

## 1.4 Offline / Poor Connection State

Proposito:

- Comunicar claramente que algunas funciones AI pueden no estar disponibles.

Debe incluir:

- Estado de conexion.
- Que sigue disponible offline: calculadoras, guias descargadas, codigos sincronizados si existen.
- Que requiere conexion: chat con Claude, diagnostico AI, sync.

## 1.5 Settings Basico

Proposito:

- Acceso rapido a preferencias y estado tecnico de la app.

Debe incluir:

- Idioma.
- Unidades.
- Tema claro/oscuro si aplica.
- Estado de conexion.
- Version de app.
- Ayuda/soporte.

---

# 2. Casos Tecnicos + Chat

Importante:

- El chat vive dentro de un caso tecnico.
- Un caso tecnico representa un equipo, falla o trabajo especifico.
- No disenar un chat central infinito como experiencia principal.

## 2.1 Lista de Casos Tecnicos

Proposito:

- Ver y retomar trabajos/fallas activos.

Debe incluir:

- Lista de casos con titulo.
- Fabricante, modelo o categoria si existen.
- Estado: abierto/cerrado.
- Ultimo mensaje o ultima actividad.
- Boton para crear caso nuevo.
- Filtro simple por estado o busqueda.

## 2.2 Crear Nuevo Caso Tecnico

Proposito:

- Crear un contenedor para una falla/equipo antes o durante el chat.

Debe incluir:

- Titulo opcional.
- Fabricante opcional.
- Modelo opcional.
- Categoria opcional.
- Boton "Empezar chat" o "Crear caso".

Nota:

- No obligar al tecnico a llenar todo antes de chatear.
- El caso puede generarse con el primer mensaje.

## 2.3 Chat Activo Dentro de un Caso

Proposito:

- Asistencia tecnica conversacional para refrigeracion general.

Debe incluir:

- Header con titulo del caso.
- Acceso al panel de metadata del caso.
- Historial de mensajes.
- Input de mensaje.
- Estado de respuesta streaming.
- Indicador de fuentes RAG cuando existan.
- Accion para cerrar caso.

## 2.4 Panel / Drawer de Metadata del Caso

Proposito:

- Editar datos del caso sin salir del chat.

Debe incluir:

- Fabricante.
- Modelo.
- Categoria.
- Estado abierto/cerrado.
- Resumen corto si existe.
- Ultima actualizacion.

## 2.5 Historial de Mensajes del Caso

Proposito:

- Mostrar mensajes anteriores de forma paginada o cargable.

Debe incluir:

- Mensajes recientes.
- Carga de mensajes anteriores.
- Diferenciacion clara entre tecnico y CoolAgent.

## 2.6 Sheet / Modal de Fuentes Usadas por RAG

Proposito:

- Mostrar al tecnico de donde salio la informacion tecnica usada por el chat.

Debe incluir:

- Titulo del documento.
- Fuente.
- Fabricante/modelo/categoria si existen.
- Fecha o metadata disponible.

Importante:

- Esta pantalla solo muestra fuentes.
- No debe permitir subir PDFs/manuales.

## 2.7 Empty State de Caso Sin Mensajes

Proposito:

- Ayudar al tecnico a empezar.

Debe incluir prompts sugeridos:

- "Mi nevera no enfria, que reviso primero?"
- "Que significa este codigo de error?"
- "Como diagnostico baja presion de succion?"
- "Que reviso en un split que congela la tuberia?"

## 2.8 Estado de Respuesta Streaming

Proposito:

- Mostrar que CoolAgent esta respondiendo en tiempo real.

Debe incluir:

- Indicador de generacion.
- Texto apareciendo progresivamente.
- Estado de error si falla la conexion.

## 2.9 Estado de Bloqueo por Fuera de Dominio

Proposito:

- Mostrar rechazo breve cuando la pregunta no pertenece a refrigeracion/climatizacion.

Debe incluir:

- Mensaje claro: CoolAgent solo ayuda con refrigeracion/climatizacion.
- Sugerencia para reformular como consulta tecnica del area.

---

# 3. Diagnostico Por Imagen

## 3.1 Capturar / Subir Imagen

Proposito:

- Permitir al tecnico tomar foto o seleccionar imagen de un equipo/falla.

Debe incluir:

- Camara.
- Galeria.
- Guia visual minima para tomar una foto util.

## 3.2 Preview de Imagen Antes de Analizar

Proposito:

- Confirmar que la imagen es correcta antes de enviar a diagnostico AI.

Debe incluir:

- Imagen seleccionada.
- Cambiar imagen.
- Continuar al formulario de contexto.

## 3.3 Formulario Corto de Contexto

Proposito:

- Dar contexto tecnico al analisis visual.

Debe incluir:

- Tipo de equipo.
- Sintoma.
- Fabricante opcional.
- Modelo opcional.
- Notas opcionales.

## 3.4 Loading / Analyzing State

Proposito:

- Mostrar que la imagen se esta analizando.

Debe incluir:

- Estado de carga.
- Mensaje de seguridad: no manipular equipo energizado si hay riesgo.

## 3.5 Resultado de Diagnostico Visual

Proposito:

- Presentar el analisis de la imagen.

Debe incluir:

- Observaciones visibles.
- Posibles problemas.
- Nivel de confianza si aplica.
- Advertencias de seguridad.
- Acciones recomendadas.

## 3.6 Suggested Next Steps

Proposito:

- Convertir diagnostico en acciones practicas.

Debe incluir:

- Lista ordenada de pasos.
- Herramientas o mediciones sugeridas.
- EPP cuando aplique.

## 3.7 Suggested Related Error Codes

Proposito:

- Conectar diagnostico visual con la base de codigos.

Debe incluir:

- Codigos relacionados si existen.
- Fabricante/modelo si aplica.
- CTA para abrir detalle del codigo.

## 3.8 Historial de Diagnosticos

Proposito:

- Retomar analisis anteriores.

Debe incluir:

- Miniatura de imagen.
- Fecha.
- Equipo/sintoma.
- Estado o resumen.

## 3.9 Detalle de Diagnostico Anterior

Proposito:

- Consultar un analisis guardado.

Debe incluir:

- Imagen.
- Resultado.
- Pasos sugeridos.
- Codigos relacionados.
- Caso tecnico asociado si existe.

---

# 4. Codigos de Error

## 4.1 Busqueda de Codigo de Error

Proposito:

- Buscar codigos por texto/codigo.

Debe incluir:

- Search input.
- Filtros rapidos.
- Estado sin resultados.

## 4.2 Filtros por Fabricante / Modelo

Proposito:

- Refinar busqueda para evitar codigos ambiguos.

Debe incluir:

- Selector de fabricante.
- Campo o selector de modelo.
- Limpiar filtros.

## 4.3 Lista de Resultados

Proposito:

- Mostrar codigos coincidentes.

Debe incluir:

- Codigo.
- Fabricante.
- Modelo si existe.
- Descripcion corta.
- Severidad.

## 4.4 Detalle de Codigo

Proposito:

- Mostrar informacion accionable del codigo.

Debe incluir:

- Codigo.
- Fabricante.
- Modelo.
- Descripcion.
- Severidad.
- Causas probables.
- Solucion sugerida.
- Fuente.
- CTA para crear caso tecnico desde este codigo.

## 4.5 Lista de Fabricantes con Conteos

Proposito:

- Navegar catalogo por fabricante.

Debe incluir:

- Nombre del fabricante.
- Conteo de modelos.
- Conteo de codigos.
- Estado si aun no hay codigos cargados.

## 4.6 Empty State Sin Resultados

Proposito:

- Explicar que no hay coincidencias.

Debe incluir:

- Mensaje claro.
- Sugerencia para quitar filtros o buscar por fabricante/modelo.

## 4.7 Estado "Catalogo Aun Sin Codigos Cargados"

Proposito:

- Reflejar el estado actual del producto si solo hay fabricantes seed.

Debe incluir:

- Mensaje honesto: el catalogo esta preparado, pero los codigos se cargaran desde manuales confiables.
- Acceso a chat/caso tecnico como alternativa.

---

# 5. Calculadoras Tecnicas

Las calculadoras deben funcionar offline siempre que sea posible.

## 5.1 Hub de Calculadoras

Proposito:

- Agrupar herramientas de calculo.

Debe incluir:

- Superheat.
- Subcooling.
- PT chart / refrigerant lookup.
- Conversor de unidades.

## 5.2 Superheat Calculator

Proposito:

- Calcular sobrecalentamiento.

Debe incluir:

- Refrigerante.
- Presion de succion.
- Temperatura de linea de succion.
- Resultado.
- Interpretacion corta.

## 5.3 Subcooling Calculator

Proposito:

- Calcular subenfriamiento.

Debe incluir:

- Refrigerante.
- Presion de liquido.
- Temperatura de linea de liquido.
- Resultado.
- Interpretacion corta.

## 5.4 PT Chart / Refrigerant Lookup

Proposito:

- Consultar relacion presion-temperatura por refrigerante.

Debe incluir:

- Selector de refrigerante.
- Entrada por presion o temperatura.
- Resultado equivalente.

## 5.5 Conversor Basico de Unidades Tecnicas

Proposito:

- Convertir unidades usadas por tecnicos.

Debe incluir:

- PSI / bar / kPa.
- Fahrenheit / Celsius.
- Micrones / Torr si aplica.

## 5.6 Resultado de Calculo con Interpretacion Corta

Proposito:

- No solo mostrar numero; ayudar a entenderlo.

Debe incluir:

- Valor calculado.
- Rango esperado si aplica.
- Advertencia: confirmar contra especificacion del fabricante.

## 5.7 Estado Offline Disponible

Proposito:

- Mostrar que la calculadora funciona sin internet.

Debe incluir:

- Badge o indicador offline-ready.

---

# 6. Guias / Procedimientos

## 6.1 Biblioteca de Guias

Proposito:

- Listar procedimientos tecnicos.

Debe incluir:

- Busqueda.
- Categorias.
- Estado descargado/offline.

## 6.2 Categorias de Guias

Categorias iniciales:

- Diagnostico.
- Mantenimiento.
- Seguridad.
- Herramientas.

## 6.3 Detalle de Guia Paso a Paso

Proposito:

- Seguir un procedimiento en campo.

Debe incluir:

- Titulo.
- Resumen.
- Pasos numerados.
- Advertencias de seguridad.

## 6.4 Checklist de Procedimiento

Proposito:

- Marcar pasos completados.

Debe incluir:

- Checkboxes.
- Progreso.
- Reiniciar checklist.

## 6.5 Materiales / Herramientas / EPP

Proposito:

- Preparar al tecnico antes de ejecutar.

Debe incluir:

- Herramientas necesarias.
- Repuestos o materiales.
- EPP requerido.

## 6.6 Guardar Guia para Offline

Proposito:

- Permitir uso sin conexion.

Debe incluir:

- CTA guardar offline.
- Estado descargado.
- Ultima actualizacion.

## 6.7 Estado "Contenido Pendiente"

Proposito:

- Manejar categorias aun sin guias.

Debe incluir:

- Mensaje claro.
- CTA para usar chat/caso tecnico mientras se carga contenido.

---

# 7. Offline / Sync

## 7.1 Estado Offline Global

Proposito:

- Mostrar conectividad y limitar expectativas.

Debe incluir:

- Online.
- Offline.
- Poor connection.
- Ultima sincronizacion.

## 7.2 Datos Disponibles Offline

Proposito:

- Ver que contenido puede usarse sin internet.

Debe incluir:

- Calculadoras.
- Guias descargadas.
- Codigos sincronizados si existen.
- Casos recientes si aplica.

## 7.3 Sync Status

Proposito:

- Mostrar si la app esta actualizada.

Debe incluir:

- Ultima sincronizacion.
- Estado: actualizado, pendiente, error.

## 7.4 Queue de Acciones Pendientes

Proposito:

- Mostrar acciones hechas offline que esperan sincronizacion.

Debe incluir:

- Tipo de accion.
- Fecha.
- Estado.

## 7.5 Error de Sincronizacion

Proposito:

- Explicar cuando algo no pudo sincronizar.

Debe incluir:

- Mensaje claro.
- Retry.
- Detalle tecnico opcional.

## 7.6 Ultima Sincronizacion

Proposito:

- Dar confianza al tecnico sobre frescura de datos.

Debe incluir:

- Fecha/hora.
- Tipo de datos sincronizados.

---

# 8. Ajustes

## 8.1 Perfil Basico / Local

Proposito:

- Preparar espacio para usuario futuro sin obligar auth ahora.

Debe incluir:

- Nombre/local alias si aplica.
- Rol tecnico.
- Empresa opcional en futuro.

## 8.2 Preferencias

Debe incluir:

- Idioma.
- Unidades.
- Tema claro/oscuro si aplica.

## 8.3 Estado de Conexion

Debe incluir:

- Online/offline.
- API reachable.
- Ultima sync.

## 8.4 Informacion de Version

Debe incluir:

- Version app.
- Version backend/API si aplica.
- Build number si aplica.

## 8.5 Ayuda / Soporte

Debe incluir:

- Contacto soporte.
- Reportar problema.
- FAQ futura.

## 8.6 Aviso de Seguridad Tecnica

Debe incluir:

- CoolAgent ayuda al diagnostico, pero no reemplaza criterio tecnico certificado.
- Verificar energia, presiones, refrigerantes y EPP antes de intervenir equipos.

---

# Explicitly Out Of Mobile MVP

Estas pantallas no son parte de la app movil MVP:

- Upload de PDFs/manuales para RAG.
- Ingesta de documentos RAG.
- Gestion de chunks/embeddings.
- Panel admin de documentos.
- Gestion de usuarios/clientes.
- Monetizacion, planes, billing.
- Rate limits/cuotas por usuario.
- Dashboard administrativo de costos.

Estas pantallas pueden existir en el futuro como admin/backoffice, pero no deben aparecer como flujo principal del tecnico movil.

## Nota especifica sobre RAG

RAG es una capacidad del backend que mejora respuestas del chat con documentacion tecnica. En el MVP mobile:

- El tecnico puede ver fuentes usadas por RAG.
- El tecnico no sube PDFs/manuales.
- El tecnico no administra la knowledge base.
- El tecnico no ve chunks, embeddings ni procesos internos de ingesta.

---

# Checklist para Claude Design

Antes de terminar el diseno, confirmar:

- La app no parece solo un chat.
- Home muestra varias herramientas tecnicas.
- Casos/chat es una seccion importante, pero no la unica.
- Diagnostico por imagen tiene flujo completo.
- Codigos de error tiene busqueda, filtros, detalle y estados vacios.
- Calculadoras tecnicas tienen screens propias.
- Guias/procedimientos y offline estan representados.
- Ajustes existe como seccion basica.
- No hay pantalla movil para subir PDFs/manuales RAG.
- No hay pantalla movil para administrar chunks/embeddings.
