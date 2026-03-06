import streamlit as st
import xmltodict
import pandas as pd
from streamlit.components.v1 import html

st.set_page_config(page_title="Núcleo Farma - Visualizador XML", layout="wide")

# CSS para garantir contraste total e visual limpo
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-label { 
        color: #333333; 
        font-size: 14px; 
        font-weight: bold; 
        margin-bottom: 8px; 
        text-transform: uppercase;
    }
    .metric-value { 
        color: #000000; 
        font-size: 24px; 
        font-weight: 800; 
    }
    /* Ajuste para inputs desabilitados (Impostos) */
    div[data-baseweb="input"] input:disabled {
        -webkit-text-fill-color: #000000 !important;
        color: #000000 !important;
        font-weight: bold !important;
        background-color: #f8f9fa !important;
        border: 1px solid #cccccc !important;
    }
    /* Estilo para o card da chave NFE */
    .chave-nfe-card {
        background-color: #FFFFFF !important;
        padding: 25px;
        border-radius: 10px;
        border: 2px solid #1a5f7a;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .chave-nfe-label {
        color: #1a5f7a;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .chave-nfe-value {
        color: #000000 !important;
        font-size: 28px;
        font-weight: 800;
        font-family: 'Courier New', monospace;
        letter-spacing: 3px;
        margin: 20px 0;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #1a5f7a;
        cursor: pointer;
        user-select: all;
        transition: all 0.3s ease;
    }
    .chave-nfe-value:hover {
        background-color: #e8f4f8;
        transform: scale(1.01);
        box-shadow: 0 2px 8px rgba(26, 95, 122, 0.2);
    }
    /* Estilo para o botão de cópia */
    .copy-button {
        background-color: #1a5f7a;
        border: none;
        color: white;
        padding: 12px 30px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        font-weight: bold;
        margin: 10px 0;
        cursor: pointer;
        border-radius: 25px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        border: 1px solid #0d3b4f;
    }
    .copy-button:hover {
        background-color: #0d3b4f;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    .mensagem-copiado {
        background-color: #28a745;
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        margin-top: 10px;
        display: inline-block;
        font-weight: 500;
        animation: fadeInOut 2s forwards;
    }
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(-10px); }
        20% { opacity: 1; transform: translateY(0); }
        80% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-10px); }
    }
    /* Títulos das seções */
    .section-title {
        color: #1a5f7a;
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 2px solid #1a5f7a;
    }
    /* Texto de informações */
    .info-text {
        color: #000000;
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1a5f7a;
        margin: 10px 0;
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
        <div class="chave-nfe-label">🔑 CHAVE DA NOTA FISCAL ELETRÔNICA</div>
        <div class="chave-nfe-value" onclick="copiarChave()" id="chaveValor" title="Clique para copiar">
            {chave_formatada}
        </div>
        <button class="copy-button" onclick="copiarChave()">
            📋 COPIAR CHAVE
        </button>
        <div id="mensagemCopiado" style="margin-top: 10px; min-height: 30px;"></div>
    </div>

    <script>
    const chaveReal = "{chave_sem_formatacao}";
    
    function mostrarMensagem(texto, tipo) {{
        const div = document.getElementById('mensagemCopiado');
        div.innerHTML = `<span class="mensagem-copiado" style="background-color: ${{tipo === 'sucesso' ? '#28a745' : '#dc3545'}};">${{texto}}</span>`;
        setTimeout(() => {{
            div.innerHTML = '';
        }}, 2000);
    }}
    
    function copiarChave() {{
        if (navigator.clipboard && navigator.clipboard.writeText) {{
            navigator.clipboard.writeText(chaveReal).then(function() {{
                mostrarMensagem('✅ Chave copiada com sucesso!', 'sucesso');
                
                const chaveElement = document.getElementById('chaveValor');
                chaveElement.style.backgroundColor = '#d4edda';
                chaveElement.style.borderColor = '#28a745';
                setTimeout(() => {{
                    chaveElement.style.backgroundColor = '#f8f9fa';
                    chaveElement.style.borderColor = '#1a5f7a';
                }}, 500);
                
            }}).catch(function(err) {{
                copiarChaveFallback();
            }});
        }} else {{
            copiarChaveFallback();
        }}
    }}
    
    function copiarChaveFallback() {{
        const textarea = document.createElement('textarea');
        textarea.value = chaveReal;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        textarea.setSelectionRange(0, 99999);
        
        try {{
            const successful = document.execCommand('copy');
            if (successful) {{
                mostrarMensagem('✅ Chave copiada com sucesso!', 'sucesso');
            }} else {{
                mostrarMensagem('❌ Clique na chave e copie manualmente (Ctrl+C)', 'erro');
            }}
        }} catch (err) {{
            mostrarMensagem('❌ Clique na chave e copie manualmente (Ctrl+C)', 'erro');
        }}
        
        document.body.removeChild(textarea);
    }}
    
    // Adicionar evento de teclado para Ctrl+C
    document.getElementById('chaveValor').addEventListener('keydown', function(e) {{
        if ((e.ctrlKey || e.metaKey) && e.key === 'c') {{
            copiarChave();
        }}
    }});
    
    // Tornar o elemento focável
    document.getElementById('chaveValor').setAttribute('tabindex', '0');
    </script>
    """
    
    st.components.v1.html(html_code, height=250)

def carregar_dados(xml_content):
    dados = xmltodict.parse(xml_content, process_namespaces=False)
    return dados

st.title("📑 Visualizador de NF-e")
st.markdown("---")

uploaded_file = st.file_uploader("Arraste o XML aqui", type="xml")

if uploaded_file:
    try:
        dados_completos = carregar_dados(uploaded_file.read())
        
        # Extrair a chave NFE
        chave_nfe = ""
        if 'nfeProc' in dados_completos and 'protNFe' in dados_completos['nfeProc']:
            protNFe = dados_completos['nfeProc']['protNFe']
            if 'infProt' in protNFe and 'chNFe' in protNFe['infProt']:
                chave_nfe = protNFe['infProt']['chNFe']
        
        if not chave_nfe and 'nfeProc' in dados_completos and 'NFe' in dados_completos['nfeProc']:
            nfe = dados_completos['nfeProc']['NFe']
            if 'infNFe' in nfe and '@Id' in nfe['infNFe']:
                id_nfe = nfe['infNFe']['@Id']
                if id_nfe.startswith('NFe'):
                    chave_nfe = id_nfe[3:]
                else:
                    chave_nfe = id_nfe
        
        nfe = dados_completos['nfeProc']['NFe']['infNFe']
        ide = nfe['ide']
        emit = nfe['emit']
        dest = nfe['dest']
        tot = nfe['total']['ICMSTot']
        
        # 1. CHAVE NFE
        chave_nfe_box(chave_nfe)
        
        # 2. CABEÇALHO
        st.markdown('<p class="section-title">📋 IDENTIFICAÇÃO DA NOTA</p>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_box("NÚMERO", ide['nNF'])
        with c2: metric_box("SÉRIE", ide['serie'])
        with c3: metric_box("VALOR TOTAL", f"R$ {tot['vNF']}")
        with c4: metric_box("OPERAÇÃO", ide['natOp'])

        # 3. EMITENTE E DESTINATÁRIO
        col_em, col_dest = st.columns(2)
        with col_em:
            st.markdown('<p class="section-title">🏢 EMITENTE</p>', unsafe_allow_html=True)
            st.markdown(f'''
            <div class="info-text">
                <strong>{emit['xNome']}</strong><br><br>
                CNPJ: {emit['CNPJ']}<br>
                IE: {emit['IE']}<br><br>
                {emit['enderEmit']['xLgr']}, {emit['enderEmit']['nro']}<br>
                {emit['enderEmit']['xMun']}/{emit['enderEmit']['UF']}
            </div>
            ''', unsafe_allow_html=True)
        
        with col_dest:
            st.markdown('<p class="section-title">👤 DESTINATÁRIO</p>', unsafe_allow_html=True)
            st.markdown(f'''
            <div class="info-text">
                <strong>{dest['xNome']}</strong><br><br>
                CNPJ: {dest['CNPJ']}<br>
                IE: {dest.get('IE', 'ISENTO')}<br><br>
                {dest['enderDest']['xLgr']}, {dest['enderDest'].get('nro', '')}<br>
                {dest['enderDest']['xMun']}/{dest['enderDest']['UF']}
            </div>
            ''', unsafe_allow_html=True)

        # 4. FATURA
        st.markdown('<p class="section-title">💳 FATURA / DUPLICATAS</p>', unsafe_allow_html=True)
        duplicatas = nfe.get('cobr', {}).get('dup', [])
        if duplicatas:
            if not isinstance(duplicatas, list): duplicatas = [duplicatas]
            cols_dup = st.columns(len(duplicatas))
            for i, d in enumerate(duplicatas):
                with cols_dup[i]:
                    st.markdown(f'''
                    <div class="info-text" style="text-align: center;">
                        <strong>Parcela: {d.get('nDup')}</strong><br>
                        Venc: {d.get('dVenc')}<br>
                        Valor: R$ {d.get('vDup')}
                    </div>
                    ''', unsafe_allow_html=True)

        # 5. IMPOSTOS
        st.markdown('<p class="section-title">📊 CÁLCULO DO IMPOSTO</p>', unsafe_allow_html=True)
        r1 = st.columns(5)
        r1[0].text_input("BASE ICMS", value=tot.get('vBC'), disabled=True)
        r1[1].text_input("VALOR ICMS", value=tot.get('vICMS'), disabled=True)
        r1[2].text_input("BASE ICMS ST", value=tot.get('vBCST', '0.00'), disabled=True)
        r1[3].text_input("VALOR ICMS ST", value=tot.get('vST', '0.00'), disabled=True)
        r1[4].text_input("TOTAL PRODUTOS", value=tot.get('vProd'), disabled=True)

        r2 = st.columns(5)
        r2[0].text_input("FRETE", value=tot.get('vFrete', '0.00'), disabled=True)
        r2[1].text_input("SEGURO", value=tot.get('vSeg', '0.00'), disabled=True)
        r2[2].text_input("DESCONTO", value=tot.get('vDesc', '0.00'), disabled=True)
        r2[3].text_input("OUTRAS DESP.", value=tot.get('vOutro', '0.00'), disabled=True)
        r2[4].text_input("TOTAL IPI", value=tot.get('vIPI', '0.00'), disabled=True)

        r3 = st.columns(4)
        r3[0].text_input("PIS", value=tot.get('vPIS', '0.00'), disabled=True)
        r3[1].text_input("COFINS", value=tot.get('vCOFINS', '0.00'), disabled=True)
        r3[2].text_input("TOT. TRIB.", value=tot.get('vTotTrib', '0.00'), disabled=True)
        r3[3].text_input("TOTAL NOTA", value=tot.get('vNF'), disabled=True)

        # 6. TRANSPORTADOR
        st.markdown('<p class="section-title">🚚 TRANSPORTADOR</p>', unsafe_allow_html=True)
        transp = nfe.get('transp', {})
        t_data = transp.get('transporta', {})
        v_data = transp.get('vol', {})
        if not isinstance(v_data, list): v_data = [v_data] if v_data else []
        vol = v_data[0] if v_data else {}

        tr1 = st.columns([3, 1, 2])
        tr1[0].text_input("RAZÃO SOCIAL", value=t_data.get('xNome', 'N/A'), disabled=True)
        tr1[1].text_input("FRETE", value=transp.get('modFrete'), disabled=True)
        tr1[2].text_input("CNPJ/CPF", value=t_data.get('CNPJ', 'N/A'), disabled=True)

        tr2 = st.columns(4)
        tr2[0].text_input("QUANTIDADE", value=vol.get('qVol', '0'), disabled=True)
        tr2[1].text_input("ESPÉCIE", value=vol.get('esp', 'N/A'), disabled=True)
        tr2[2].text_input("PESO BRUTO", value=vol.get('pesoB', '0.000'), disabled=True)
        tr2[3].text_input("PESO LÍQUIDO", value=vol.get('pesoL', '0.000'), disabled=True)

        # 7. PRODUTOS
        st.markdown('<p class="section-title">📦 PRODUTOS</p>', unsafe_allow_html=True)
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
                "V. UNIT": f"R$ {p['vUnCom']}",
                "V. TOTAL": f"R$ {p['vProd']}",
                "BC ICMS": imposto[tipo_icms].get('vBC', '0.00'),
                "V. ICMS": imposto[tipo_icms].get('vICMS', '0.00'),
                "ALIQ %": imposto[tipo_icms].get('pICMS', '0.00')
            })
        st.dataframe(pd.DataFrame(lista_prods), use_container_width=True, hide_index=True)

        # 8. INFORMAÇÕES ADICIONAIS
        if 'infAdic' in nfe and nfe['infAdic'].get('infCpl'):
            st.markdown('<p class="section-title">📝 INFORMAÇÕES COMPLEMENTARES</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-text">{nfe["infAdic"].get("infCpl")}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar o XML: {str(e)}")
