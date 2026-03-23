import streamlit as st
import xmltodict
import pandas as pd

st.set_page_config(page_title="Núcleo Farma - Visualizador XML", layout="wide")

# 🎨 CSS melhorado
st.markdown("""
<style>
[data-testid="stHeader"] {background: #1a1c23;}
.reportview-container { background: #f0f2f6; }

.metric-card {
    background-color: #FFFFFF !important;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
    text-align: center;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.metric-label {
    color: #666;
    font-size: 12px;
    font-weight: bold;
}

.metric-value {
    color: #000;
    font-size: 22px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)


def metric_box(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# 🔧 CARREGAMENTO ROBUSTO
def carregar_dados(xml_content):
    dados = xmltodict.parse(xml_content, process_namespaces=False)

    if 'nfeProc' in dados:
        return dados['nfeProc']['NFe']['infNFe']
    else:
        return dados['NFe']['infNFe']


st.title("📑 Visualizador de NF-e (Layout Padrão DANFE)")
st.markdown("---")

uploaded_file = st.file_uploader("Arraste o XML aqui", type="xml")

if uploaded_file:
    try:
        nfe = carregar_dados(uploaded_file.read())

        ide = nfe.get('ide', {})
        emit = nfe.get('emit', {})
        dest = nfe.get('dest', {})
        tot = nfe.get('total', {}).get('ICMSTot', {})

        # 🧾 CABEÇALHO
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_box("NÚMERO NF", ide.get('nNF', ''))
        with c2: metric_box("SÉRIE", ide.get('serie', ''))
        with c3: metric_box("VALOR TOTAL", f"R$ {tot.get('vNF', '0.00')}")
        with c4: metric_box("OPERAÇÃO", ide.get('natOp', ''))

        # 🏢 EMITENTE / DESTINATÁRIO
        col_em, col_dest = st.columns(2)

        with col_em:
            st.subheader("🏢 Emitente")
            st.info(f"""
**{emit.get('xNome', '')}**

CNPJ: {emit.get('CNPJ', '')} | IE: {emit.get('IE', '')}

{emit.get('enderEmit', {}).get('xLgr', '')}, {emit.get('enderEmit', {}).get('nro', '')}
{emit.get('enderEmit', {}).get('xMun', '')}/{emit.get('enderEmit', {}).get('UF', '')}
""")

        with col_dest:
            st.subheader("👤 Destinatário")
            st.success(f"""
**{dest.get('xNome', '')}**

CNPJ: {dest.get('CNPJ', '')} | IE: {dest.get('IE', 'ISENTO')}

{dest.get('enderDest', {}).get('xLgr', '')}, {dest.get('enderDest', {}).get('nro', '')}
{dest.get('enderDest', {}).get('xMun', '')}/{dest.get('enderDest', {}).get('UF', '')}
""")

        # 💳 DUPLICATAS
        st.subheader("💳 FATURA / DUPLICATAS")
        duplicatas = nfe.get('cobr', {}).get('dup', [])

        if duplicatas:
            if not isinstance(duplicatas, list):
                duplicatas = [duplicatas]

            cols = st.columns(len(duplicatas))
            for i, d in enumerate(duplicatas):
                with cols[i]:
                    st.warning(f"""
Parc: {d.get('nDup')}
Venc: {d.get('dVenc')}
Valor: R$ {d.get('vDup')}
""")

        # 📊 IMPOSTOS
        st.subheader("📊 CÁLCULO DO IMPOSTO")

        r1 = st.columns(5)
        r1[0].text_input("BASE ICMS", tot.get('vBC'), disabled=True)
        r1[1].text_input("ICMS", tot.get('vICMS'), disabled=True)
        r1[2].text_input("BC ST", tot.get('vBCST', '0.00'), disabled=True)
        r1[3].text_input("ICMS ST", tot.get('vST', '0.00'), disabled=True)
        r1[4].text_input("PRODUTOS", tot.get('vProd'), disabled=True)

        # 🚚 TRANSPORTE
        st.subheader("🚚 TRANSPORTADOR")
        transp = nfe.get('transp', {})
        t_data = transp.get('transporta', {})

        st.text_input("RAZÃO SOCIAL", t_data.get('xNome', 'N/A'), disabled=True)
        st.text_input("CNPJ", t_data.get('CNPJ', 'N/A'), disabled=True)

        # 📦 PRODUTOS
        st.subheader("📦 PRODUTOS")

        itens = nfe.get('det', [])
        if not isinstance(itens, list):
            itens = [itens]

        lista_prods = []

        for i in itens:
            p = i.get('prod', {})

            # 🔥 ICMS seguro
            imposto = i.get('imposto', {}).get('ICMS', {})
            tipo_icms = next(iter(imposto), None)
            icms_data = imposto.get(tipo_icms, {}) if tipo_icms else {}

            # 🔥 NCM + CEST
            ncm = p.get('NCM', '')
            cest = p.get('CEST', '')

            if cest:
                ncm_cest = f"{ncm} / {cest}"
            else:
                ncm_cest = ncm

            lista_prods.append({
                "CÓDIGO": p.get('cProd'),
                "DESCRIÇÃO": p.get('xProd'),
                "NCM / CEST": ncm_cest,
                "CFOP": p.get('CFOP'),
                "QTD": p.get('qCom'),
                "V. UNIT": p.get('vUnCom'),
                "V. TOTAL": p.get('vProd'),
                "BC ICMS": icms_data.get('vBC', '0.00'),
                "V. ICMS": icms_data.get('vICMS', '0.00'),
                "ALIQ %": icms_data.get('pICMS', '0.00')
            })

        df = pd.DataFrame(lista_prods)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 📥 EXPORTAR
        st.download_button(
            "📥 Baixar CSV",
            df.to_csv(index=False).encode('utf-8'),
            "produtos.csv",
            "text/csv"
        )

        # 📝 INFO ADICIONAL
        st.subheader("📝 DADOS ADICIONAIS")
        st.info(nfe.get('infAdic', {}).get('infCpl', 'N/A'))

    except Exception as e:
        st.error(f"Erro ao processar XML: {e}")
