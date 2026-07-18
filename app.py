
            idx += 1
            
    st.subheader("📍UBICACIONES EN TIEMPO REAL")
    st.components.v1.html("""
        <div id="map-container-general" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
            <button onclick="toggleFS('map-container-general')" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                ⛶ Pantalla Completa
            </button>
            <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0" allowfullscreen="true" allow="fullscreen"></iframe>
        </div>
        <script>
            function toggleFS(id) { 
                var elem = document.getElementById(id); 
                if (!document.fullscreenElement) { 
                    elem.requestFullscreen().catch(err => alert("Error: " + err.message)); 
                } else { 
                    document.exitFullscreen(); 
                } 
            }
        </script>
    """, height=510)

elif seleccion == "Inmunización":
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str).fillna("0")
        cols_vacunas = ["TOXOIDE", "FIEBRE AMARILLA", "S.R.P", "BOPB", "BCG", "PENTAVALENTE", "HEP B", "IPV"]
        c_vac = st.columns(4)
        for i, v in enumerate(cols_vacunas):
            sum_val = pd.to_numeric(df_detalle[v].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0).sum() if v in df_detalle.columns else 0
            valor_formateado = f"{int(sum_val):,}".replace(",", ".")
            c_vac[i % 4].markdown(f'''
                <div class="strat-card" style="padding: 10px 5px;">
                    <div class="strat-title" style="font-size: 11px;">{v}</div>
                    <div class="strat-value" style="font-size: 18px;">{valor_formateado}</div>
                </div>
            ''', unsafe_allow_html=True)
        total_general = sum([pd.to_numeric(df_detalle[v].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0).sum() for v in cols_vacunas if v in df_detalle.columns])
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown(f'''
                <div class="total-card">
                    <div class="total-title">TOTAL GENERAL</div>
                    <div class="total-value">{f"{int(total_general):,}".replace(",", ".")}</div>
                </div>
            ''', unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)
        df_mostrar = df_detalle.copy()
        for col in (cols_vacunas + ["TOTAL"]):
            if col in df_mostrar.columns:
                df_mostrar[col] = pd.to_numeric(df_mostrar[col].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0).astype(int)
                df_mostrar[col] = df_mostrar[col].apply(lambda x: f"{x:,}".replace(",", "."))
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif seleccion == "Saneamiento Ambiental":
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str).fillna("0")
        iconos = {"DESRATIZACIÓN": "🐀", "FUMIGACIÓN": "💨", "DESINFECCIÓN": "🪣", "ABATIZACIÓN": "💧", "DESPARASITACIÓN": "💊", "PERSONAS PROTEGIDAS": "🛡️"}
        campos = ["DESRATIZACIÓN", "FUMIGACIÓN", "DESINFECCIÓN", "ABATIZACIÓN", "DESPARASITACIÓN", "PERSONAS PROTEGIDAS"]
        c_sane = st.columns(3)
        for i, campo in enumerate(campos):
            val = df_detalle[campo].iloc[0] if campo in df_detalle.columns else "0"
            c_sane[i % 3].markdown(f'''
                <div class="strat-card" style="padding: 15px 5px;">
                    <div class="strat-title" style="font-size: 13px;">{iconos.get(campo, "📊")} {campo}</div>
                    <div class="strat-value" style="font-size: 22px; margin-top: 5px;">{val}</div>
                </div>
            ''', unsafe_allow_html=True)
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif seleccion == "Ruta Epidemiológica":
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str)
        st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    st.markdown("### 📍UBICACIÓN DEL PACIENTE")
    st.components.v1.html("""<div id="map-container-ruta" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
        <button onclick="toggleFS('map-container-ruta')" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
            ⛶ Pantalla Completa
        </button>
        <iframe src="https://www.google.com/maps/d/embed?mid=1yl45t_HdDytdAAzsaOcMJzM3ICa5bPk" width="100%" height="100%" frameborder="0" allowfullscreen="true" allow="fullscreen"></iframe>
    </div>
    <script>
        function toggleFS(id) { 
            var elem = document.getElementById(id); 
            if (!document.fullscreenElement) { 
                elem.requestFullscreen().catch(err => alert("Error: " + err.message)); 
            } else { 
                document.exitFullscreen(); 
            } 
        }
    </script>""", height=510)

else:
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str)
        df_detalle = df_detalle.replace('None', pd.NA).dropna(how='all')
        if seleccion == "Campamentos Transitorios": orden = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS"]
        else: orden = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "NACIONALIAD", "PAIS RESPONSABLE", "ATENCIONES"]
        df_detalle = df_detalle.reindex(columns=orden)
        
        if seleccion == "Hospitales de Campaña" and "NACIONALIAD" in df_detalle.columns and "ATENCIONES" in df_detalle.columns:
            df_stats = df_detalle.copy()
            df_stats['ATENCIONES'] = pd.to_numeric(df_stats['ATENCIONES'].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            df_stats['NACIONALIAD'] = df_stats['NACIONALIAD'].astype(str).str.upper().str.strip()
            resumen = df_stats.groupby('NACIONALIAD')['ATENCIONES'].sum()
            suma_nac = resumen.get('NACIONAL', 0)
            suma_ext = resumen.get('EXTRANJERO', 0) + resumen.get('ESTRANJERO', 0)
            cols = st.columns(2)
            cols[0].metric("Total Atenciones NACIONALES", f"{int(suma_nac):,}".replace(",", "."))
            cols[1].metric("Total Atenciones EXTRANJEROS", f"{int(suma_ext):,}".replace(",", "."))
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
            if (suma_nac + suma_ext) > 0:
                fig = go.Figure(data=[go.Pie(labels=['NACIONAL', 'EXTRANJERO'], values=[suma_nac, suma_ext], hole=.6, marker_colors=['#FF0000', '#002060'], textinfo='none')])
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), margin=dict(t=20, b=80, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
