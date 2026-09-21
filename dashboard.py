import streamlit as st
import datetime
import time
import pandas as pd
import plotly.express as px
from database import executar_query
from utils import checar_rodizio
from config import apply_custom_css

def render_dashboard():
    apply_custom_css()
    col_user, col_logout = st.columns([4, 1], vertical_alignment="center")
    col_user.write(f"Olá, **{st.session_state.username}**! 🧑‍✈️")
    if col_logout.button("Sair"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
        
    st.title("Controle Semanal")

    meus_veiculos = executar_query(
        "SELECT id, modelo, km_atual, km_intervalo_oleo, km_ultima_troca_oleo, tipo_veiculo, placa FROM veiculos WHERE usuario_id = ? AND status_ativo = 1", 
        (st.session_state.user_id,)
    )
    
    if not meus_veiculos:
        st.warning("Você ainda não possui nenhum veículo cadastrado. Cadastre o seu primeiro veículo para começar.")
        st.subheader("Cadastro de Veículo")
        add_modelo = st.text_input("Modelo do Veículo (ex: Titan 160, Onix 1.0)", key="fst_modelo")
        add_tipo = st.selectbox("Tipo do Veículo:", ["Carro", "Moto", "Caminhão", "Van", "Utilitário"], key="fst_tipo")
        add_placa = st.text_input("Placa do Veículo (Opcional)", key="fst_placa")
        add_km = st.number_input("Quilometragem Atual", min_value=0, step=100, key="fst_km")
        add_intervalo = st.number_input("Intervalo para Troca de Óleo (KM)", min_value=100, value=1000, step=100, key="fst_intervalo")
        
        if st.button("Salvar Veículo e Começar"):
            if add_modelo:
                executar_query(
                    "INSERT INTO veiculos (usuario_id, modelo, tipo_veiculo, placa, km_atual, km_intervalo_oleo, km_ultima_troca_oleo, status_ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                    (st.session_state.user_id, add_modelo, add_tipo, add_placa, add_km, add_intervalo, add_km, 1)
                )

                validacao = executar_query("SELECT id FROM veiculos WHERE usuario_id = ? AND modelo = ?", (st.session_state.user_id, add_modelo))
                if validacao:
                    st.success("Veículo cadastrado com sucesso absoluto! Carregando painel...")
                    st.rerun()
                else:
                    st.error("Erro de gravação: O banco de dados rejeitou o registro do veículo.")
            else:
                st.error("Preencha o modelo do veículo!")
        st.stop()

    v_id, v_modelo, v_km_base, v_intervalo, v_ultima_troca, v_tipo, v_placa = meus_veiculos[0]

    t_max_res = executar_query("SELECT MAX(km_final) FROM turnos WHERE veiculo_id = ?", (v_id,))
    c_max_res = executar_query("SELECT MAX(km_atual) FROM combustivel WHERE veiculo_id = ?", (v_id,))
    m_max_res = executar_query("SELECT MAX(km_registro) FROM historico_manutencao WHERE veiculo_id = ?", (v_id,))
    
    t_max = t_max_res[0][0] if isinstance(t_max_res, list) and len(t_max_res) > 0 and t_max_res[0][0] is not None else 0
    c_max = c_max_res[0][0] if isinstance(c_max_res, list) and len(c_max_res) > 0 and c_max_res[0][0] is not None else 0
    m_max = m_max_res[0][0] if isinstance(m_max_res, list) and len(m_max_res) > 0 and m_max_res[0][0] is not None else 0
    
    km_atual_absoluto = max([int(v_km_base), int(t_max), int(c_max), int(m_max)])
    
    if km_atual_absoluto > int(v_km_base):
        executar_query("UPDATE veiculos SET km_atual = ? WHERE id = ?", (km_atual_absoluto, v_id))
        
    km_restantes = int(v_intervalo) - (km_atual_absoluto - int(v_ultima_troca))
    if km_restantes <= 0: 
        st.error(f"🚨 **ALERTA:** Troque o óleo **{v_modelo}**! Passou {abs(km_restantes)} KM.")
    elif km_restantes <= 100: 
        st.warning(f"⚠️ **ATENÇÃO:** Restam apenas {km_restantes} KM para a troca de óleo.")
        
    # DEFINIÇÃO DAS 5 ABAS DO APLICATIVO
    tab_turno, tab_ganhos, tab_combustivel, tab_graficos, tab_manutencao = st.tabs([
        "Turno Diário", "Lançar Ganhos", "Abastecimento", "Resumo Financeiro", "Garagem & Óleo"
    ])

    render_tab_turno(tab_turno, meus_veiculos, km_atual_absoluto)
    render_tab_ganhos(tab_ganhos)
    render_tab_combustivel(tab_combustivel, v_id, km_atual_absoluto)
    render_tab_graficos(tab_graficos)
    render_tab_manutencao(tab_manutencao, v_id, v_modelo, km_atual_absoluto, v_intervalo, v_ultima_troca, km_restantes)

def render_tab_turno(tab, meus_veiculos, km_atual_absoluto):
    apply_custom_css()
    with tab:
        st.header("Gerenciamento de Turno")
        turno_atual = executar_query("SELECT id, km_inicial, data FROM turnos WHERE usuario_id = ? AND status = 'Aberto'", (st.session_state.user_id,))
        
        if not turno_atual:
            st.info("Você não possui turnos abertos.")
            options = []
            for veiculo in meus_veiculos:
                v_id_opt, v_mod_opt, v_km_opt, _, _, v_tipo_opt, v_placa_opt = veiculo
                status_rodizio = checar_rodizio(v_tipo_opt, v_placa_opt)
                options.append(f"{v_mod_opt} (Painel: {v_km_opt} KM) - [{status_rodizio}]")
                
            veiculo_selecionado = st.selectbox("Selecione o veículo para rodar hoje:", options)
            idx_v = options.index(veiculo_selecionado)
            veiculo_id_turno = meus_veiculos[idx_v][0]
            
            km_inicial_input = st.number_input("Confirme o KM Inicial do Painel", min_value=int(km_atual_absoluto), value=int(km_atual_absoluto))
            if st.button("Iniciar Turno", type="primary"):
                executar_query("INSERT INTO turnos (usuario_id, veiculo_id, data, km_inicial, status) VALUES (?, ?, ?, ?, 'Aberto')", (st.session_state.user_id, veiculo_id_turno, str(datetime.date.today()), km_inicial_input))
                st.success("Turno iniciado!")
                st.rerun()
        else:
            t_id, t_km_inicial, t_data = turno_atual[0]
            st.warning(f"Turno em Andamento. KM Inicial: {t_km_inicial} KM.")
            km_final_input = st.number_input("Digite a KM Final ao Encerrar o Dia", min_value=int(t_km_inicial), value=None, placeholder=f"Ex: {int(t_km_inicial) + 10}")
            gasto_refeicao = st.number_input("Valor Gasto com Alimentação hoje (R$)", min_value=0.0, step=5.0, value=None, placeholder="Ex: 25.00")
            
            if st.button("Encerrar Turno", type="primary"):
                if km_final_input is None:
                    st.error("Preencha a KM Final!")
                else:
                    gasto_r = gasto_refeicao if gasto_refeicao is not None else 0.0
                    sucesso = executar_query("UPDATE turnos SET km_final = ?, gasto_alimentacao = ?, status = 'Encerrado' WHERE id = ?", (km_final_input, gasto_r, t_id))
                    if sucesso:
                        st.success("Turno encerrado e gastos salvos!")
                        st.rerun()

def render_tab_ganhos(tab):
    apply_custom_css()
    with tab:
        st.header("Lançamento de Faturamento")

        with st.form("form_ganhos", clear_on_submit=False):
            app_selecionado = st.selectbox("Selecione a Plataforma:", ["Uber", "99 APP", "iFood", "InDrive", "Lalamove", "Keeta", "Outros"])
            valor_faturado = st.number_input("Valor Bruto Ganho (R$)", min_value=0.0, step=10.0, value=None, placeholder="Ex: 150")
            km_plataforma = st.number_input("KM Registrada pelo Aplicativo (Opcional)", min_value=0.0, step=1.0, value=None, placeholder="Ex: 45")
            
            submitted = st.form_submit_button("Gravar Ganho", type="primary")
            
        if submitted:
            if valor_faturado is None or valor_faturado == 0.0:
                st.error("Preencha o valor faturado!")
            else:
                km_p = km_plataforma if km_plataforma is not None else 0.0
                sucesso = executar_query(
                    "INSERT INTO ganhos (usuario_id, data, fonte, valor_bruto, km_da_plataforma) VALUES (?, ?, ?, ?, ?)", 
                    (st.session_state.user_id, str(datetime.date.today()), app_selecionado, valor_faturado, km_p)
                )
                
                if sucesso:
                    st.success("Faturamento lançado com sucesso!")

def render_tab_combustivel(tab, v_id, km_atual_absoluto):
    apply_custom_css()
    with tab:
        st.header("Registrar Abastecimento")
        
        ultimo_posto = executar_query("SELECT km_atual FROM combustivel WHERE veiculo_id = ? ORDER BY id DESC LIMIT 1", (v_id,))
        km_base_posto = ultimo_posto[0][0] if ultimo_posto else km_atual_absoluto
        st.write(f"ℹ Base de KM sugerida: **{km_base_posto} KM**")

        with st.form(key="form_combustivel", clear_on_submit=True):
            valor_abastecido = st.number_input("Valor Pago no Posto (R$)", min_value=0.0, step=10.0)
            litros_abastecidos = st.number_input("Quantidade de Litros", min_value=0.0, step=1.0)
            km_abastecimento = st.number_input("KM Atual ao Abastecer", min_value=float(km_base_posto))

            submit_button = st.form_submit_button(label="Gravar Abastecimento", type="primary")

        if submit_button:
            if valor_abastecido <= 0 or litros_abastecidos <= 0:
                st.error("Os valores devem ser maiores que zero!")
            else:
                sucesso = executar_query(
                    "INSERT INTO combustivel (usuario_id, veiculo_id, data, valor_pago, litros, km_atual) VALUES (?, ?, ?, ?, ?, ?)", 
                    (st.session_state.user_id, v_id, str(datetime.date.today()), valor_abastecido, litros_abastecidos, km_abastecimento)
                )
                if sucesso:
                    st.success("Abastecimento registrado com sucesso!")



def render_tab_graficos(tab):
    apply_custom_css()
    with tab:
        st.header("Resumo Financeiro")
        periodo = st.radio("Visualizar dados de:", ["Hoje", "Esta Semana", "Este Mês", "Este Ano", "Todo o Período"], horizontal=True, label_visibility="collapsed")
        hoje_str = str(datetime.date.today())
        
        if periodo == "Hoje":
            sql_condicao = "AND data = ?"
            params_condicao = (st.session_state.user_id, hoje_str)
        elif periodo == "Esta Semana":
            inicio_semana = str(datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday()))
            sql_condicao = "AND data >= ?"
            params_condicao = (st.session_state.user_id, inicio_semana)
        elif periodo == "Este Mês":
            inicio_mes = str(datetime.date.today().replace(day=1))
            sql_condicao = "AND data >= ?"
            params_condicao = (st.session_state.user_id, inicio_mes)
        elif periodo == "Este Ano":
            inicio_ano = str(datetime.date.today().replace(month=1, day=1))
            sql_condicao = "AND data >= ?"
            params_condicao = (st.session_state.user_id, inicio_ano)
        else:
            sql_condicao = ""
            params_condicao = (st.session_state.user_id,)

        total_ganho_res = executar_query(f"SELECT SUM(valor_bruto) FROM ganhos WHERE usuario_id = ? {sql_condicao}", params_condicao)
        total_posto_res = executar_query(f"SELECT SUM(valor_pago) FROM combustivel WHERE usuario_id = ? {sql_condicao}", params_condicao)
        total_comida_res = executar_query(f"SELECT SUM(gasto_alimentacao) FROM turnos WHERE usuario_id = ? {sql_condicao}", params_condicao)
        
        bruto = total_ganho_res[0][0] if total_ganho_res and total_ganho_res[0][0] is not None else 0.0
        posto = total_posto_res[0][0] if total_posto_res and total_posto_res[0][0] is not None else 0.0
        comida = total_comida_res[0][0] if total_comida_res and total_comida_res[0][0] is not None else 0.0
        liquido = bruto - (posto + comida)
        
        perc_lucro = (liquido / bruto * 100) if bruto > 0 else 0.0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Faturamento Bruto", f"R$ {bruto:.2f}")
        c2.metric("Gasto Combustível", f"R$ {posto:.2f}")
        c3.metric("Gasto Alimentação", f"R$ {comida:.2f}")
        
        if liquido >= 0: c4.metric("Lucro Líquido Real", f"R$ {liquido:.2f}", delta=f"{perc_lucro:.1f}% de Lucro")
        else: c4.metric("Lucro Líquido Real", f"R$ {liquido:.2f}", delta=f"{perc_lucro:.1f}% de Prejuízo", delta_color="inverse")
        
        st.divider()
        
        col_graf_apps, col_graf_gastos = st.columns(2)
        
        with col_graf_apps:
            st.subheader("Faturamento por Aplicativo")
            dados_apps = executar_query(f"SELECT fonte, SUM(valor_bruto) FROM ganhos WHERE usuario_id = ? {sql_condicao} GROUP BY fonte", params_condicao)
            
            if dados_apps:
                df_apps = pd.DataFrame(dados_apps, columns=["Aplicativo", "Faturamento (R$)"])
                cores_apps = {
                    "Uber": "#000000",
                    "99 Moto/Carro": "#FFD100",
                    "iFood": "#EA1D2C",
                    "InDrive": "#A2F82F",
                    "Lalamove": "#F37021",
                    "Keeta": "#7BFF00",
                    "Particular / Fora de App": "#888888"
                }
                fig_bar = px.bar(df_apps, x="Aplicativo", y="Faturamento (R$)", color="Aplicativo", color_discrete_map=cores_apps, text="Faturamento (R$)")
                fig_bar.update_traces(marker_line_color='white', marker_line_width=1, textposition='outside')
                fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="", margin=dict(l=0, r=0, t=30, b=0), height=350)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Nenhum faturamento registrado para o período.")

        with col_graf_gastos:
            st.subheader("Distribuição de Gastos")
            if posto > 0 or comida > 0:
                df_gastos = pd.DataFrame({
                    "Categoria": ["Combustível", "Alimentação"],
                    "Valor (R$)": [posto, comida]
                })
                fig_pie = px.pie(df_gastos, values="Valor (R$)", names="Categoria", color="Categoria", color_discrete_map={"Combustível": "#0026fc", "Alimentação": "#00FF6A"}, hole=0.4)
                fig_pie.update_traces(textinfo='percent+label', textposition='inside')
                fig_pie.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0), height=350)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Nenhum gasto registrado para o período.")

def render_tab_manutencao(tab, v_id, v_modelo, km_atual_absoluto, v_intervalo, v_ultima_troca, km_restantes):
    apply_custom_css()
    with tab:
        st.header("Gerenciar Veículos e Trocas")
        st.write(f"📂 **Veículo:** {v_modelo} | **KM Máximo:** {km_atual_absoluto} KM")
        
        if km_restantes > 0:
            st.write(f"**Limite Alerta Óleo:** {v_intervalo} KM | **Última Troca:** {v_ultima_troca} KM | **Faltam:** {km_restantes} KM")
        else:
            st.write(f"**Limite Alerta Óleo:** {v_intervalo} KM | **Última Troca:** {v_ultima_troca} KM | **Vencido há:** {abs(km_restantes)} KM")

        st.write("---")
        st.subheader("Registrar Troca de Óleo")
    
        km_real_troca = st.number_input(
            "Informe a KM exata em que o óleo foi trocado:", 
            min_value=0, 
            value=int(km_atual_absoluto), 
            step=100, 
            key="input_km_troca_manutencao"
        )

        placeholder = st.empty()

        if st.button("Registrar Troca de Óleo", type="primary"):

            executar_query("UPDATE veiculos SET km_ultima_troca_oleo = ? WHERE id = ?", (km_real_troca, v_id))

            executar_query(
                "INSERT INTO historico_manutencao (usuario_id, veiculo_id, data, tipo_manutencao, km_registro) VALUES (?, ?, ?, 'Troca de Óleo', ?)", 
                (st.session_state.user_id, v_id, str(datetime.date.today()), km_real_troca)
            )
            
            placeholder.success(f"Contador atualizado para a KM {km_real_troca}!")

            time.sleep(1)
            st.rerun()

        st.divider()
        st.subheader("Adicionar Outro Veículo")

        with st.form(key="form_adicionar_veiculo", clear_on_submit=True):
            add_modelo = st.text_input("Modelo do Novo Veículo")
            add_tipo = st.selectbox("Tipo do Novo Veículo:", ["Carro", "Moto", "Caminhão", "Van", "Utilitário"])
            add_placa = st.text_input("Placa do Novo Veículo")
            add_km = st.number_input("KM Inicial do Painel", min_value=0)
            add_intervalo = st.number_input("Intervalo de Óleo customizado (KM)", min_value=100, value=900, step=100)
            
            submit_adicionar = st.form_submit_button("Adicionar", type="primary")

        if submit_adicionar:
            if add_modelo:
                sucesso = executar_query(
                    "INSERT INTO veiculos (usuario_id, modelo, tipo_veiculo, placa, km_atual, km_intervalo_oleo, km_ultima_troca_oleo) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (st.session_state.user_id, add_modelo, add_tipo, add_placa, add_km, add_intervalo, add_km)
                )
                if sucesso:
                    st.success("Veículo cadastrado com sucesso!")
