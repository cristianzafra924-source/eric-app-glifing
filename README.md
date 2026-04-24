# App de Eric · Método Glifing

App educativa de lectura basada en el método Glifing, con seguimiento de progreso y calendario visual.

---

## Despliegue en Streamlit Community Cloud

### 1. Crear la base de datos en Supabase (gratis)

1. Ve a [supabase.com](https://supabase.com) → crea una cuenta y un proyecto nuevo.
2. En el **SQL Editor** del proyecto, ejecuta:

```sql
CREATE TABLE IF NOT EXISTS eric_progreso (
  fecha       TEXT PRIMARY KEY,
  datos       JSONB NOT NULL DEFAULT '{}',
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Permite acceso público (app de uso personal)
ALTER TABLE eric_progreso ENABLE ROW LEVEL SECURITY;
CREATE POLICY "acceso_total" ON eric_progreso FOR ALL USING (true) WITH CHECK (true);
```

3. En **Project Settings → API**, copia:
   - **Project URL** → `SUPABASE_URL`
   - **anon public key** → `SUPABASE_KEY`

### 2. Configurar los secretos en Streamlit Cloud

En [share.streamlit.io](https://share.streamlit.io), abre tu app → **Settings → Secrets** y añade:

```toml
SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIs..."
```

### 3. Publicar en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio público de GitHub.
2. En [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Selecciona el repo y pon `app.py` como fichero principal.
4. Añade los secretos del paso 2.
5. Despliega.

---

## Uso sin Supabase (solo sesión)

Si no configuras Supabase, la app funciona igualmente pero el progreso
se pierde al cerrar el navegador. El indicador en la barra lateral
muestra 🟡 cuando no hay conexión a la nube.

---

## Estructura del proyecto

```
eric_app/
├── app.py                  # Interfaz principal
├── ejercicios_glifing.py   # Motor de ejercicios
├── progreso_glifing.py     # Lógica de progreso y BD
├── requirements.txt
├── .gitignore
├── .streamlit/
│   ├── config.toml         # Tema oscuro
│   └── secrets.toml        # ← NO subir a Git
└── README.md
```
