
import streamlit as st
from datetime import date

st.set_page_config(
    page_title="FIX | Precificação de Rótulos e Etiquetas",
    page_icon="🏷️",
    layout="centered",
)

# ---------- Estilo ----------
st.markdown("""
<style>
    .block-container {max-width: 900px; padding-top: 1.2rem; padding-bottom: 2rem;}
    .fix-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 4px 18px rgba(0,0,0,.06);
        margin-bottom: 16px;
    }
    .fix-result {
        background: #111827;
        color: white;
        border-radius: 18px;
        padding: 20px;
        margin-top: 10px;
    }
    .fix-result h2, .fix-result h3, .fix-result p {color: white;}
    .price-big {font-size: 2.2rem; font-weight: 800; margin: 0;}
    .muted {color: #6b7280;}
    div[data-testid="stMetricValue"] {font-size: 1.6rem;}
</style>
""", unsafe_allow_html=True)

# ---------- Cabeçalho ----------
col_logo, col_title = st.columns([1, 2.4], vertical_alignment="center")
with col_logo:
    st.image("logo_fix.png", use_container_width=True)
with col_title:
    st.title("Precificação FIX")
    st.caption("Rótulos e Etiquetas • uso interno de vendedores")

st.divider()

# ---------- Dados ----------
st.subheader("Dados da cotação")

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
    corte = st.selectbox(
        "Tipo de corte",
        ["Contorno", "Reto", "Meio-corte"]
    )

st.subheader("Condições comerciais")
c1, c2 = st.columns(2)
with c1:
    comissao_pct = st.number_input("Comissão (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
with c2:
    desconto_pct = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)

# ---------- Regra FIX ----------
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

area_unitaria = (largura / 100) * (altura / 100)
area_total = area_unitaria * quantidade
valor_m2 = valor_m2_por_quantidade(int(quantidade))

st.divider()
st.subheader("Resultado")

if valor_m2 is None:
    st.error("Quantidade acima de 1.500 unidades. Consulte a administração para definir o valor.")
else:
    preco_bruto = area_total * valor_m2
    preco_final = preco_bruto * (1 - desconto_pct / 100)
    preco_unitario = preco_final / quantidade
    comissao_valor = preco_final * (comissao_pct / 100)

    m1, m2, m3 = st.columns(3)
    m1.metric("Preço final", f"R$ {preco_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    m2.metric("Preço unitário", f"R$ {preco_unitario:,.3f}".replace(",", "X").replace(".", ",").replace("X", "."))
    m3.metric("Comissão", f"R$ {comissao_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    with st.expander("Detalhes comerciais"):
        st.write(f"**Área total:** {area_total:.2f} m²")
        st.write(f"**Valor aplicado:** R$ {valor_m2:.2f}/m²")
        st.write(f"**Comissão:** {comissao_pct:.1f}%")
        st.write(f"**Desconto:** {desconto_pct:.1f}%")

    def moeda(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    resumo = f"""FIX COMUNICAÇÃO VISUAL
COTAÇÃO DE RÓTULOS / ETIQUETAS

Cliente: {cliente or "-"}
Vendedor: {vendedor or "-"}
Data: {data_cotacao.strftime("%d/%m/%Y")}

Medida: {largura:.1f} x {altura:.1f} cm
Quantidade: {quantidade}
Material: {material}
Laminação: {laminacao}
Corte: {corte}

PREÇO FINAL: {moeda(preco_final)}
PREÇO UNITÁRIO: {moeda(preco_unitario)}
COMISSÃO ({comissao_pct:.1f}%): {moeda(comissao_valor)}
"""

    st.download_button(
        "Baixar resumo da cotação",
        data=resumo.encode("utf-8"),
        file_name="cotacao_fix.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.caption("FIX Comunicação Visual • Aplicativo interno de precificação")
