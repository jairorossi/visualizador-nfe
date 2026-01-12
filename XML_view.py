import streamlit as st
import xmltodict
import pandas as pd

st.set_page_config(page_title="Núcleo Farma - Visualizador XML", layout="wide")

# CSS para garantir contraste total e visual de PDF profissional
st.markdown("""
    <style>
    [data-testid="stHeader"] {background: #1a1c23;}
    .reportview-container { background: #f0f2f6; }
    /* Estilo dos Cards do Cabeçalho */
    .metric-card {
        background-color: #FFFFFF !important;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #000000;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-label { color: #555555; font-size: 12px; font-weight: bold; margin-bottom: 5px; }
    .metric-value { color: #000000; font-size: 22px; font-weight: 800; }
    /* Ajuste para inputs desabilitados (Impostos) */
    div[data-baseweb="input"] input:disabled {
        -webkit-text-fill-color: #000000 !important;
        color: #000000 !important;
        font-weight: bold !important;
        background-color: #f8f9fa !important;
    }
    </style>
    """, unsafe_allow_html=True)

def metric_box(label, value):
    st.markdown(f'<div class="metric-card"><p class="metric-label">{label}</p><p class="metric-value">{value}</p></div>', unsafe_allow_html=True)

def carregar_dados(xml_content):
    dados = xmltodict.parse(xml_content, process_namespaces=False)
    return dados['nfeProc']['NFe']['infNFe']

st.title("📑 Visualizador de NF-e (Layout Padrão DANFE)")
st.markdown("---")

uploaded_file = st.file_uploader("Arraste o XML aqui", type="xml")

if uploaded_file:
    try:
        nfe = carregar_dados(uploaded_file.read())
        ide = nfe['ide']
        emit = nfe['emit']
        dest = nfe['dest']
        tot = nfe['total']['ICMSTot']
        
        # 1. CABEÇALHO (IDENTIFICAÇÃO)
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_box("NÚMERO NF", ide['nNF'])
        with c2: metric_box("SÉRIE", ide['serie'])
        with c3: metric_box("VALOR TOTAL", f"R$ {tot['vNF']}")
        with c4: metric_box("OPERAÇÃO", ide['natOp'])

        # 2. EMITENTE E DESTINATÁRIO
        col_em, col_dest = st.columns(2)
        with col_em:
            st.subheader("🏢 Emitente")
            st.info(f"**{emit['xNome']}**\n\nCNPJ: {emit['CNPJ']} | IE: {emit['IE']}\n\n{emit['enderEmit']['xLgr']}, {emit['enderEmit']['nro']} - {emit['enderEmit']['xMun']}/{emit['enderEmit']['UF']}")
        with col_dest:
            st.subheader("👤 Destinatário")
            st.success(f"**{dest['xNome']}**\n\nCNPJ: {dest['CNPJ']} | IE: {dest.get('IE', 'ISENTO')}\n\n{dest['enderDest']['xLgr']}, {dest['enderDest'].get('nro', '')} - {dest['enderDest']['xMun']}/{dest['enderDest']['UF']}")

        # 3. FATURA / DUPLICATAS
        st.subheader("💳 FATURA / DUPLICATAS")
        duplicatas = nfe.get('cobr', {}).get('dup', [])
        if duplicatas:
            if not isinstance(duplicatas, list): duplicatas = [duplicatas]
            cols_dup = st.columns(len(duplicatas))
            for i, d in enumerate(duplicatas):
                with cols_dup[i]:
                    st.warning(f"**Parc: {d.get('nDup')}**\n\nVenc: {d.get('dVenc')}\n\nValor: R$ {d.get('vDup')}")

        # 4. CÁLCULO DO IMPOSTO (Conforme solicitado)
        st.subheader("📊 CÁLCULO DO IMPOSTO")
        r1 = st.columns(5)
        r1[0].text_input("BASE DE CÁLC. DO ICMS", value=tot.get('vBC'), disabled=True)
        r1[1].text_input("VALOR DO ICMS", value=tot.get('vICMS'), disabled=True)
        r1[2].text_input("BASE CÁLC. ICMS S.T.", value=tot.get('vBCST', '0.00'), disabled=True)
        r1[3].text_input("VALOR DO ICMS SUBST.", value=tot.get('vST', '0.00'), disabled=True)
        r1[4].text_input("V. TOTAL PRODUTOS", value=tot.get('vProd'), disabled=True)

        r2 = st.columns(5)
        r2[0].text_input("VALOR DO FRETE", value=tot.get('vFrete', '0.00'), disabled=True)
        r2[1].text_input("VALOR DO SEGURO", value=tot.get('vSeg', '0.00'), disabled=True)
        r2[2].text_input("DESCONTO", value=tot.get('vDesc', '0.00'), disabled=True)
        r2[3].text_input("OUTRAS DESPESAS", value=tot.get('vOutro', '0.00'), disabled=True)
        r2[4].text_input("VALOR TOTAL IPI", value=tot.get('vIPI', '0.00'), disabled=True)

        r3 = st.columns(4)
        r3[0].text_input("VALOR DO PIS", value=tot.get('vPIS', '0.00'), disabled=True)
        r3[1].text_input("VALOR DA COFINS", value=tot.get('vCOFINS', '0.00'), disabled=True)
        r3[2].text_input("V. TOT. TRIB.", value=tot.get('vTotTrib', '0.00'), disabled=True)
        r3[3].text_input("VALOR TOTAL DA NOTA", value=tot.get('vNF'), disabled=True)

        # 5. TRANSPORTADOR / VOLUMES TRANSPORTADOS
        st.subheader("🚚 TRANSPORTADOR / VOLUMES TRANSPORTADOS")
        transp = nfe.get('transp', {})
        t_data = transp.get('transporta', {})
        v_data = transp.get('vol', {})
        if not isinstance(v_data, list): v_data = [v_data] if v_data else []
        vol = v_data[0] if v_data else {}

        tr1 = st.columns([3, 1, 2])
        tr1[0].text_input("RAZÃO SOCIAL", value=t_data.get('xNome', 'N/A'), disabled=True)
        tr1[1].text_input("FRETE POR CONTA", value=transp.get('modFrete'), disabled=True)
        tr1[2].text_input("CNPJ / CPF", value=t_data.get('CNPJ', 'N/A'), disabled=True)

        tr2 = st.columns(4)
        tr2[0].text_input("QUANTIDADE", value=vol.get('qVol', '0'), disabled=True)
        tr2[1].text_input("ESPÉCIE", value=vol.get('esp', 'N/A'), disabled=True)
        tr2[2].text_input("PESO BRUTO", value=vol.get('pesoB', '0.000'), disabled=True)
        tr2[3].text_input("PESO LÍQUIDO", value=vol.get('pesoL', '0.000'), disabled=True)

        # 6. DADOS DOS PRODUTOS
        st.subheader("📦 DADOS DOS PRODUTOS / SERVIÇOS")
        itens = nfe['det']
        if not isinstance(itens, list): itens = [itens]
        
        lista_prods = []
        for i in itens:
            p = i['prod']
            imposto = i['imposto']['ICMS']
            tipo_icms = list(imposto.keys())[0]
            lista_prods.append({
                "CÓDIGO": p['cProd'],
                "DESCRIÇÃO": p['xProd'],
                "NCM": p['NCM'],
                "CFOP": p['CFOP'],
                "UN": p['uCom'],
                "QTD": p['qCom'],
                "V. UNIT": p['vUnCom'],
                "V. TOTAL": p['vProd'],
                "BC ICMS": imposto[tipo_icms].get('vBC', '0.00'),
                "V. ICMS": imposto[tipo_icms].get('vICMS', '0.00'),
                "ALIQ %": imposto[tipo_icms].get('pICMS', '0.00')
            })
        st.dataframe(pd.DataFrame(lista_prods), use_container_width=True, hide_index=True)

        # 7. INFORMAÇÕES ADICIONAIS
        st.subheader("📝 DADOS ADICIONAIS")
        st.info(f"**INFORMAÇÕES COMPLEMENTARES:**\n\n{nfe['infAdic'].get('infCpl', 'N/A')}")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")