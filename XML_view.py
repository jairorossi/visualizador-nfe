import streamlit as st
import xmltodict
import pandas as pd
import pyperclip
from streamlit.components.v1 import html

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
    /* Estilo para o card da chave NFE */
    .chave-nfe-card {
        background-color: #e8f4f8 !important;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #1a5f7a;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .chave-nfe-label {
        color: #0a2f3a;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .chave-nfe-value {
        color: #000000;
        font-size: 24px;
        font-weight: 800;
        font-family: monospace;
        letter-spacing: 2px;
        margin-bottom: 15px;
        cursor: pointer;
        user-select: all;
        padding: 10px;
        background-color: #ffffff;
        border-radius: 5px;
        border: 1px dashed #1a5f7a;
    }
    .chave-nfe-value:hover {
        background-color: #f0f8ff;
    }
    /* Estilo para os botões */
    .fsist-button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        font-weight: bold;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .fsist-button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    .copy-button {
        background-color: #2196F3;
        border: none;
        color: white;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .copy-button:hover {
        background-color: #1976D2;
    }
    .tooltip {
        position: relative;
        display: inline-block;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 140px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 150%;
        left: 50%;
        margin-left: -75px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #555 transparent transparent transparent;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)

def metric_box(label, value):
    st.markdown(f'<div class="metric-card"><p class="metric-label">{label}</p><p class="metric-value">{value}</p></div>', unsafe_allow_html=True)

def chave_nfe_box(chave):
    # Formatar a chave em grupos de 4 dígitos para melhor legibilidade
    if chave and len(chave) == 44:
        chave_formatada = ' '.join([chave[i:i+4] for i in range(0, 44, 4)])
        chave_sem_formatacao = chave
    else:
        chave_formatada = chave
        chave_sem_formatacao = chave
    
    # Criar o HTML com JavaScript para copiar
    html_code = f"""
    <div class="chave-nfe-card">
        <p class="chave-nfe-label">🔑 CHAVE DA NOTA FISCAL ELETRÔNICA (44 DÍGITOS)</p>
        <div class="tooltip">
            <p class="chave-nfe-value" onclick="copiarChave()" id="chaveValor">{chave_formatada}</p>
            <span class="tooltiptext" id="tooltipTexto">Clique para copiar</span>
        </div>
        <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
            <button class="copy-button" onclick="copiarChave()">
                📋 Copiar Chave
            </button>
            <button class="fsist-button" onclick="abrirFSist()">
                🌐 Abrir FSist (cole a chave)
            </button>
        </div>
        <p style="color: #666; font-size: 12px; margin-top: 10px;">
            👆 Clique na chave para copiar | Depois cole no site da FSist
        </p>
    </div>

    <script>
    const chaveReal = "{chave_sem_formatacao}";
    
    function copiarChave() {{
        navigator.clipboard.writeText(chaveReal).then(function() {{
            const tooltip = document.getElementById('tooltipTexto');
            const originalText = tooltip.textContent;
            tooltip.textContent = '✅ Copiado!';
            tooltip.style.backgroundColor = '#4CAF50';
            
            setTimeout(function() {{
                tooltip.textContent = originalText;
                tooltip.style.backgroundColor = '#555';
            }}, 2000);
        }}, function(err) {{
            alert('Erro ao copiar: ' + err);
        }});
    }}
    
    function abrirFSist() {{
        window.open('https://www.fsist.com.br', '_blank');
    }}
    </script>
    """
    
    st.components.v1.html(html_code, height=250)

def carregar_dados(xml_content):
    dados = xmltodict.parse(xml_content, process_namespaces=False)
    return dados

st.title("📑 Visualizador de NF-e (Layout Padrão DANFE)")
st.markdown("---")

# Informação sobre o FSist
with st.expander("ℹ️ Como baixar o XML no FSist", expanded=True):
    st.markdown("""
    ### 📋 Passo a passo para baixar o XML:
    
    1. **Clique na chave** acima ou no botão **"Copiar Chave"** para copiar os 44 dígitos
    2. **Clique em "Abrir FSist"** para ir ao site
    3. **No site FSist:**
       - Cole a chave no campo "Digite a Chave" (Ctrl+V)
       - Clique em "CONSULTAR NOTA"
       - Siga as instruções (será necessário certificado digital)
    
    ⚠️ **Importante sobre o FSist:**
    - Gratuito para uma chave por vez
    - Exige **certificado digital** (A1 ou A3)
    - O certificado deve ser do emitente, destinatário ou autorizado na tag autXML
    """)

uploaded_file = st.file_uploader("Arraste o XML aqui", type="xml")

if uploaded_file:
    try:
        dados_completos = carregar_dados(uploaded_file.read())
        
        # Extrair a chave NFE - Primeiro do protNFe (mais confiável)
        chave_nfe = ""
        if 'nfeProc' in dados_completos and 'protNFe' in dados_completos['nfeProc']:
            protNFe = dados_completos['nfeProc']['protNFe']
            if 'infProt' in protNFe and 'chNFe' in protNFe['infProt']:
                chave_nfe = protNFe['infProt']['chNFe']
        
        # Se não encontrar no protNFe, tenta extrair do Id da infNFe
        if not chave_nfe and 'nfeProc' in dados_completos and 'NFe' in dados_completos['nfeProc']:
            nfe = dados_completos['nfeProc']['NFe']
            if 'infNFe' in nfe and '@Id' in nfe['infNFe']:
                id_nfe = nfe['infNFe']['@Id']
                # Remove o prefixo "NFe" se existir
                if id_nfe.startswith('NFe'):
                    chave_nfe = id_nfe[3:]
                else:
                    chave_nfe = id_nfe
        
        # Extrair os dados da NFe para o resto do processamento
        nfe = dados_completos['nfeProc']['NFe']['infNFe']
        ide = nfe['ide']
        emit = nfe['emit']
        dest = nfe['dest']
        tot = nfe['total']['ICMSTot']
        
        # 1. EXIBIR A CHAVE NFE PRIMEIRO COM OPÇÃO DE COPIAR
        chave_nfe_box(chave_nfe)
        
        # 2. CABEÇALHO (IDENTIFICAÇÃO)
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_box("NÚMERO NF", ide['nNF'])
        with c2: metric_box("SÉRIE", ide['serie'])
        with c3: metric_box("VALOR TOTAL", f"R$ {tot['vNF']}")
        with c4: metric_box("OPERAÇÃO", ide['natOp'])

        # 3. EMITENTE E DESTINATÁRIO
        col_em, col_dest = st.columns(2)
        with col_em:
            st.subheader("🏢 Emitente")
            st.info(f"**{emit['xNome']}**\n\nCNPJ: {emit['CNPJ']} | IE: {emit['IE']}\n\n{emit['enderEmit']['xLgr']}, {emit['enderEmit']['nro']} - {emit['enderEmit']['xMun']}/{emit['enderEmit']['UF']}")
        with col_dest:
            st.subheader("👤 Destinatário")
            st.success(f"**{dest['xNome']}**\n\nCNPJ: {dest['CNPJ']} | IE: {dest.get('IE', 'ISENTO')}\n\n{dest['enderDest']['xLgr']}, {dest['enderDest'].get('nro', '')} - {dest['enderDest']['xMun']}/{dest['enderDest']['UF']}")

        # 4. FATURA / DUPLICATAS
        st.subheader("💳 FATURA / DUPLICATAS")
        duplicatas = nfe.get('cobr', {}).get('dup', [])
        if duplicatas:
            if not isinstance(duplicatas, list): duplicatas = [duplicatas]
            cols_dup = st.columns(len(duplicatas))
            for i, d in enumerate(duplicatas):
                with cols_dup[i]:
                    st.warning(f"**Parc: {d.get('nDup')}**\n\nVenc: {d.get('dVenc')}\n\nValor: R$ {d.get('vDup')}")

        # 5. CÁLCULO DO IMPOSTO
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

        # 6. TRANSPORTADOR / VOLUMES TRANSPORTADOS
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

        # 7. DADOS DOS PRODUTOS
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

        # 8. INFORMAÇÕES ADICIONAIS
        st.subheader("📝 DADOS ADICIONAIS")
        st.info(f"**INFORMAÇÕES COMPLEMENTARES:**\n\n{nfe['infAdic'].get('infCpl', 'N/A')}")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
