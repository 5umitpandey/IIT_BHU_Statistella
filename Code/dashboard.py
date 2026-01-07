import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

COLOR_HOME = "#4CAF50"
COLOR_AWAY = "#F44336"
COLOR_EAST = "#1E88E5"
COLOR_WEST = "#E53935"
COLOR_LEAGUE = "#FFD700"


# Team primary/secondary color pairs
TEAM_COLORS = {
    "Hawks": ("#E03A3E", "#C1D32F"),
    "Celtics": ("#007A33", "#BA9653"),
    "Nets": ("#000000", "#FFFFFF"),
    "Hornets": ("#1D1160", "#00788C"),
    "Bulls": ("#CE1141", "#000000"),
    "Cavaliers": ("#860038", "#FDBB30"),
    "Mavericks": ("#00538C", "#B8C4CA"),
    "Nuggets": ("#0E2240", "#FEC524"),
    "Pistons": ("#C8102E", "#1D42BA"),
    "Warriors": ("#1D428A", "#FFC72C"),
    "Rockets": ("#CE1141", "#C4CED4"),
    "Pacers": ("#002D62", "#FDBB30"),
    "Clippers": ("#C8102E", "#1D428A"),
    "Lakers": ("#552583", "#FDB927"),
    "Grizzlies": ("#5D76A9", "#12173F"),
    "Heat": ("#98002E", "#F9A01B"),
    "Bucks": ("#00471B", "#EEE1C6"),
    "Timberwolves": ("#0C2340", "#236192"),
    "Pelicans": ("#0C2340", "#C8102E"),
    "Knicks": ("#006BB6", "#F58426"),
    "Thunder": ("#007AC1", "#EF3B24"),
    "Magic": ("#0077C0", "#C4CED4"),
    "76ers": ("#006BB6", "#ED174C"),
    "Suns": ("#1D1160", "#E56020"),
    "Trail Blazers": ("#E03A3E", "#000000"),
    "Kings": ("#5A2D81", "#63727A"),
    "Spurs": ("#C4CED4", "#000000"),
    "Raptors": ("#CE1141", "#000000"),
    "Jazz": ("#002B5C", "#F9A01B"),
    "Wizards": ("#002B5C", "#E31837")
}


# --------------------------------------------------
# 1. Load Data
# --------------------------------------------------
team_game_stats = pd.read_csv(
    resource_path("Processed_Data/team_game_stats.csv")
)

player_game_stats = pd.read_csv(
    resource_path("Processed_Data/player_game_stats.csv"),
    low_memory=False
)


team_game_stats["GAME_DATE_EST"] = pd.to_datetime(team_game_stats["GAME_DATE_EST"])
player_game_stats["GAME_DATE_EST"] = pd.to_datetime(player_game_stats["GAME_DATE_EST"])

# --------------------------------------------------
# 2. App Initialization
# --------------------------------------------------
app = Dash(__name__)
app.title = "Statistella | NBA Evolution Dashboard"

# ---------- KPI card style (used in layout) ----------
kpi_style = {
    "background": "#111",
    "color": "white",
    "padding": "20px",
    "borderRadius": "12px",
    "width": "18%",
    "textAlign": "center",
    "boxShadow": "0 0 10px rgba(0,0,0,0.5)"
}


# Add badge CSS to the app index
app.index_string += """
<style>
.badge {
    background: #222;
    color: gold;
    padding: 12px 18px;
    border-radius: 20px;
    font-weight: bold;
}
</style>
"""

# NOTE: badges will be rendered dynamically in the callback; remove static globals


# --------------------------------------------------
# 3. Helper Functions
# --------------------------------------------------
def center_text(text):
    return html.Div(
        text,
        style={
            "textAlign": "center",
            "color": "#cfd8dc",
            "marginBottom": "30px",
            "fontSize": "14px"
        }
    )


def section_header(title, subtitle):
    return html.Div([
        html.H2(title, style={"color": "white", "textAlign": "center"}),
        html.P(subtitle, style={"color": "#aaa", "maxWidth": "900px", "textAlign": "center", "margin": "0 auto"})
    ], style={"marginTop": "50px", "marginBottom": "20px", "textAlign": "center"})


def insight_box(text):
    return html.Div(
        text,
        style={
            "background": "#1c1c1c",
            "color": "white",
            "padding": "12px",
            "borderLeft": "4px solid #00c8ff",
            "marginTop": "10px",
            "textAlign": "center"
        }
    )


def legend_explanation(text):
    return html.Div(
        text,
        style={"color": "#bbb", "fontSize": "13px", "textAlign": "center", "maxWidth": "900px", "margin": "8px auto 24px"}
    )

# --------------------------------------------------
# 4. Layout
# --------------------------------------------------
app.layout = html.Div(
    style={
        "backgroundColor": "#0e1117",
        "padding": "20px",
        "fontFamily": "Arial",
    },
    children=[

        # ---------------- Title ----------------
        html.H1(
            "NBA Evolution & Performance Dashboard (FULLY DYNAMIC)",
            style={"textAlign": "center", "color": "white"}
        ),

        insight_box(
            "An interactive exploration of how scoring, teams, and players have shaped the modern NBA."
        ),

        
        # ---------------- Filters ----------------
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "center",
                "gap": "20px",
                "marginBottom": "30px"
            },
            children=[
                dcc.Dropdown(
                    id="season_filter",
                    options=[{"label": s, "value": s} for s in sorted(team_game_stats["SEASON"].unique())],
                    multi=True,
                    placeholder="Select Season",
                    style={"width": "200px"}
                ),
                dcc.Dropdown(
                    id="team_filter",
                    options=[{"label": t, "value": t} for t in sorted(team_game_stats["NICKNAME"].unique())],
                    multi=True,
                    placeholder="Select Team",
                    style={"width": "200px"}
                ),
                dcc.Dropdown(
                    id="player_filter",
                    options=[{"label": p, "value": p} for p in sorted(player_game_stats["PLAYER_NAME"].unique())],
                    multi=True,
                    placeholder="Select Player",
                    style={"width": "250px"}
                )
            ]
        ),

        # ---------- KPI CARDS (dynamic) ----------
        html.Div(id="kpi_container"),

        # ---------- Badges (dynamic) ----------
        html.Div(id="badges_container"),

        # SECTION 1 — LEAGUE EVOLUTION
        # ==================================================
        section_header(
            "League Evolution & Scoring Trends",
            "The modern NBA has steadily shifted toward faster pace, spacing, and higher offensive output."
        ),

        

        dcc.Graph(id="season_scoring_trend"),
        insight_box(
            "Scoring increased sharply after 2015, aligning with the league-wide three-point revolution."
        ),

        dcc.Graph(id="league_parity"),
        insight_box("Despite rising scores, the league has maintained competitive balance with median win rates near 50%."),

        dcc.Graph(id="home_away_trend"),
        insight_box("Home-court advantage remains strong, though the gap has narrowed in recent seasons."),

        html.Hr(),

        # ==================================================
        # SECTION 2 — TEAM & CONFERENCE ANALYSIS
        # ==================================================
        section_header(
            "Team & Conference Dynamics",
            "Analyzing team and conference-level trends to reveal sustained excellence and regional shifts."
        ),

        dcc.Graph(id="team_vs_league"),
        insight_box("Top franchises consistently outperform the league average, highlighting sustained organizational excellence."),
        
        dcc.Graph(id="dominant_seasons"),
        insight_box("Certain teams have had standout seasons, dominating the competition with exceptional win rates."),

        dcc.Graph(id="east_west"),
        insight_box("Eastern and Western Conferences show shifting dominance across different NBA eras."),

        dcc.Graph(id="team_consistency"),
        insight_box("Some teams avoid extreme score swings, indicating long-term stability and consistent execution."),
        html.Div(id="team_consistency_msg", style={"color": "#aaa", "textAlign": "center"}),

        dcc.Graph(id="most_successful_teams"),
        insight_box("A handful of franchises have dominated over the past two decades, setting the standard for success."),
        
        html.Hr(),

        # ==================================================
        # SECTION 3 — PLAYER INSIGHTS
        # ==================================================
        section_header(
            "Player Performance & Impact",
            "How player usage, efficiency, and archetypes drive individual and team success."
        ),

        dcc.Graph(id="player_archetypes"),
        insight_box("Players naturally fall into archetypes based on usage, efficiency, and role within a team."),

        dcc.Graph(id="high_scorers"),
        insight_box("True superstars separate themselves by consistently delivering 20+ point performances."),

        dcc.Graph(id="top_games"),
        insight_box("These games represent extreme individual dominance across scoring, rebounding, and playmaking."),

        dcc.Graph(id="most_successful_players"),
        insight_box("The most successful players combine high efficiency with significant playing time to impact games consistently."),   


        html.Footer(
                        "Team Name: ASHSUM | Data Source: NBA Official Datasets | Seasons 2004-2022 | Built for Statistella Hackathon",
                        style={
                            "color": "#777",
                            "textAlign": "center",
                            "marginTop": "50px",
                            "padding": "22px"
                        }
                    )

    ]
)

# --------------------------------------------------
# 5. Callbacks
# --------------------------------------------------
@app.callback(
    Output("kpi_container", "children"),
    Output("badges_container", "children"),
    Output("season_scoring_trend", "figure"),
    Output("league_parity", "figure"),
    Output("home_away_trend", "figure"),
    Output("team_vs_league", "figure"),
    Output("east_west", "figure"),
    Output("team_consistency", "figure"),
    Output("team_consistency_msg", "children"),
    Output("player_archetypes", "figure"),
    Output("high_scorers", "figure"),
    Output("top_games", "figure"),
    Output("most_successful_teams", "figure"),
    Output("dominant_seasons", "figure"),
    Output("most_successful_players", "figure"),

    Input("season_filter", "value"),
    Input("team_filter", "value"),
    Input("player_filter", "value")
)
def update_dashboard(season, team, player):

    df_team = team_game_stats.copy()
    df_player = player_game_stats.copy()

    if season:
        df_team = df_team[df_team["SEASON"].isin(season)]
        df_player = df_player[df_player["SEASON"].isin(season)]

    if team:
        df_team = df_team[df_team["NICKNAME"].isin(team)]
        df_player = df_player[df_player["NICKNAME"].isin(team)]

    if player:
        df_player = df_player[df_player["PLAYER_NAME"].isin(player)]

    
    # -------- Dynamic KPI cards & badges (update with filters) --------
    # Seasons text
    seasons = sorted(df_team["SEASON"].unique()) if "SEASON" in df_team.columns else []
    seasons_text = f"{seasons[0]} – {seasons[-1]}" if len(seasons) > 0 else "All Seasons"

    # Safe aggregations
    total_games = int(df_team["GAME_ID"].nunique()) if "GAME_ID" in df_team.columns else int(len(df_team))
    total_players = int(df_player["PLAYER_NAME"].nunique()) if "PLAYER_NAME" in df_player.columns else 0
    avg_pts = df_team["PTS"].mean() if not df_team.empty and "PTS" in df_team.columns else 0
    home_win_rate = (
        df_team[df_team["HOME_AWAY"] == "Home"]["WIN"].mean() * 100
        if ("HOME_AWAY" in df_team.columns and not df_team[df_team["HOME_AWAY"] == "Home"].empty)
        else 0
    )

    kpi_cards = html.Div([
        html.Div([html.H3(seasons_text), html.P("Seasons Covered")], style=kpi_style),
        html.Div([html.H3(f"{total_games:,}"), html.P("Total Games")], style=kpi_style),
        html.Div([html.H3(f"{total_players:,}"), html.P("Total Players")], style=kpi_style),
        html.Div([html.H3(f"{avg_pts:.1f}"), html.P("Avg Points / Game")], style=kpi_style),
        html.Div([html.H3(f"{home_win_rate:.1f}%"), html.P("Home Win Rate")], style=kpi_style),
    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "30px"})

    # Build color maps for teams and players — keep primary and secondary maps
    default_team_color = "#888888"
    team_primary_map = {}
    team_secondary_map = {}
    for t in sorted(df_team["NICKNAME"].dropna().unique()):
        try:
            cols = TEAM_COLORS.get(t)
            if cols:
                team_primary_map[t] = cols[0] if cols[0] else default_team_color
                # secondary falls back to primary when missing
                team_secondary_map[t] = cols[1] if len(cols) > 1 and cols[1] else team_primary_map[t]
            else:
                team_primary_map[t] = default_team_color
                team_secondary_map[t] = default_team_color
        except Exception:
            team_primary_map[t] = default_team_color
            team_secondary_map[t] = default_team_color

    # player -> team (choose most frequent current team for player in filtered df)
    player_primary_map = {}
    player_secondary_map = {}
    try:
        player_groups = df_player.groupby("PLAYER_NAME")
        for player_name, grp in player_groups:
            team_mode = None
            if "NICKNAME" in grp.columns:
                try:
                    team_mode = grp["NICKNAME"].mode().iloc[0]
                except Exception:
                    team_mode = None
            player_primary_map[player_name] = team_primary_map.get(team_mode, default_team_color)
            player_secondary_map[player_name] = team_secondary_map.get(team_mode, player_primary_map[player_name])
    except Exception:
        player_primary_map = {}
        player_secondary_map = {}

    # Helper to apply two-tone styling to a Plotly figure's traces
    def apply_two_tone(fig, primary_map, secondary_map):
        if fig is None:
            return
        for trace in fig.data:
            name = getattr(trace, 'name', None)
            # choose primary/secondary based on trace name (team/player)
            primary = primary_map.get(name)
            secondary = secondary_map.get(name)

            # If not found, try to fallback to a sensible default
            if primary is None:
                # safe access: trace.marker may be an object, not a dict
                primary = None
                if hasattr(trace, 'marker') and getattr(trace.marker, 'color', None) is not None:
                    primary = trace.marker.color
                elif hasattr(trace, 'line') and getattr(trace.line, 'color', None) is not None:
                    primary = trace.line.color
                else:
                    primary = default_team_color
            if secondary is None:
                secondary = primary

            # Apply for bar/marker traces
            try:
                if hasattr(trace, 'marker'):
                    trace.marker.color = primary
                    trace.marker.line = dict(color=secondary, width=3)
                # for line traces, set line color and marker outline
                if hasattr(trace, 'line'):
                    trace.line.color = primary
                    # ensure marker exists and has outline
                    if hasattr(trace, 'marker'):
                        trace.marker.line = dict(color=secondary, width=3)
            except Exception:
                pass

    # Badges: ensure visible (use inline styles matching KPI look but gold text)
    try:
        top_team = df_team.groupby("NICKNAME")["WIN"].mean().idxmax()
    except Exception:
        top_team = "N/A"

    try:
        top_player = df_player.groupby("PLAYER_NAME")["EFFICIENCY_SCORE"].mean().idxmax()
    except Exception:
        top_player = "N/A"

    badge_style = {
        "background": kpi_style["background"],
        "color": "gold",
        "padding": "12px 18px",
        "borderRadius": "20px",
        "fontWeight": "bold"
    }

    badges = html.Div([
        html.Div(f"🏆 Most Successful Team: {top_team}", style=badge_style),
        html.Div(f"⭐ Most Impactful Player: {top_player}", style=badge_style),
    ], style={"display": "flex", "gap": "20px", "margin": "20px 0", "justifyContent": "center"})


    # -------- League Scoring Trend --------
    season_scoring = (
        df_team.groupby("SEASON")["PTS"].mean().reset_index()
    )

    fig1 = px.line(
        season_scoring, x="SEASON", y="PTS", markers=True,
        title="Season-wise Average Points Per Team", text="PTS"
    )
    fig1.update_xaxes(
    tickmode="array",
    tickvals=sorted(season_scoring["SEASON"].unique())
    )

    fig1.update_traces(
    texttemplate="%{text:.2f}",
    textposition="top center"
    )

    # ERA annotation: mark 2015 (three-point era) on the time series
    try:
        era_x = 2015
        era_y = season_scoring["PTS"].max()
        fig1.add_vline(x=era_x, line_dash="dash", line_color="gray")
        fig1.add_annotation(
            x=era_x, y=era_y,
            text="Three-Point Revolution",
            showarrow=True,
            arrowcolor="gray"
        )
    except Exception:
        pass


    # -------- League Parity --------
    parity = (
        df_team.groupby(["SEASON", "NICKNAME"])["WIN"].mean()
        .groupby("SEASON").median().reset_index()
    )

    fig2 = px.line(
        parity, x="SEASON", y="WIN", markers=True,
        title="League Competitiveness (Median Win %)", text="WIN"
    )
    fig2.update_xaxes(
    tickmode="array",
    tickvals=sorted(parity["SEASON"].unique())
)
    
    fig2.update_yaxes(tickformat=".0%")

    fig2.update_traces(
    texttemplate="%{text:.2f}",
    textposition="top center"
    )

    # -------- Home vs Away --------
    home_away = (
        df_team.groupby(["SEASON", "HOME_AWAY"])["WIN"].mean().reset_index()
    )

    fig3 = px.line(
        home_away, x="SEASON", y="WIN", color="HOME_AWAY", markers=True,
        title="Home vs Away Win Percentage", text="WIN"
    )
    fig3.update_yaxes(tickformat=".0%")
    fig3.update_xaxes(
    tickmode="array",
    tickvals=sorted(home_away["SEASON"].unique())
)
    
    fig3.update_traces(
    texttemplate="%{text:.2f}",
    textposition="top center"
    )


    # -------- Team vs League --------
    team_avg = (
        df_team.groupby(["SEASON", "NICKNAME"])["PTS"].mean().reset_index()
    )

    league_avg = (
        df_team.groupby("SEASON")["PTS"].mean().reset_index()
    )

    fig4 = px.line(
        team_avg, x="SEASON", y="PTS", color="NICKNAME",
        title="Team Scoring vs League Average", markers=True,
        color_discrete_map=team_primary_map
    )

    fig4.add_scatter(
        x=league_avg["SEASON"], y=league_avg["PTS"],
        mode="lines", name="League Avg",
        line=dict(color="black", dash="dash", width=3)
    )
    fig4.update_xaxes(
    tickmode="array",
    tickvals=sorted(league_avg["SEASON"].unique())
)
    
    fig4.update_traces(
    texttemplate="%{text:.2f}",
    textposition="top center"
    )
    # apply two-tone styling (primary line, secondary marker outline)
    apply_two_tone(fig4, team_primary_map, team_secondary_map)


    # -------- East vs West --------
    conf = (
        df_team.groupby(["SEASON", "CONFERENCE"])["PTS"].mean().reset_index()
    )

    fig5 = px.line(
        conf, x="SEASON", y="PTS", color="CONFERENCE", markers=True,
        title="Eastern vs Western Conference Scoring", text="PTS"
    )
    fig5.update_xaxes(
    tickmode="array",
    tickvals=sorted(conf["SEASON"].unique())
)
    fig5.update_traces(
    texttemplate="%{text:.2f}",
    textposition="top center"
    )


    # -------- Team Consistency --------
    # Team consistency may be empty depending on filters — handle empty state
    try:
        consistency = (
            df_team.groupby(["SEASON", "NICKNAME"])["POINT_DIFF"].std()
            .groupby("SEASON").median().reset_index()
        )
    except Exception:
        consistency = None

    if consistency is None or consistency.empty:
        fig6 = {}
        team_consistency_msg = "No data for selected filters"
    else:
        fig6 = px.line(
            consistency, x="SEASON", y="POINT_DIFF", markers=True,
            title="League-wide Team Consistency", text="POINT_DIFF"
        )

        fig6.update_xaxes(
            tickmode="array",
            tickvals=sorted(consistency["SEASON"].unique())
        )
        fig6.update_traces(
            texttemplate="%{text:.2f}",
            textposition="top center"
        )
        team_consistency_msg = ""

    # -------- Most Successful Teams --------
    team_success = (
        df_team
        .groupby("NICKNAME")["WIN"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig_success_teams = px.bar(
        team_success,
        x="WIN",
        y="NICKNAME",
        orientation="h",
        title="Most Successful Teams (Win Percentage, 2004-2022)",
        text="WIN",
        color="NICKNAME",
        color_discrete_map=team_primary_map
    )
    # outline bars with the team's secondary color
    # enforce two-tone and thicker borders
    apply_two_tone(fig_success_teams, team_primary_map, team_secondary_map)

    fig_success_teams.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig_success_teams.update_xaxes(tickformat=".0%")
    fig_success_teams.update_yaxes(title="")


    # -------- Most Dominant Team Seasons --------
    dominant_seasons = (
        df_team
        .groupby(["SEASON", "NICKNAME"])["WIN"]
        .mean()
        .reset_index()
        .sort_values("WIN", ascending=False)
        .head(10)
    )

    dominant_seasons["LABEL"] = (
        dominant_seasons["NICKNAME"] + " (" + dominant_seasons["SEASON"].astype(str) + ")"
    )

    fig_dominant_seasons = px.bar(
        dominant_seasons,
        x="WIN",
        y="LABEL",
        orientation="h",
        title="Most Dominant Team Seasons",
        text="WIN",
        color="NICKNAME",
        color_discrete_map=team_primary_map
    )
    apply_two_tone(fig_dominant_seasons, team_primary_map, team_secondary_map)

    fig_dominant_seasons.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig_dominant_seasons.update_xaxes(tickformat=".0%")
    fig_dominant_seasons.update_yaxes(title="")
    fig_dominant_seasons.update_xaxes(
    tickmode="array",
    tickvals=sorted(dominant_seasons["SEASON"].unique())
)



    # -------- Player Archetypes (Usage vs Efficiency with Labels) --------

    # Step 1: Aggregate player stats safely
    archetype_data = (
        df_player
        .groupby("PLAYER_NAME")
        .agg(
            AVG_MIN=("MINUTES_PLAYED", "mean"),
            AVG_PTS=("PTS", "mean"),
            GAMES_PLAYED=("PTS", "count")
        )
        .reset_index()
    )

    # Step 2: Remove low-sample noise
    archetype_data = archetype_data[
        (archetype_data["GAMES_PLAYED"] >= 30) &
        (archetype_data["AVG_MIN"] >= 8)
    ]

    # Step 3: Compute efficiency correctly
    archetype_data["PTS_PER_MIN"] = archetype_data["AVG_PTS"] / archetype_data["AVG_MIN"]

    # Step 4: Define league medians
    usage_median = archetype_data["AVG_MIN"].median()
    eff_median = archetype_data["PTS_PER_MIN"].median()

    # Step 5: Assign archetypes
    def assign_archetype(row):
        if row["AVG_MIN"] >= usage_median and row["PTS_PER_MIN"] >= eff_median:
            return "High-Usage Stars"
        elif row["AVG_MIN"] >= usage_median and row["PTS_PER_MIN"] < eff_median:
            return "Volume Scorers"
        elif row["AVG_MIN"] < usage_median and row["PTS_PER_MIN"] >= eff_median:
            return "Efficient Role Players"
        else:
            return "Low-Impact Bench Players"

    archetype_data["ARCHETYPE"] = archetype_data.apply(assign_archetype, axis=1)

    # Step 6: Plot with proper legend
    fig7 = px.scatter(
        archetype_data,
        x="AVG_MIN",
        y="PTS_PER_MIN",
        color="ARCHETYPE",
        hover_name="PLAYER_NAME",
        title="Player Archetypes: Usage vs Scoring Efficiency",
        opacity=0.75,
        color_discrete_map={
            "High-Usage Stars": "#f94144",
            "Volume Scorers": "#f3722c",
            "Efficient Role Players": "#43aa8b",
            "Low-Impact Bench Players": "#577590"
        }
    )

    # Step 7: Reference lines
    fig7.add_vline(x=usage_median, line_dash="dash", line_color="gray")
    fig7.add_hline(y=eff_median, line_dash="dash", line_color="gray")

    fig7.update_xaxes(title="Average Minutes Played (Usage)")
    fig7.update_yaxes(title="Points per Minute (Efficiency)")


    # -------- High Scorers --------
    df_player["TWENTY_PLUS"] = (df_player["PTS"] >= 20).astype(int)

    scorers = (
        df_player
        .groupby("PLAYER_NAME")["TWENTY_PLUS"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig8 = px.bar(
        scorers,
        x="PLAYER_NAME",
        y="TWENTY_PLUS",
        title="Most Consistent 20+ Point Scorers",
        text=scorers["TWENTY_PLUS"].round(2),  # pre-round values
        color="PLAYER_NAME",
        color_discrete_map=player_primary_map
    )
    apply_two_tone(fig8, player_primary_map, player_secondary_map)

    fig8.update_traces(
        texttemplate="%{y:.2%}",   # two decimals only
        textposition="outside",
        textangle=0                # force horizontal text
    )

    fig8.update_yaxes(tickformat=".0%")
    fig8.update_xaxes(title="Player")


    

    # -------- Most Successful Players --------
    player_success = (
        df_player
        .groupby("PLAYER_NAME")
        .agg(
            AVG_EFF=("EFFICIENCY_SCORE", "mean"),
            GAMES=("EFFICIENCY_SCORE", "count")
        )
        .reset_index()
    )

    # Filter meaningful careers
    player_success = player_success[player_success["GAMES"] >= 100]

    player_success = (
        player_success
        .sort_values("AVG_EFF", ascending=False)
        .head(10)
    )

    fig_success_players = px.bar(
        player_success,
        x="AVG_EFF",
        y="PLAYER_NAME",
        orientation="h",
        title="Most Impactful Players (Avg Efficiency per Game)",
        text="AVG_EFF",
        color="PLAYER_NAME",
        color_discrete_map=player_primary_map
    )
    apply_two_tone(fig_success_players, player_primary_map, player_secondary_map)

    fig_success_players.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_success_players.update_yaxes(title="")


    # -------- Top Single-Game Performances (Corrected) --------

    top_games = (
        df_player
        .groupby("PLAYER_NAME", as_index=False)
        .agg(
            BEST_EFF=("EFFICIENCY_SCORE", "max"),
            BEST_PTS=("PTS", "max")
        )
        .sort_values("BEST_EFF", ascending=False)
        .head(10)
    )

    fig9 = px.bar(
        top_games,
        x="BEST_EFF",
        y="PLAYER_NAME",
        orientation="h",
        title="Top Single-Game Performances (Best Game per Player)",
        text="BEST_EFF",
        color="PLAYER_NAME",
        color_discrete_map=player_primary_map
                )
    apply_two_tone(fig9, player_primary_map, player_secondary_map)

    fig9.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig9.update_xaxes(title="Efficiency Score")
    fig9.update_yaxes(title="")

    return (
        kpi_cards,
        badges,
        fig1,
        fig2,
        fig3,
        fig4,
        fig5,
        fig6,
        team_consistency_msg,
        fig_success_teams,
        fig_dominant_seasons,
        fig7,
        fig8,
        fig_success_players,
        fig9,
    )


# --------------------------------------------------
# 6. Run Server
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)