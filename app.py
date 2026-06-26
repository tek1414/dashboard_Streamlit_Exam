import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_data

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------
st.set_page_config(
    page_title="Dashboard Analyse Client",
    page_icon="📊",
    layout="wide"
)

COULEURS = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD',
            '#8C564B', '#E377C2', '#17BECF', '#BCBD22', '#7F7F7F']

# -----------------------------------------
# CHARGEMENT DES DONNEES
# -----------------------------------------
df = load_data()

if df is not None:

    df['Delai Livraison'] = (df['Ship Date'] - df['Order Date']).dt.days
    df['Year'] = df['Order Date'].dt.year

    # -----------------------------------------
    # SIDEBAR : Filtres
    # -----------------------------------------
    st.sidebar.header("Filtres")

    liste_regions = ["Toutes"] + df['Region'].unique().tolist()
    region_choisie = st.sidebar.selectbox("Region :", liste_regions)

    liste_segments = ["Tous"] + df['Segment'].unique().tolist()
    segment_choisi = st.sidebar.selectbox("Segment :", liste_segments)

    # Application des filtres
    df_filtre = df.copy()
    if region_choisie != "Toutes":
        df_filtre = df_filtre[df_filtre['Region'] == region_choisie]
    if segment_choisi != "Tous":
        df_filtre = df_filtre[df_filtre['Segment'] == segment_choisi]

    # -----------------------------------------
    # TITRE PRINCIPAL
    # -----------------------------------------
    st.title("Dashboard Analyse Clientele - Superstore")
    st.markdown("Analyse de la rentabilite et du comportement client pour optimiser les campagnes marketing.")

    # -----------------------------------------
    # NAVIGATION PAR ONGLETS
    # -----------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "Vue Globale",
        "Analyse Clients",
        "Analyse Geographique",
        "Analyse Produits"
    ])

    # -----------------------------------------
    # ONGLET 1 : VUE GLOBALE
    # -----------------------------------------
    with tab1:
        st.subheader("Vue Globale")
        st.markdown("Vue d'ensemble des performances commerciales de l'entreprise.")
        st.divider()

        # Calculs KPIs
        ca_total             = df_filtre['Sales'].sum()
        profit_total         = df_filtre['Profit'].sum()
        nb_commandes         = df_filtre['Order ID'].nunique()
        nb_clients           = df_filtre['Customer ID'].nunique()
        marge                = (profit_total / ca_total * 100) if ca_total > 0 else 0
        panier_moyen         = ca_total / nb_commandes if nb_commandes > 0 else 0
        remise_moyenne       = df_filtre['Discount'].mean() * 100
        delai_moyen          = df_filtre['Delai Livraison'].mean()
        ca_par_client        = ca_total / nb_clients if nb_clients > 0 else 0
        commandes_par_client = nb_commandes / nb_clients if nb_clients > 0 else 0

        # KPIs ligne 1
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Chiffre d'Affaires",  f"${ca_total:,.0f}")
        col2.metric("Profit Net",           f"${profit_total:,.0f}")
        col3.metric("Taux de Marge",        f"{marge:.1f}%")
        col4.metric("Panier Moyen",         f"${panier_moyen:,.0f}")
        col5.metric("Nb Commandes",         f"{nb_commandes:,}")

        # KPIs ligne 2
        col6, col7, col8, col9, col10 = st.columns(5)
        col6.metric("Clients Uniques",       f"{nb_clients:,}")
        col7.metric("CA par Client",          f"${ca_par_client:,.0f}")
        col8.metric("Commandes par Client",  f"{commandes_par_client:.1f}")
        col9.metric("Remise Moyenne",        f"{remise_moyenne:.1f}%")
        col10.metric("Delai Livraison Moy.", f"{delai_moyen:.0f} jours")

        st.divider()

        # Evolution mensuelle
        st.subheader("Evolution mensuelle des Ventes et du Profit")
        df_temps = df_filtre.copy()
        df_temps['Mois'] = df_temps['Order Date'].dt.to_period('M').astype(str)
        df_temps_agg = df_temps.groupby('Mois').agg(
            Ventes=('Sales', 'sum'),
            Profit=('Profit', 'sum')
        ).reset_index()

        fig_temps = go.Figure()
        fig_temps.add_trace(go.Scatter(
            x=df_temps_agg['Mois'], y=df_temps_agg['Ventes'],
            name='Ventes', line=dict(color='#1F77B4', width=2),
            fill='tozeroy', fillcolor='rgba(31,119,180,0.1)'
        ))
        fig_temps.add_trace(go.Scatter(
            x=df_temps_agg['Mois'], y=df_temps_agg['Profit'],
            name='Profit', line=dict(color='#2CA02C', width=2)
        ))
        fig_temps.update_layout(xaxis_title="Mois", yaxis_title="Montant ($)")
        st.plotly_chart(fig_temps, use_container_width=True)

        st.divider()

        # Performance par categorie
        st.subheader("Performance par Categorie")
        df_cat = df_filtre.groupby('Category').agg(
            Ventes=('Sales', 'sum'),
            Profit=('Profit', 'sum')
        ).reset_index()
        df_cat['Marge (%)'] = (df_cat['Profit'] / df_cat['Ventes'] * 100).round(1)

        col1, col2, col3 = st.columns(3)
        with col1:
            fig = px.bar(df_cat, x='Category', y='Ventes', title="Ventes par Categorie",
                         color='Category', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(df_cat, x='Category', y='Profit', title="Profit par Categorie",
                         color='Category', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col3:
            fig = px.bar(df_cat, x='Category', y='Marge (%)', title="Taux de Marge par Categorie",
                         color='Category', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------
    # ONGLET 2 : ANALYSE CLIENTS
    # -----------------------------------------
    with tab2:
        st.subheader("Analyse Clients")
        st.markdown("Identification des clients a fort potentiel et analyse par segment.")
        st.divider()

        ca_total             = df_filtre['Sales'].sum()
        profit_total         = df_filtre['Profit'].sum()
        nb_clients           = df_filtre['Customer ID'].nunique()
        nb_commandes         = df_filtre['Order ID'].nunique()
        ca_par_client        = ca_total / nb_clients if nb_clients > 0 else 0
        profit_par_client    = profit_total / nb_clients if nb_clients > 0 else 0
        commandes_par_client = nb_commandes / nb_clients if nb_clients > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Clients Uniques",       f"{nb_clients:,}")
        col2.metric("Commandes par Client",  f"{commandes_par_client:.1f}")
        col3.metric("CA Moyen par Client",   f"${ca_par_client:,.0f}")
        col4.metric("Profit Moyen par Client", f"${profit_par_client:,.0f}")

        st.divider()

        # Top 10 clients
        st.subheader("Top 10 Clients")
        col1, col2 = st.columns(2)
        with col1:
            top_ca = df_filtre.groupby('Customer Name')['Sales'].sum()\
                               .sort_values(ascending=True).tail(10).reset_index()
            fig = px.bar(top_ca, x='Sales', y='Customer Name', orientation='h',
                         title="Par Chiffre d'Affaires",
                         color='Customer Name', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            top_profit = df_filtre.groupby('Customer Name')['Profit'].sum()\
                                   .sort_values(ascending=True).tail(10).reset_index()
            fig = px.bar(top_profit, x='Profit', y='Customer Name', orientation='h',
                         title="Par Profit",
                         color='Customer Name', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Analyse par segment
        st.subheader("Analyse par Segment")
        df_seg = df_filtre.groupby('Segment').agg(
            Ventes=('Sales', 'sum'),
            Profit=('Profit', 'sum'),
            Clients=('Customer ID', 'nunique'),
            Commandes=('Order ID', 'nunique')
        ).reset_index()
        df_seg['Marge (%)']       = (df_seg['Profit'] / df_seg['Ventes'] * 100).round(1)
        df_seg['CA Moyen/Client'] = (df_seg['Ventes'] / df_seg['Clients']).round(0)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df_seg, values='Ventes', names='Segment',
                         title="Repartition du CA par Segment",
                         color_discrete_sequence=COULEURS, hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(df_seg, x='Segment', y='Marge (%)',
                         title="Taux de Marge par Segment",
                         color='Segment', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Top clients par nb commandes
        st.subheader("Top 10 Clients par Nombre de Commandes")
        top_cmd = df_filtre.groupby('Customer Name')['Order ID'].nunique()\
                            .sort_values(ascending=True).tail(10).reset_index()
        top_cmd.columns = ['Customer Name', 'Nb Commandes']
        fig = px.bar(top_cmd, x='Nb Commandes', y='Customer Name', orientation='h',
                     color='Customer Name', color_discrete_sequence=COULEURS)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Tableau recap
        st.subheader("Tableau Recapitulatif par Segment")
        st.dataframe(df_seg, use_container_width=True)

    # -----------------------------------------
    # ONGLET 3 : ANALYSE GEOGRAPHIQUE
    # -----------------------------------------
    with tab3:
        st.subheader("Analyse Geographique")
        st.markdown("Identification des zones geographiques les plus rentables.")
        st.divider()

        col1, col2, col3 = st.columns(3)
        col1.metric("Regions",  df_filtre['Region'].nunique())
        col2.metric("Etats",    df_filtre['State'].nunique())
        col3.metric("Villes",   df_filtre['City'].nunique())

        st.divider()

        # Par region
        st.subheader("Performance par Region")
        df_region = df_filtre.groupby('Region').agg(
            Ventes=('Sales', 'sum'),
            Profit=('Profit', 'sum'),
            Clients=('Customer ID', 'nunique')
        ).reset_index()
        df_region['Marge (%)'] = (df_region['Profit'] / df_region['Ventes'] * 100).round(1)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df_region, x='Region', y='Profit', title="Profit par Region",
                         color='Region', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(df_region, x='Region', y='Marge (%)', title="Taux de Marge par Region",
                         color='Region', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Top Etats et Villes
        st.subheader("Zoom par Etat et Ville")
        col1, col2 = st.columns(2)
        with col1:
            df_etats = df_filtre.groupby('State')['Profit'].sum()\
                                 .sort_values(ascending=True).tail(10).reset_index()
            fig = px.bar(df_etats, x='Profit', y='State', orientation='h',
                         title="Top 10 Etats les plus Rentables",
                         color='State', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            df_villes = df_filtre.groupby('City')['Sales'].sum()\
                                  .sort_values(ascending=True).tail(10).reset_index()
            fig = px.bar(df_villes, x='Sales', y='City', orientation='h',
                         title="Top 10 Villes par CA",
                         color='City', color_discrete_sequence=COULEURS)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------
    # ONGLET 4 : ANALYSE PRODUITS
    # -----------------------------------------
    with tab4:
        st.subheader("Analyse Produits")
        st.markdown("Analyse des categories, sous-categories et impact des remises.")
        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Produits Distincts", f"{df_filtre['Product ID'].nunique():,}")
        col2.metric("Quantites Vendues",  f"{df_filtre['Quantity'].sum():,}")
        col3.metric("CA Total",           f"${df_filtre['Sales'].sum():,.0f}")
        col4.metric("Remise Moyenne",     f"{df_filtre['Discount'].mean()*100:.1f}%")

        st.divider()

        # Par sous-categorie
        st.subheader("Performance par Sous-Categorie")
        df_subcat = df_filtre.groupby(['Category', 'Sub-Category']).agg(
            Ventes=('Sales', 'sum'),
            Profit=('Profit', 'sum')
        ).reset_index()

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df_subcat.sort_values('Ventes', ascending=True),
                         x='Ventes', y='Sub-Category', orientation='h',
                         color='Category', title="Ventes par Sous-Categorie",
                         color_discrete_sequence=COULEURS)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(df_subcat.sort_values('Profit', ascending=True),
                         x='Profit', y='Sub-Category', orientation='h',
                         color='Category', title="Profit par Sous-Categorie",
                         color_discrete_sequence=COULEURS)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Top 10 produits
        st.subheader("Top 10 Produits les plus Vendus")
        top_prod = df_filtre.groupby('Product Name')['Sales'].sum()\
                             .sort_values(ascending=True).tail(10).reset_index()
        fig = px.bar(top_prod, x='Sales', y='Product Name', orientation='h',
                     color='Product Name', color_discrete_sequence=COULEURS)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Impact des remises
        st.subheader("Impact des Remises sur le Profit")
        fig = px.scatter(df_filtre, x='Discount', y='Profit', color='Category',
                         title="Relation entre Remise et Profit",
                         color_discrete_sequence=COULEURS, opacity=0.6)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Donnees brutes
        with st.expander("Voir les donnees brutes filtrees"):
            st.dataframe(df_filtre.sort_values(by='Order Date', ascending=False),
                         use_container_width=True)

else:
    st.error("Impossible de charger les donnees. Verifiez l'emplacement du fichier CSV.")