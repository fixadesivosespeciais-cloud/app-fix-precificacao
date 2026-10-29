
import streamlit as st
from datetime import date
from io import BytesIO
from urllib.parse import quote
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

st.set_page_config(
    page_title="FIX | Precificação",
    page_icon="🏷️",
    layout="centered",
)

st.markdown("""
<style>
    .block-container {
        max-width: 980px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .fix-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0;
    }
    .fix-sub {
        color: #9ca3af;
        margin-top: 4px;
        font-size: 0.95rem;
    }
    .result-card {
        background: linear-gradient(135deg, #111827, #1f2937);
        padding: 20px;
        border-radius: 18px;
        border: 1px solid #374151;
        margin-bottom: 14px;
    }
    .result-label {
        color: #d1d5db;
        font-size: 0.9rem;
        margin-bottom: 4px;
    }
    .result-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.15;
    }
    .result-small {
        color: #f3f4f6;
        font-size: 1.2rem;
        font-weight: 700;
    }
    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 0.8rem;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

def moeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def moeda3(v):
    return f"R$ {v:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")

def valor_m2_por_quantidade(qtd: int):
    if 1 <= qtd <= 250:
        return 135.0
    elif qtd <= 500:
        return 125.0
    elif qtd <= 999:
        return 110.0
    elif qtd <= 1500:
        return 95.0
    return None

def gerar_pdf_cliente(dados):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _, h = A4

    y = h - 22*mm
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20*mm, y, "FIX Comunicação Visual")
    y -= 8*mm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(20*mm, y, "Cotação de Rótulos / Etiquetas")
    y -= 10*mm

    c.setFont("Helvetica", 10)
    linhas = [
        f"Cliente: {dados['cliente'] or '-'}",
        f"Vendedor: {dados['vendedor'] or '-'}",
        f"Data: {dados['data']}",
        f"Validade da proposta: {dados['validade']} dias",
        "",
        f"Medida: {dados['largura']:.1f} x {dados['altura']:.1f} cm",
        f"Quantidade: {dados['quantidade']}",
        f"Material: {dados['material']}",
        f"Laminação: {dados['laminacao']}",
        f"Tipo de corte: {dados['corte']}",
        "",
        f"Preço final: {moeda(dados['preco_final'])}",
        f"Preço unitário: {moeda3(dados['preco_unitario'])}",
    ]

    if dados["observacoes"].strip():
        linhas += ["", "Observações:", dados["observacoes"]]

    for linha in linhas:
        c.drawString(20*mm, y, linha)
        y -= 6*mm

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(20*mm, 18*mm, "FIX Comunicação Visual • Cotação comercial")
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# Cabeçalho
col_logo, col_txt = st.columns([0.75, 3.25], vertical_alignment="center")
with col_logo:
    st.image("logo_fix.png", width=135)
with col_txt:
    st.markdown('<div class="fix-title">Precificação FIX</div>', unsafe_allow_html=True)
    st.markdown('<div class="fix-sub">Rótulos e Etiquetas • uso interno de vendedores</div>', unsafe_allow_html=True)

st.divider()

st.markdown('<div class="section-title">Dados da cotação</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    cliente = st.text_input("Cliente")
    vendedor = st.text_input("Vendedor")
with c2:
    produto = st.selectbox("Produto", ["Rótulos / Etiquetas"])
    data_cotacao = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")

c1, c2, c3 = st.columns(3)
with c1:
    largura = st.number_input("Largura (cm)", min_value=0.1, value=4.0, step=0.1)
with c2:
    altura = st.number_input("Altura (cm)", min_value=0.1, value=4.0, step=0.1)
with c3:
    quantidade = st.number_input("Quantidade", min_value=1, value=1000, step=1)

c1, c2, c3 = st.columns(3)
with c1:
    material = st.selectbox(
        "Material",
        ["Vinil Branco", "Vinil Transparente", "BOPP", "Papel Couchê", "Papel Adesivo"]
    )
with c2:
    laminacao = st.selectbox(
        "Laminação",
        ["Sem laminação", "Laminação brilho", "Laminação fosca"]
    )
with c3:
    corte = st.selectbox("Tipo de corte", ["Contorno", "Reto", "Meio-corte"])

st.markdown('<div class="section-title">Condições comerciais</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    comissao_pct = st.number_input("Comissão (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
with c2:
    desconto_pct = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
with c3:
    validade = st.number_input("Validade da proposta (dias)", min_value=1, max_value=90, value=7, step=1)

observacoes = st.text_area("Observações", placeholder="Ex.: prazo de produção, retirada, acabamento especial...")

area_unitaria = (largura / 100) * (altura / 100)
area_total = area_unitaria * quantidade
valor_m2 = valor_m2_por_quantidade(int(quantidade))

st.divider()
st.markdown('<div class="section-title">Resultado</div>', unsafe_allow_html=True)

if valor_m2 is None:
    st.error("Quantidade acima de 1.500 unidades. Consulte a administração.")
else:
    preco_base = area_total * valor_m2
    adicional_laminacao_m2 = 30.0 if laminacao in ["Laminação brilho", "Laminação fosca"] else 0.0
    adicional_laminacao = area_total * adicional_laminacao_m2
    preco_bruto = preco_base + adicional_laminacao
    preco_final = preco_bruto * (1 - desconto_pct / 100)
    preco_unitario = preco_final / quantidade
    comissao_valor = preco_final * (comissao_pct / 100)

    c1, c2, c3 = st.columns([1.4, 1, 1])

    with c1:
        st.markdown(
            f'<div class="result-card"><div class="result-label">PREÇO FINAL</div>'
            f'<div class="result-value">{moeda(preco_final)}</div></div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f'<div class="result-card"><div class="result-label">PREÇO UNITÁRIO</div>'
            f'<div class="result-small">{moeda3(preco_unitario)}</div></div>',
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f'<div class="result-card"><div class="result-label">COMISSÃO</div>'
            f'<div class="result-small">{moeda(comissao_valor)}</div></div>',
            unsafe_allow_html=True
        )

    with st.expander("Detalhes da cotação"):
        st.write(f"**Área total:** {area_total:.2f} m²")
        st.write(f"**Valor base aplicado:** {moeda(valor_m2)}/m²")
        if adicional_laminacao_m2 > 0:
            st.write(f"**Adicional de laminação:** {moeda(adicional_laminacao_m2)}/m²")
            st.write(f"**Valor total da laminação:** {moeda(adicional_laminacao)}")
        st.write(f"**Comissão:** {comissao_pct:.1f}%")
        st.write(f"**Desconto:** {desconto_pct:.1f}%")

    whatsapp = f"""FIX COMUNICAÇÃO VISUAL

COTAÇÃO DE RÓTULOS / ETIQUETAS

Cliente: {cliente or "-"}
Data: {data_cotacao.strftime("%d/%m/%Y")}
Validade: {validade} dias

Medida: {largura:.1f} x {altura:.1f} cm
Quantidade: {quantidade}
Material: {material}
Laminação: {laminacao}
Tipo de corte: {corte}

PREÇO FINAL: {moeda(preco_final)}
PREÇO UNITÁRIO: {moeda3(preco_unitario)}
"""

    if observacoes.strip():
        whatsapp += f"\nObservações: {observacoes.strip()}\n"

    st.markdown("### Texto para WhatsApp")
    st.text_area("Prévia do texto", value=whatsapp, height=280)

    whatsapp_url = "https://api.whatsapp.com/send?text=" + quote(whatsapp)

    dados_pdf = {
        "cliente": cliente,
        "vendedor": vendedor,
        "data": data_cotacao.strftime("%d/%m/%Y"),
        "validade": validade,
        "largura": largura,
        "altura": altura,
        "quantidade": quantidade,
        "material": material,
        "laminacao": laminacao,
        "corte": corte,
        "preco_final": preco_final,
        "preco_unitario": preco_unitario,
        "observacoes": observacoes,
    }

    c1, c2 = st.columns(2)
    with c1:
        st.link_button(
            "Abrir no WhatsApp",
            whatsapp_url,
            use_container_width=True,
        )

    with c2:
        st.download_button(
            "Gerar PDF da cotação",
            data=gerar_pdf_cliente(dados_pdf),
            file_name="cotacao_fix.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

st.markdown('<div class="footer">FIX Comunicação Visual • Aplicativo interno de precificação</div>', unsafe_allow_html=True)
