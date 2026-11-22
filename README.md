# Software FJ — Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto de la **Fase 4 – Prácticas simuladas** del curso **Programación (213023)**,
Universidad Nacional Abierta y a Distancia (UNAD), programa de Ingeniería de Sistemas.

Aplicación en **Python** orientada a objetos, **sin base de datos**, que gestiona clientes,
servicios y reservas de la empresa ficticia *Software FJ*. Demuestra abstracción, herencia,
polimorfismo, encapsulación y **manejo avanzado de excepciones**, con registro de eventos
y errores en un archivo de logs. La aplicación nunca se detiene ante un error.

## Requisitos

- Python 3.10 o superior (solo biblioteca estándar).

## Ejecución

```bash
python main.py              # 29 simulaciones válidas e inválidas; genera logs/software_fj.log
python -m unittest -v       # 16 pruebas unitarias
```

## Estructura

```
software_fj/
├── main.py                  # simulación de 29 operaciones
├── software_fj/
│   ├── excepciones.py       # jerarquía de excepciones personalizadas
│   ├── registro.py          # configuración del archivo de logs
│   ├── base.py              # clase abstracta EntidadBase
│   ├── cliente.py           # Cliente (datos encapsulados y validados)
│   ├── servicios.py         # ServicioBase (abstracta) + 3 servicios
│   ├── reserva.py           # Reserva y EstadoReserva
│   └── gestor.py            # SistemaGestion (listas internas + ejecución segura)
├── tests/test_sistema.py    # pruebas unitarias
├── docs/                    # evidencias: salida de consola y log de ejemplo
└── logs/                    # archivo de logs (se genera al ejecutar)
```

## Diseño orientado a objetos

| Clase | Tipo | Rol |
|---|---|---|
| `EntidadBase` | Abstracta | Id, fecha de creación y `describir()` para todas las entidades |
| `Cliente` | Concreta | Nombre, documento, correo y teléfono con validación en cada asignación |
| `ServicioBase` | Abstracta | Tarifa, disponibilidad, `validar_parametros`, `_costo_base`, `describir` |
| `SalaReserva` | Servicio | Capacidad, proyector opcional, límite de 8 h |
| `AlquilerEquipo` | Servicio | Cobro por unidades y horas, límite de 72 h |
| `AsesoriaEspecializada` | Servicio | Nivel junior/senior, modalidad virtual/presencial |
| `Reserva` | Concreta | Integra cliente, servicio, duración y estado; confirma, cancela y procesa |
| `SistemaGestion` | Concreta | Listas internas y `ejecutar()` que protege cada operación |

- **Polimorfismo:** cada servicio sobrescribe `describir`, `validar_parametros` y `_costo_base`.
- **Sobrecarga:** `calcular_costo(horas)`, `calcular_costo(horas, impuesto)`,
  `calcular_costo(horas, impuesto, descuento)` y las variantes `costo_sin_impuesto` y
  `costo_con_descuento`.
- **Encapsulación:** atributos protegidos con propiedades de solo lectura o con validación.

## Manejo de excepciones

- **Excepciones personalizadas** (`ErrorSoftwareFJ` y 12 subclases) con código (`SFJ-xxx`).
- **try/except** por tipo de error en validaciones y búsquedas.
- **try/except/else/finally** en `Reserva.procesar()` y en `SistemaGestion.ejecutar()`.
- **Encadenamiento:** `raise ReservaInvalidaError(...) from error` conserva la causa original.
- **Errores inesperados** (por ejemplo `ZeroDivisionError`) se envuelven en `ErrorInesperadoError`,
  se registran con traza completa y el sistema continúa.

## Logs

`logs/software_fj.log` registra cada operación (INFO), cada error controlado (ERROR), los errores
inesperados con traza (CRITICAL) y el cierre de cada operación (DEBUG). Un ejemplo real está en
`docs/software_fj_ejemplo.log`.

## Organización del trabajo en Git

El proyecto fue desarrollado de forma individual, pero se organizó con un flujo profesional:

1. Una rama por módulo: `feature/<módulo>`, creada desde `main`.
2. Commits pequeños y descriptivos (`feat:`, `docs:`, `test:`, `chore:`).
3. Un *issue* por cada módulo y un Pull Request hacia `main` que lo cierra (`Closes #N`).

| Rama | Contenido | Issue |
|---|---|---|
| `feature/excepciones-logging` | Excepciones personalizadas y archivo de logs | #1 |
| `feature/entidades-cliente` | Clase abstracta EntidadBase y Cliente | #2 |
| `feature/servicios` | ServicioBase y los tres servicios, sobrecarga de costos | #3 |
| `feature/reservas-gestor` | Reserva, estados y SistemaGestion | #4 |
| `feature/pruebas-docs` | main.py, pruebas unitarias, README y evidencias | #5 |

## Autor

_Nombre del estudiante_ — Programación (213023), UNAD.
