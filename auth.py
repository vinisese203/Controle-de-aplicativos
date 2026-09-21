import streamlit as st
import re
from database import executar_query
from utils import hash_senha
from config import apply_custom_css

def render_auth():
    apply_custom_css()
    st.title("Controle de Corridas APP")
    tab_login, tab_cadastro = st.tabs(["Entrar", "Criar Conta"])
    
    with tab_login:
        user_input = st.text_input("Usuário / Login", key="login_usuario")
        pass_input = st.text_input("Senha", type="password", key="login_senha")

        
        if st.button("Entrar no Sistema", type="primary"):
            res = executar_query("SELECT id, usuario FROM usuarios WHERE usuario = ? AND senha_hash = ?", (user_input, hash_senha(pass_input)))
            if res and len(res) > 0:
                st.session_state.user_id = res[0][0]
                st.session_state.username = res[0][1]
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with tab_cadastro:
        st.subheader("Cadastro de Novo Motorista e Veículo")
        new_user = st.text_input("Escolha um Nome de Usuário", key="cadastro_usuario")
        st.markdown("<p style='color: #ff9f43; font-size: 13px; margin-top: -10px; margin-bottom: 15px;'>⚠️ ATENÇÃO: Apenas com letras minúsculas e sem espaços.</p>", unsafe_allow_html=True)
        
        new_pass = st.text_input("Escolha uma Senha Segura", type="password", key="cadastro_senha")
        confirm_pass = st.text_input("Confirme a sua Senha", type="password", key="cadastro_confirmar_senha")
        
        atende_tamanho = len(new_pass) >= 8
        atende_maiuscula = any(c.isupper() for c in new_pass)
        atende_especial = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', new_pass))
        atende_numero = any(c.isdigit() for c in new_pass)
        
        if len(new_pass) == 0: cor_tamanho = cor_maiuscula = cor_especial = cor_numero = "gray"
        else:
            cor_tamanho = "green" if atende_tamanho else "red"
            cor_maiuscula = "green" if atende_maiuscula else "red"
            cor_especial = "green" if atende_especial else "red"
            cor_numero = "green" if atende_numero else "red"
        
        st.markdown(
            f"""
            <div style='font-size: 14px; margin-top: -5px; margin-bottom: 15px;'>
                <p style='margin: 4px 0;'><span style='color: {cor_tamanho}; font-weight: bold;'>{'●' if atende_tamanho else '○'}</span> <span style='color: #e0e0e0;'>Ter no mínimo 8 caracteres</span></p>
                <p style='margin: 4px 0;'><span style='color: {cor_maiuscula}; font-weight: bold;'>{'●' if atende_maiuscula else '○'}</span> <span style='color: #e0e0e0;'>Ter uma letra maiúscula</span></p>
                <p style='margin: 4px 0;'><span style='color: {cor_numero}; font-weight: bold;'>{'●' if atende_numero else '○'}</span> <span style='color: #e0e0e0;'>Ter pelo menos um número</span></p>
                <p style='margin: 4px 0;'><span style='color: {cor_especial}; font-weight: bold;'>{'●' if atende_especial else '○'}</span> <span style='color: #e0e0e0;'>Ter um caractere especial (!@#$%^&*...)</span></p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        if len(confirm_pass) > 0 and new_pass != confirm_pass: st.error("❌ As senhas estão diferentes.")
        
        st.divider()
        st.write("📋 Cadastro do Primeiro Veículo:")
        modelo_v = st.text_input("Modelo do Veículo (ex: Titan 160, Onix 1.0)")
        tipo_v = st.selectbox("Tipo do Veículo:", ["Carro", "Moto", "Caminhão", "Van", "Utilitário"])
        placa_v = st.text_input("Placa do Veículo (Opcional)")
        km_atual_v = st.number_input("Quilometragem Atual", min_value=0, step=100)
        intervalo_o = st.number_input("Intervalo para Troca de Óleo (KM)", min_value=100, value=1000, step=100)
        
        if st.button("Finalizar"):
            tem_espaco = " " in new_user
            tem_maiuscula = any(c.isupper() for c in new_user)
            
            if not new_user or not new_pass or not confirm_pass or not modelo_v: 
                st.error("Preencha todos os campos obrigatórios!")
            elif tem_espaco or tem_maiuscula:
                st.error("❌ Erro de Formato: O nome de usuário não pode conter espaços nem letras maiúsculas!")
            elif new_pass != confirm_pass: 
                st.error("As senhas não coincidem!")
            elif not (atende_tamanho and atende_maiuscula and atende_especial and atende_numero): 
                st.error("A sua senha não atende a todos os requisitos de segurança!")
            else:
                criou_usuario = executar_query("INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)", (new_user, hash_senha(new_pass)))
                
                if criou_usuario:
                    busca_id = executar_query("SELECT id FROM usuarios WHERE usuario = ?", (new_user,))
                    if isinstance(busca_id, list) and len(busca_id) > 0:
                        u_id_puro = busca_id[0][0]
                        criou_veiculo = executar_query(
                            "INSERT INTO veiculos (usuario_id, modelo, tipo_veiculo, placa, km_atual, km_intervalo_oleo, km_ultima_troca_oleo) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                            (u_id_puro, modelo_v, tipo_v, placa_v, km_atual_v, intervalo_o, km_atual_v)
                        )
                        if criou_veiculo:
                            st.success("Conta e veículo criados com sucesso.")
                    else:
                        st.error("Erro crítico de sincronização: Não foi possível pescar o índice numérico do usuário.")

