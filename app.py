import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime as dt
from streamlit_option_menu import option_menu
import time
import plotly.express as px

# --- CONFIGURAÇÕES DE ACESSO ---
SUPABASE_URL = "https://ydsrakqqnljbnsfoavhb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkc3Jha3FxbmxqYm5zZm9hdmhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5MDk4MjQsImV4cCI6MjA4MzQ4NTgyNH0.du454d_ZrTByEIVbIfQHNg1z6u4XfHvRhfyJwHz--Ug"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gerenciador VIP",
    layout="wide",
    page_icon="💜"
)

# --- TABELA DE PREÇOS ---
TABELA_SERVICOS = {
    "Unha de Fibra: Aplicação": 100.0, "Unha de Fibra: Manutenção": 80.0,
    "Unha de Gel: Aplicação": 90.0, "Unha de Gel: Manutenção": 80.0,
    "Banho de Gel: Aplicação": 60.0, "Banho de Gel: Manutenção": 50.0,
    "Adicional: Encapsulada": 10.0, "Remoção": 40.0, "Outros": 0.0
}

# --- CSS DARK ROXO (BLINDADO) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

/* 1. Background Geral */
[data-testid="stAppViewContainer"] { background-color: #1a0b2e !important; }
[data-testid="stSidebar"] { background-color: #2d1b4e !important; border-right: 1px solid #432c7a; }
[data-testid="stHeader"] { background-color: #1a0b2e !important; }

/* 2. Tipografia (Apenas textos, protegendo ícones) */
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span, div {
    font-family: 'Montserrat', sans-serif;
    color: #e0d4fc !important;
}
h1, h2, h3 { color: #d05ce3 !important; font-weight: 700 !important; }

/* 3. Inputs e Caixas de Texto */
.stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea {
    background-color: #2d1b4e !important;
    color: #ffffff !important;
    border: 1px solid #5b3a95 !important;
    border-radius: 8px !important;
}

/* 4. Selectbox (Menu Dropdown) */
div[data-baseweb="select"] > div {
    background-color: #2d1b4e !important;
    border: 1px solid #5b3a95 !important;
    color: white !important;
}
div[data-baseweb="popover"] { background-color: #2d1b4e !important; }
div[data-baseweb="select"] span { color: white !important; }

/* 5. Botões Neon */
.stButton > button {
    border-radius: 12px !important;
    background: linear-gradient(90deg, #9c27b0, #673ab7) !important;
    color: white !important;
    font-weight: bold !important;
    border: 1px solid #d05ce3 !important;
    box-shadow: 0px 0px 10px rgba(156, 39, 176, 0.5) !important;
    transition: transform 0.2s;
}
.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0px 0px 15px #d05ce3 !important;
}

/* 6. Cards / Expanders */
div[data-testid="stExpander"] {
    border: 1px solid #5b3a95 !important;
    background-color: #241240 !important;
    border-radius: 15px !important;
}
div[data-testid="stExpander"] summary svg { color: #d05ce3 !important; fill: #d05ce3 !important; }

/* 7. Métricas */
div[data-testid="stMetric"] {
    background-color: #241240 !important;
    border: 1px solid #5b3a95 !important;
    border-radius: 12px !important;
    padding: 10px !important;
}
div[data-testid="stMetricValue"] { color: #d05ce3 !important; }

/* 8. CORREÇÃO FINAL DE ÍCONES (Impede texto por cima) */
.material-icons, 
i, 
span[class^="material-"], 
svg {
    font-family: 'Material Icons' !important;
    font-weight: normal;
    font-style: normal;
    display: inline-block;
    text-transform: none;
    letter-spacing: normal;
    word-wrap: normal;
    white-space: nowrap;
    direction: ltr;
}

/* Link Zap */
.alerta-zap { 
    background-color: #00e676; 
    color: #004d40 !important; 
    padding: 8px; 
    border-radius: 8px; 
    text-align: center; 
    font-weight: bold; 
    text-decoration: none; 
    display: block; 
    border: 2px solid #00a152; 
}
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DO LINK MÁGICO (LOGIN AUTOMÁTICO) ---
# Verifica se o link tem "?acesso=vip"
params = st.query_params
token_acesso = params.get("acesso", None)

if 'autenticado' not in st.session_state: 
    st.session_state['autenticado'] = False

# Se o token estiver certo, libera o acesso direto
if token_acesso == "vip":
    st.session_state['autenticado'] = True

if 'menu_index' not in st.session_state: st.session_state['menu_index'] = 0
if 'menu_key' not in st.session_state: st.session_state['menu_key'] = 0

# --- TELA DE LOGIN (Só aparece se NÃO tiver o link mágico) ---
if not st.session_state['autenticado']:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 style='text-align: center;'>💜 Login VIP</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário").strip()
            p = st.text_input("Senha", type="password").strip()
            if st.form_submit_button("Entrar"):
                if u == "admin" and p == "nail123":
                    st.session_state['autenticado'] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
    st.stop()

# --- MENU LATERAL ---
opcoes = ["Agenda", "Checkout", "Financeiro", "CRM & Fidelidade", "Estoque", "Clientes"]
with st.sidebar:
    st.title("💜 Menu")
    menu_selecionado = option_menu(
        None, opcoes,
        icons=["calendar2-heart", "cart4", "graph-up", "gem", "box-seam", "people-fill"],
        default_index=st.session_state['menu_index'],
        key=f"menu_{st.session_state['menu_key']}",
        styles={
            "container": {"background-color": "#2d1b4e", "padding": "5px"},
            "nav-link": {"color": "#e0d4fc", "font-size": "15px", "text-align": "left", "margin": "5px"},
            "nav-link-selected": {"background-color": "#673ab7", "color": "white", "font-weight": "bold"}
        }
    )
    st.divider()
    if st.button("Sair"):
        st.session_state['autenticado'] = False
        st.query_params.clear() # Limpa o token ao sair
        st.rerun()

# --- FUNCIONALIDADES ---

if menu_selecionado == "Agenda":
    st.header("🗓️ Agenda")
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("### ➕ Agendar")
        tipo_cadastro = st.radio("Tipo:", ["Cliente Existente", "Nova Cliente"], horizontal=True)

        with st.form("ag_form"):
            d = st.date_input("Data", value=dt.now())
            h = st.time_input("Hora")

            nome_final = ""
            if tipo_cadastro == "Cliente Existente":
                clis = supabase.table("clientes").select("nome").execute().data
                lista_n = [c['nome'] for c in clis] if clis else []
                nome_sel = st.selectbox("Selecione:", lista_n if lista_n else ["Nenhuma"])
                nome_final = nome_sel
                t_novo, cpf_novo = None, None
            else:
                st.markdown("---")
                nome_novo = st.text_input("Nome Completo")
                t_novo = st.text_input("WhatsApp (DDD+Num)")
                cpf_novo = st.text_input("CPF (Obrigatório)")
                nome_final = nome_novo

            s = st.multiselect("Serviços", list(TABELA_SERVICOS.keys()))

            if st.form_submit_button("Confirmar Agendamento"):
                erro = False
                if not nome_final or nome_final == "Nenhuma":
                    st.error("Nome inválido!"); erro = True
                if not s:
                    st.error("Serviço obrigatório!"); erro = True

                if tipo_cadastro == "Nova Cliente":
                    if not cpf_novo:
                        st.error("CPF obrigatório!"); erro = True
                    else:
                        try:
                            supabase.table("clientes").insert({"nome": nome_final, "cpf": cpf_novo, "telefone": t_novo}).execute()
                        except:
                            st.error("CPF já existe!"); erro = True

                if not erro:
                    supabase.table("agenda").insert({"data_hora": f"{d}T{h}", "cliente_nome": nome_final, "servico": ", ".join(s), "status": "Pendente"}).execute()
                    st.success("Agendado!")
                    time.sleep(1); st.rerun()

    with col2:
        st.markdown("### 🟣 Próximos")
        res = supabase.table("agenda").select("*").eq("status", "Pendente").order("data_hora").execute().data
        clis_all = supabase.table("clientes").select("nome, telefone").execute().data
        mapa_zap = {c['nome']: c.get('telefone', '') for c in clis_all} if clis_all else {}

        if res:
            for row in res:
                tel = mapa_zap.get(row['cliente_nome'], "")
                zap_html = ""
                if tel:
                    msg = f"Olá {row['cliente_nome']}, confirmando horário dia {row['data_hora'][8:10]}/{row['data_hora'][5:7]} às {row['data_hora'][11:16]}?"
                    link = f"https://wa.me/55{tel.replace(' ', '').replace('-', '')}?text={msg.replace(' ', '%20')}"
                    zap_html = f'<a href="{link}" target="_blank" class="alerta-zap">💬 WhatsApp</a>'

                with st.expander(f"⏰ {row['data_hora'][11:16]} - {row['cliente_nome']}"):
                    if zap_html: st.markdown(zap_html, unsafe_allow_html=True)
                    st.write(f"**Serviços:** {row['servico']}")
                    c1, c2 = st.columns(2)
                    if c1.button("Checkout", key=f"chk_{row['id']}"):
                        st.session_state['checkout_nome'] = row['cliente_nome']
                        st.session_state['checkout_serv'] = row['servico'].split(", ")
                        st.session_state['checkout_id'] = row['id']
                        st.session_state['menu_index'] = 1; st.session_state['menu_key'] += 1; st.rerun()
                    if c2.button("Excluir", key=f"del_{row['id']}"):
                        supabase.table("agenda").delete().eq("id", row['id']).execute(); st.rerun()
        else:
            st.info("Nenhum horário pendente.")

elif menu_selecionado == "Checkout":
    st.header("🏁 Checkout")
    clis = supabase.table("clientes").select("nome, cpf").execute().data
    estoque_atual = supabase.table("estoque").select("*").order("item").execute().data

    if not clis:
        st.warning("Sem clientes.")
    else:
        n_pre = st.session_state.get('checkout_nome', "")
        s_pre = st.session_state.get('checkout_serv', [])
        v_sug = float(sum([TABELA_SERVICOS.get(sv, 0.0) for sv in s_pre]))

        with st.form("pay"):
            st.markdown("#### 1. Atendimento")
            c1, c2 = st.columns(2)
            lista_c = [c['nome'] for c in clis]
            idx = lista_c.index(n_pre) if n_pre in lista_c else 0
            c_sel = c1.selectbox("Cliente", lista_c, index=idx)
            s_sel = c2.multiselect("Serviços", list(TABELA_SERVICOS.keys()), default=s_pre)

            st.divider()
            st.markdown("#### 2. Baixa de Estoque")
            
            input_keys = {}
            if estoque_atual:
                cols = st.columns(3)
                for i, item in enumerate(estoque_atual):
                    with cols[i % 3]:
                        key_name = f"st_{item['id']}"
                        st.number_input(f"{item['item']} (Disp: {item['quantidade']})", min_value=0, key=key_name)
                        input_keys[item['id']] = key_name
            else: st.info("Estoque vazio.")

            st.divider()
            st.markdown("#### 3. Pagamento")
            c3, c4 = st.columns(2)
            v_cob = c3.number_input("Valor Total (R$)", value=v_sug)
            pg = c4.radio("Forma", ["Pix", "Cartão", "Dinheiro"], horizontal=True)

            if st.form_submit_button("FINALIZAR"):
                # Recupera e valida estoque
                itens_baixar = {}
                for item_id, key_name in input_keys.items():
                    qtd_digitada = st.session_state.get(key_name, 0)
                    if qtd_digitada > 0:
                        qtd_atual = next((x['quantidade'] for x in estoque_atual if x['id'] == item_id), 0)
                        itens_baixar[item_id] = {'qtd': qtd_digitada, 'atual': qtd_atual}

                cpf = next(c['cpf'] for c in clis if c['nome'] == c_sel)
                supabase.table("historico").insert(
                    {"cliente_cpf": cpf, "servico": ", ".join(s_sel), "valor_cobrado": float(v_cob),
                     "forma_pagamento": pg}).execute()

                for id_i, d in itens_baixar.items():
                    nova_qtd = max(0, d['atual'] - d['qtd'])
                    supabase.table("estoque").update({"quantidade": nova_qtd}).eq("id", id_i).execute()

                if 'checkout_id' in st.session_state:
                    supabase.table("agenda").update({"status": "Concluído"}).eq("id", st.session_state['checkout_id']).execute()
                    del st.session_state['checkout_id']

                st.success("Venda salva!")
                st.session_state['menu_index'] = 0; st.session_state['menu_key'] += 1; time.sleep(1); st.rerun()

elif menu_selecionado == "Financeiro":
    st.header("📊 Financeiro")
    tab1, tab2 = st.tabs(["Visão Geral", "Despesas"])

    with tab1:
        hist = supabase.table("historico").select("*").execute().data
        desp = supabase.table("despesas").select("*").execute().data
        rec = sum([float(h['valor_cobrado']) for h in hist]) if hist else 0.0
        pag = sum([float(d['valor']) for d in desp]) if desp else 0.0
        lucro = rec - pag

        c1, c2, c3 = st.columns(3)
        c1.metric("Receita", f"R$ {rec:.2f}")
        c2.metric("Despesas", f"R$ {pag:.2f}")
        c3.metric("Lucro", f"R$ {lucro:.2f}", delta_color="normal")

        if hist:
            df = pd.DataFrame(hist)
            df['valor'] = pd.to_numeric(df['valor_cobrado'])
            fig = px.pie(df, names='forma_pagamento', values='valor', title='Meios de Pagamento',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with st.form("despesa"):
            desc = st.text_input("Descrição")
            val = st.number_input("Valor (R$)", min_value=0.0)
            if st.form_submit_button("Salvar Conta"):
                supabase.table("despesas").insert({"descricao": desc, "valor": val}).execute()
                st.success("Salvo!"); st.rerun()

elif menu_selecionado == "CRM & Fidelidade":
    st.header("💎 CRM")
    hist = supabase.table("historico").select("*").execute().data
    clis = supabase.table("clientes").select("*").execute().data

    if hist and clis:
        df = pd.DataFrame(hist)
        visitas = df['cliente_cpf'].value_counts().reset_index()
        visitas.columns = ['cpf', 'contagem']

        for _, r in visitas.iterrows():
            nome = next((c['nome'] for c in clis if c['cpf'] == r['cpf']), "Desconhecida")
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{nome}**")
                c1.progress(min(r['contagem'] / 10, 1.0))
                c2.write(f"{r['contagem']}/10")
                if r['contagem'] >= 10: st.success("🎁 PRÊMIO LIBERADO!")

elif menu_selecionado == "Estoque":
    st.header("📦 Gestão de Estoque")

    # Formulário de Cadastro Rápido
    with st.expander("➕ Cadastrar Novo Item", expanded=False):
        with st.form("novo_item_est"):
            col_a, col_b = st.columns([3, 1])
            i = col_a.text_input("Nome do Material")
            q = col_b.number_input("Quantidade Inicial", min_value=0, value=1)
            if st.form_submit_button("Salvar Novo Item"):
                if i:
                    supabase.table("estoque").insert({"item": i, "quantidade": q}).execute()
                    st.success("Item adicionado!")
                    st.rerun()

    # Lista de Controle
    res = supabase.table("estoque").select("*").order("item").execute().data
    if res:
        st.divider()
        st.markdown("#### Seus Materiais:")
        for item in res:
            status_icon = "🟢"
            if item['quantidade'] < 5: status_icon = "⚠️"
            if item['quantidade'] == 0: status_icon = "🔴"

            with st.expander(f"{status_icon} {item['item']} (Qtd: {item['quantidade']})"):
                c1, c2, c3 = st.columns([1, 1, 2])

                if c1.button("➖ 1", key=f"sub_{item['id']}"):
                    if item['quantidade'] > 0:
                        supabase.table("estoque").update({"quantidade": item['quantidade'] - 1}).eq("id", item['id']).execute()
                        st.rerun()

                if c2.button("➕ 1", key=f"add_{item['id']}"):
                    supabase.table("estoque").update({"quantidade": item['quantidade'] + 1}).eq("id", item['id']).execute()
                    st.rerun()

                if c3.button("🗑️ Excluir Item", key=f"del_{item['id']}"):
                    supabase.table("estoque").delete().eq("id", item['id']).execute()
                    st.rerun()

                st.divider()
                st.markdown("**Editar Detalhes:**")
                with st.form(key=f"edit_form_{item['id']}"):
                    novo_nome = st.text_input("Nome", value=item['item'])
                    nova_qtd_manual = st.number_input("Quantidade Total", value=item['quantidade'], min_value=0)

                    if st.form_submit_button("💾 Salvar Alterações"):
                        supabase.table("estoque").update({"item": novo_nome, "quantidade": nova_qtd_manual}).eq("id", item['id']).execute()
                        st.success("Atualizado!")
                        st.rerun()
    else:
        st.info("Seu estoque está vazio.")

elif menu_selecionado == "Clientes":
    st.header("👥 Clientes")
    with st.expander("➕ Nova Ficha"):
        with st.form("cli_full"):
            n = st.text_input("Nome");
            c = st.text_input("CPF")
            t = st.text_input("WhatsApp");
            a = st.text_area("Anamnese")
            if st.form_submit_button("Salvar"):
                if n and c:
                    supabase.table("clientes").insert({"nome": n, "cpf": c, "telefone": t, "anamnese": a}).execute()
                    st.success("Salvo!"); st.rerun()

    res = supabase.table("clientes").select("*").execute().data
    if res:
        for cli in res:
            with st.expander(f"👤 {cli['nome']}"):
                st.markdown(f"**Zap:** {cli.get('telefone', '-')}")
                st.info(f"Obs: {cli.get('anamnese', '-')}")
