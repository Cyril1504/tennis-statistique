import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Tennis Tracker Mobile", layout="centered", page_icon="🎾")

if 'match_data' not in st.session_state: st.session_state.match_data = []
if 'score' not in st.session_state:
    st.session_state.score = {"pA_points": 0, "pB_points": 0, "pA_jeux": 0, "pB_jeux": 0, "pA_sets": 0, "pB_sets": 0, "in_tiebreak": False}
if 'score_history' not in st.session_state: st.session_state.score_history = []

st.sidebar.header("⚙️ Configuration")
player_a = st.sidebar.text_input("Joueur A", value="Joueur A")
player_b = st.sidebar.text_input("Joueur B", value="Joueur B")

if st.sidebar.button("🗑️ Réinitialiser le match", type="primary"):
    st.session_state.match_data, st.session_state.score_history = [], []
    st.session_state.score = {"pA_points": 0, "pB_points": 0, "pA_jeux": 0, "pB_jeux": 0, "pA_sets": 0, "pB_sets": 0, "in_tiebreak": False}
    st.rerun()

def update_score(winner):
    sc = st.session_state.score
    st.session_state.score_history.append(sc.copy())
    if winner == player_a: sc["pA_points"] += 1
    else: sc["pB_points"] += 1
    
    if sc["in_tiebreak"]:
        if sc["pA_points"] >= 7 and (sc["pA_points"] - sc["pB_points"]) >= 2:
            sc["pA_sets"] += 1; sc["pA_jeux"], sc["pB_jeux"] = 0, 0
            sc["pA_points"], sc["pB_points"] = 0, 0; sc["in_tiebreak"] = False
        elif sc["pB_points"] >= 7 and (sc["pB_points"] - sc["pA_points"]) >= 2:
            sc["pB_sets"] += 1; sc["pA_jeux"], sc["pB_jeux"] = 0, 0
            sc["pA_points"], sc["pB_points"] = 0, 0; sc["in_tiebreak"] = False
    else:
        if sc["pA_points"] >= 4 and (sc["pA_points"] - sc["pB_points"]) >= 2: sc["pA_jeux"] += 1; sc["pA_points"], sc["pB_points"] = 0, 0
        elif sc["pB_points"] >= 4 and (sc["pB_points"] - sc["pA_points"]) >= 2: sc["pB_jeux"] += 1; sc["pA_points"], sc["pB_points"] = 0, 0
        if sc["pA_jeux"] == 6 and sc["pB_jeux"] == 6: sc["in_tiebreak"] = True
        elif sc["pA_jeux"] >= 6 and (sc["pA_jeux"] - sc["pB_jeux"]) >= 2: sc["pA_sets"] += 1; sc["pA_jeux"], sc["pB_jeux"] = 0, 0
        elif sc["pB_jeux"] >= 6 and (sc["pB_jeux"] - sc["pA_jeux"]) >= 2: sc["pB_sets"] += 1; sc["pA_jeux"], sc["pB_jeux"] = 0, 0

def undo_last_point():
    if st.session_state.match_data and st.session_state.score_history:
        st.session_state.match_data.pop()
        st.session_state.score = st.session_state.score_history.pop()
        st.toast("↩️ Point annulé !", icon="✅")

def get_pts(pa, pb, in_tb):
    if in_tb: return str(pa), str(pb)
    if pa >= 3 and pb >= 3:
        if pa == pb: return "40", "40"
        return ("Av", "40") if pa > pb else ("40", "Av")
    return {0:"0", 1:"15", 2:"30", 3:"40"}[pa], {0:"0", 1:"15", 2:"30", 3:"40"}[pb]

# --- AFFICHAGE DES SCORES MOBILE COMPACT ---
sc = st.session_state.score
pt_a, pt_b = get_pts(sc["pA_points"], sc["pB_points"], sc["in_tiebreak"])

if sc["in_tiebreak"]:
    st.warning("⚠️ MODE TIE-BREAK EN COURS", icon="🎾")

# Grille de score ultra-lisible sans HTML complexe
c_a, c_b = st.columns(2)
with c_a:
    st.metric(label=f"🔴 {player_a}", value=f"Points : {pt_a}", delta=f"Sets: {sc['pA_sets']} | Jeux: {sc['pA_jeux']}", delta_color="off")
with c_b:
    st.metric(label=f"🔵 {player_b}", value=f"Points : {pt_b}", delta=f"Sets: {sc['pB_sets']} | Jeux: {sc['pB_jeux']}", delta_color="off")

tab1, tab2, tab3 = st.tabs(["🕹️ Tracker", "📊 Radar", "📋 Données"])

with tab1:
    def log_event(w, p, t, s="N/A"):
        update_score(w)
        st.session_state.match_data.append({"Gagnant du point": w, "Joueur ayant fait l'action/erreur": p, "Type d'action": t, "Côté du coup": s})
        st.rerun()
        
    if st.button("↩️ Annuler le coup précédent", use_container_width=True, disabled=len(st.session_state.match_data) == 0):
        undo_last_point(); st.rerun()
        
    col_pA, col_pB = st.columns(2)
    
    with col_pA:
        st.markdown(f"<p style='text-align:center;font-weight:bold;color:#ef553b;margin:5px 0;'>Commandes {player_a}</p>", unsafe_html=True)
        sub1, sub2 = st.columns(2)
        if sub1.button("🔥 CD", key="w_cd_a", use_container_width=True): log_event(player_a, player_a, "Winner", "Coup Droit")
        if sub2.button("🔥 REV", key="w_rev_a", use_container_width=True): log_event(player_a, player_a, "Winner", "Revers")
        
        sub3, sub4 = st.columns(2)
        if sub3.button("📉 CD Fault", key="ue_cd_a", use_container_width=True): log_event(player_b, player_a, "Faute Directe", "Coup Droit")
        if sub4.button("📉 REV Fault", key="ue_rev_a", use_container_width=True): log_event(player_b, player_a, "Faute Directe", "Revers")
        
        sub5, sub6 = st.columns(2)
        if sub5.button("🛡️ CD Prov", key="fe_cd_a", use_container_width=True): log_event(player_b, player_a, "Faute Provoquée", "Coup Droit")
        if sub6.button("🛡️ REV Prov", key="fe_rev_a", use_container_width=True): log_event(player_b, player_a, "Faute Provoquée", "Revers")
        
        if st.button("🎯 Ace", key="ace_a", use_container_width=True): log_event(player_a, player_a, "Ace", "Service")
        if st.button("❌ Dbl Faute", key="df_a", use_container_width=True): log_event(player_b, player_a, "Double Faute", "Service")

    with col_pB:
        st.markdown(f"<p style='text-align:center;font-weight:bold;color:#636efa;margin:5px 0;'>Commandes {player_b}</p>", unsafe_html=True)
        sub1, sub2 = st.columns(2)
        if sub1.button("🔥 CD ", key="w_cd_b", use_container_width=True): log_event(player_b, player_b, "Winner", "Coup Droit")
        if sub2.button("🔥 REV ", key="w_rev_b", use_container_width=True): log_event(player_b, player_b, "Winner", "Revers")
        
        sub3, sub4 = st.columns(2)
        if sub3.button("📉 CD Fault ", key="ue_cd_b", use_container_width=True): log_event(player_a, player_b, "Faute Directe", "Coup Droit")
        if sub4.button("📉 REV Fault ", key="ue_rev_b", use_container_width=True): log_event(player_a, player_b, "Faute Directe", "Revers")
        
        sub5, sub6 = st.columns(2)
        if sub5.button("🛡️ CD Prov ", key="fe_cd_b", use_container_width=True): log_event(player_a, player_b, "Faute Provoquée", "Coup Droit")
        if sub6.button("🛡️ REV Prov ", key="fe_rev_b", use_container_width=True): log_event(player_a, player_b, "Faute Provoquée", "Revers")
        
        if st.button("🎯 Ace ", key="ace_b", use_container_width=True): log_event(player_b, player_b, "Ace", "Service")
        if st.button("❌ Dbl Faute ", key="df_b", use_container_width=True): log_event(player_a, player_b, "Double Faute", "Service")

df = pd.DataFrame(st.session_state.match_data)
with tab2:
    if df.empty: st.info("Enregistrez des points pour générer le radar.")
    else:
        def calc(p, t, c): return len(df[(df["Joueur ayant fait l'action/erreur"] == p) & (df["Type d'action"] == t) & (df["Côté du coup"] == c)])
        w_cd_a, w_rev_a = calc(player_a, "Winner", "Coup Droit"), calc(player_a, "Winner", "Revers")
        ue_cd_a, ue_rev_a = calc(player_a, "Faute Directe", "Coup Droit"), calc(player_a, "Faute Directe", "Revers")
        fe_cd_a, fe_rev_a = calc(player_a, "Faute Provoquée", "Coup Droit"), calc(player_a, "Faute Provoquée", "Revers")
        w_cd_b, w_rev_b = calc(player_b, "Winner", "Coup Droit"), calc(player_b, "Winner", "Revers")
        ue_cd_b, ue_rev_b = calc(player_b, "Faute Directe", "Coup Droit"), calc(player_b, "Faute Directe", "Revers")
        fe_cd_b, fe_rev_b = calc(player_b, "Faute Provoquée", "Coup Droit"), calc(player_b, "Faute Provoquée", "Revers")
        
        categories = ['Win CD', 'Win REV', 'Faute CD', 'Faute REV', 'Prov CD', 'Prov REV']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[w_cd_a, w_rev_a, ue_cd_a, ue_rev_a, fe_cd_a, fe_rev_a], theta=categories, fill='toself', name=player_a, line_color="#ef553b"))
        fig.add_trace(go.Scatterpolar(r=[w_cd_b, w_rev_b, ue_cd_b, ue_rev_b, fe_cd_b, fe_rev_b], theta=categories, fill='toself', name=player_b, line_color="#636efa"))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False)), margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True, key="mobile_radar")

with tab3:
    if df.empty: st.info("Aucun point collecté. Saisissez vos données dans le premier onglet pour activer l'export.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("### 💾 Rapport Excel")
        
        ace_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Ace")])
        df_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Double Faute")])
        ace_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Ace")])
        df_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Double Faute")])
        
        w_cd_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Winner") & (df["Côté du coup"] == "Coup Droit")])
        w_rev_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Winner") & (df["Côté du coup"] == "Revers")])
        ue_cd_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Faute Directe") & (df["Côté du coup"] == "Coup Droit")])
        ue_rev_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Faute Directe") & (df["Côté du coup"] == "Revers")])
        fe_cd_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Faute Provoquée") & (df["Côté du coup"] == "Coup Droit")])
        fe_rev_a = len(df[(df["Joueur ayant fait l'action/erreur"] == player_a) & (df["Type d'action"] == "Faute Provoquée") & (df["Côté du coup"] == "Revers")])
        w_cd_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Winner") & (df["Côté du coup"] == "Coup Droit")])
        w_rev_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Winner") & (df["Côté du coup"] == "Revers")])
        ue_cd_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Faute Directe") & (df["Côté du coup"] == "Coup Droit")])
        ue_rev_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Faute Directe") & (df["Côté du coup"] == "Revers")])
        fe_cd_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Faute Provoquée") & (df["Côté du coup"] == "Coup Droit")])
        fe_rev_b = len(df[(df["Joueur ayant fait l'action/erreur"] == player_b) & (df["Type d'action"] == "Faute Provoquée") & (df["Côté du coup"] == "Revers")])

        summary_data = {
            "Indicateur Metrique": [
                "Aces", "Double Fautes", "Winners Coup Droit", "Winners Revers",
                "Fautes Directes Coup Droit", "Fautes Directes Revers",
                "Fautes Provoquees Coup Droit", "Fautes Provoquees Revers"
            ],
            player_a: [ace_a, df_a, w_cd_a, w_rev_a, ue_cd_a, ue_rev_a, fe_cd_a, fe_rev_a],
            player_b: [ace_b, df_b, w_cd_b, w_rev_b, ue_cd_b, ue_rev_b, fe_cd_b, fe_rev_b]
        }
        df_summary_excel = pd.DataFrame(summary_data)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_summary_excel.to_excel(writer, sheet_name='Synthese Globale', index=False)
            df.to_excel(writer, sheet_name='Journal Point par Point', index=False)
            
        st.download_button(
            label="📥 Télécharger le rapport (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name=f"rapport_tennis_{player_a}vs{player_b}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
