import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


st.set_page_config(page_title="Startups Unicórnio até Setembro de 2022", layout="wide")
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center;'>
        <div style='font-size: 80px; line-height: 1;'>🦄</div>
        <h1 style='color:#00FFFF; margin-top: 0;'>Startups Unicórnio até Setembro de 2022</h1>
        <h6 style='color:#00FFFF; margin-top: -10px; font-weight: normal;'>
            Análise exploratória baseada em dados do Kaggle
        </h6>
    </div>
""", unsafe_allow_html=True)

with st.expander("📘 O que é uma startup unicórnio?"):
    st.markdown("""
    Uma *startup unicórnio* é uma empresa privada de base tecnológica avaliada em mais de **1 bilhão de dólares**,
    geralmente sem capital aberto na bolsa. Elas costumam se destacar pela inovação e crescimento acelerado.
    """)


try:
    df = pd.read_csv("data/unicorns.csv")
except FileNotFoundError:
    st.error("Arquivo 'data/unicorns.csv' não encontrado. Por favor, coloque o arquivo na pasta /data.")
    st.stop()


df.columns = df.columns.str.strip()
df.rename(columns={
    'Company': 'Empresa',
    'Valuation ($B)': 'Valor ($)',
    'Date Joined': 'Data de Adesão',
    'Country': 'País',
    'City': 'Cidade',
    'Industry': 'Setor',
    'Investors': 'Investidores',
}, inplace=True)


df['Setor'] = df['Setor'].str.strip().str.title()
df['Setor'] = df['Setor'].replace({
    'Fin Tech': 'Fintech',
    'Financial Technology': 'Fintech',
    'Internet': 'Internet Software & Services',
    'Artificial Intelligence': 'Artificial Intelligence',
    'Artificial intelligence': 'Artificial Intelligence',
})


df = df[~df['Setor'].str.contains(',', na=False)]


df['Valor ($)'] = df['Valor ($)'].replace('[\$,]', '', regex=True).astype(float)
df['Data de Adesão'] = pd.to_datetime(df['Data de Adesão'])
df['Ano'] = df['Data de Adesão'].dt.year


with st.sidebar:
    st.header("Filtros Gerais")
    anos = df['Ano'].sort_values().unique()
    ano_min, ano_max = int(anos.min()), int(anos.max())
    intervalo_anos = st.slider("Filtrar por ano de adesão", ano_min, ano_max, (ano_min, ano_max))

    top_10_paises = df['País'].value_counts().head(10).index.tolist()
    paises = st.multiselect(
        "Selecione os países para análise",
        options=sorted(df['País'].unique()),
        default=top_10_paises,
        help="Os 10 países com mais unicórnios são pré-selecionados. Você pode incluir outros se desejar."
    )

    setores = st.multiselect(
        "Selecione os setores",
        options=sorted(df['Setor'].unique()),
        default=sorted(df['Setor'].unique())
    )

    st.header("Comparação entre países")
    paises_comparar = st.multiselect(
        "Escolha até 3 países para comparar",
        options=sorted(df['País'].unique()),
        default=top_10_paises[:2],
        max_selections=3
    )


df_filtrado = df[
    (df['Ano'] >= intervalo_anos[0]) &
    (df['Ano'] <= intervalo_anos[1]) &
    (df['País'].isin(paises)) &
    (df['Setor'].isin(setores))
]


col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Startups", df_filtrado.shape[0])
col2.metric("Valor Médio (B$)", f"{df_filtrado['Valor ($)'].mean():.2f}" if not df_filtrado.empty else "N/A")
col3.metric("País com mais startups", df_filtrado['País'].mode()[0] if not df_filtrado.empty else "N/A")
col4.metric("Setor mais comum", df_filtrado['Setor'].mode()[0] if not df_filtrado.empty else "N/A")


st.subheader("Distribuição de Unicórnios por Setor")
df_setor = df_filtrado['Setor'].value_counts().reset_index()
df_setor.columns = ['Setor', 'Quantidade']
fig_setor = px.bar(df_setor, x='Setor', y='Quantidade',
                   color='Quantidade', color_continuous_scale='Viridis',
                   labels={'Quantidade': 'Número de Unicórnios', 'Setor': 'Setor'},
                   title="Unicórnios por Setor")
st.plotly_chart(fig_setor, use_container_width=True)


st.subheader("Percentual de Unicórnios por País")
df_pais = round(df_filtrado['País'].value_counts(normalize=True) * 100, 1).reset_index()
df_pais.columns = ['País', 'Percentual']
fig_pais = px.bar(df_pais, x='País', y='Percentual',
                  color='Percentual', color_continuous_scale='Magma',
                  labels={'Percentual': 'Porcentagem (%)', 'País': 'País'},
                  title="Percentual de Unicórnios por País")
st.plotly_chart(fig_pais, use_container_width=True)


st.subheader("Evolução de Unicórnios por Ano")
evolucao = df_filtrado['Ano'].value_counts().sort_index().reset_index()
evolucao.columns = ['Ano', 'Total']
fig_evo = px.line(evolucao, x='Ano', y='Total', title="Unicórnios por Ano")
st.plotly_chart(fig_evo, use_container_width=True)


if paises_comparar:
    df_comp = df_filtrado[df_filtrado['País'].isin(paises_comparar)]
    val_medios = df_comp.groupby('País')['Valor ($)'].mean().sort_values(ascending=False)

    st.subheader("Valor médio por país selecionado")
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    sns.barplot(x=val_medios.index, y=val_medios.values, palette='coolwarm', ax=ax4)
    ax4.set_ylabel("Valor Médio (Bilhões $)")
    ax4.set_xticklabels(val_medios.index, rotation=45, ha='right', fontsize=9)
    fig4.tight_layout()
    st.pyplot(fig4)

    st.subheader("Evolução do valor médio por ano")
    val_ano = df_comp.groupby(['Ano', 'País'])['Valor ($)'].mean().unstack()
    st.line_chart(val_ano)


st.subheader("Top 10 empresas com maior valor")
top_empresas = df_filtrado.sort_values(by='Valor ($)', ascending=False).head(10)
st.dataframe(top_empresas[['Empresa', 'País', 'Valor ($)', 'Setor']])


st.subheader("💼 Principais investidores em startups")


todos_investidores = df_filtrado['Investidores'].dropna().str.split(', ')
investidores_expandidos = todos_investidores.explode()
investidores_expandidos = investidores_expandidos.str.strip().str.title()

top_investidores = (
    investidores_expandidos.value_counts()
    .rename_axis('Investidor')
    .reset_index(name='Total')
    .head(15)
)

st.dataframe(top_investidores, use_container_width=True)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=top_investidores, y='Investidor', x='Total', palette='crest', ax=ax)
ax.set_title("Top 15 Investidores mais recorrentes")
ax.set_xlabel("Número de startups investidas")
ax.set_ylabel("Investidor")
st.pyplot(fig)


st.subheader("Setores preferidos dos principais investidores")
investidores_setores = df_filtrado[['Investidores', 'Setor']].dropna()
investidores_setores['Investidores'] = investidores_setores['Investidores'].str.split(', ')
investidores_setores = investidores_setores.explode('Investidores')

principais = investidores_setores['Investidores'].value_counts().head(10).index
dados_heatmap = investidores_setores[investidores_setores['Investidores'].isin(principais)]
tabela = pd.crosstab(dados_heatmap['Investidores'], dados_heatmap['Setor'])

fig_heat, ax_heat = plt.subplots(figsize=(12, 6))
sns.heatmap(tabela, cmap='YlGnBu', linewidths=0.5, annot=True, fmt='d', cbar_kws={'label': 'Nº de investimentos'})
ax_heat.set_title('Número de investimentos por investidor e setor')
st.pyplot(fig_heat)


st.subheader("🔍 Análise detalhada de um investidor específico")
todos_investidores = df_filtrado['Investidores'].dropna().str.split(', ')
investidores_unicos = pd.Series(todos_investidores.sum()).value_counts().index.tolist()

investidor_escolhido = st.selectbox("Selecione um investidor para análise", investidores_unicos)

df_investidor = df_filtrado[df_filtrado['Investidores'].str.contains(investidor_escolhido, na=False)]

if not df_investidor.empty:
    st.markdown(f"**Total de startups investidas por {investidor_escolhido}: {df_investidor.shape[0]}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.countplot(data=df_investidor, y='Setor', order=df_investidor['Setor'].value_counts().index, palette='flare')
    ax.set_title(f"Setores mais investidos por {investidor_escolhido}")
    ax.set_xlabel("Número de startups")
    ax.set_ylabel("Setor")
    st.pyplot(fig)
else:
    st.warning("Nenhuma startup encontrada para esse investidor.")


colab_url = "https://colab.research.google.com/drive/1W0gN4gGbEOIlmSJdU5RcGGO9Mq97SHhv?usp=sharing"
st.markdown(
    f"""
    <a href="{colab_url}" target="_blank" style="
        display: inline-block;
        border-radius: 12px;
        background-color: #00FFFF10;
        color: white;
        border: 1px solid #00FFFF50;
        padding: 8px 16px;
        font-weight: 600;
        text-decoration: none;
        cursor: pointer;
        margin-top: 10px;
        text-align: center;
        ">
        Abrir Google Colab
    </a>
    """,
    unsafe_allow_html=True,
)


with st.expander("🔍 Ver todos os dados filtrados"):
    st.dataframe(df_filtrado.reset_index(drop=True))


st.download_button("Baixar dados filtrados (CSV)",
                   data=df_filtrado.to_csv(index=False),
                   file_name="startups_filtradas.csv",
                   mime='text/csv')


st.markdown(
    """
    <style>
        .footer {
            position: relative;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 1rem 0;
            color: #888;
            font-size: 0.9rem;
        }
        .footer a {
            color: #00FFFF;
            text-decoration: none;
            margin: 0 15px;
            font-weight: bold;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
    <div class="footer">
        Desenvolvido por Kaique Henrique |
        <a href="https://github.com/kaiquehsp" target="_blank">GitHub</a> |
        <a href="https://linkedin.com/in/kaiquehenrique/" target="_blank">LinkedIn</a>
    </div>
    """,
    unsafe_allow_html=True
)
