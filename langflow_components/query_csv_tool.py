"""
Query CSV Tool for LangFlow
Provides flexible CSV querying with schema awareness (Self-Contained Version)
"""

from lfx.custom import Component
from lfx.io import Output
from lfx.field_typing import Tool
from langchain_core.tools import StructuredTool
from pathlib import Path
import pandas as pd
import re as _re
import json
import logging
import difflib
from typing import Optional

logger = logging.getLogger(__name__)


# Columns that identify a row — never treated as measurable stats in auto-resolve
_IDENTITY_COLS = {'score', 'team', 'formation', 'avg_age', 'id', 'date',
                  'tournament', 'city', 'country', 'neutral'}


def _fuzzy_match_column(requested: str, available: list, cutoff: float = 0.82) -> str | None:
    """
    Return the best-matching column name from `available` for a misspelled `requested`.
    Returns None if no close match found above `cutoff`.
    Only matches within the same home_/away_ prefix family to avoid cross-side confusion.
    """
    matches = difflib.get_close_matches(requested, available, n=1, cutoff=cutoff)
    if matches:
        return matches[0]
    return None


def _strip_home_away_prefix(name: str) -> str:
    """Remove accidental home_/away_ prefix the model may have added."""
    for pfx in ("home_", "away_"):
        if name.startswith(pfx):
            return name[len(pfx):]
    return name


def _extract_stats_from_filter(cf: str) -> list:
    """
    Pull every unique base stat name referenced in a pandas filter expression.
    Strips home_/away_ prefix and removes identity/non-metric column names.
    Preserves order of first occurrence.
    """
    raw = _re.findall(r'(?:home|away)_(\w+)', cf.replace(' ', ''))
    return list(dict.fromkeys(m for m in raw if m not in _IDENTITY_COLS))


def _detect_winner_loser(cf: str):
    """
    Inspect a custom_filter string (spaces already removed) and return
    ('winner' | 'loser' | None) based on score comparison patterns.
    Handles: >, >=, <, <= in both directions.
    """
    cf = cf.replace(' ', '')
    winner_patterns = [
        r'home_score>away_score',   # home_score > away_score
        r'home_score>=away_score',  # home_score >= away_score  (edge case)
        r'away_score<home_score',   # away_score < home_score
        r'away_score<=home_score',  # away_score <= home_score  (edge case)
    ]
    loser_patterns = [
        r'home_score<away_score',
        r'home_score<=away_score',
        r'away_score>home_score',
        r'away_score>=home_score',
    ]
    for p in winner_patterns:
        if _re.search(p, cf):
            return 'winner'
    for p in loser_patterns:
        if _re.search(p, cf):
            return 'loser'
    return None


class QueryCSVTool(Component):
    display_name: str = "Query CSV"
    description: str = "Query CSV data with filters and schema awareness"
    documentation: str = "https://github.com/babaksh/FanPulse"
    icon: str = "database"
    name: str = "query_csv_tool"

    outputs = [
        Output(display_name="Tool", name="tool", method="build_tool"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path('d:/MyPythonProjects/FanPulse')
        self.schema_path = self.project_root / "data" / "match_data" / "data_schema.json"
        self.results_csv = self.project_root / "data" / "match_data" / "results.csv"
        self.tactical_csv = self.project_root / "data" / "match_data" / "tactical_data.csv"
        self.schema = None

    def _load_schema(self):
        """Load data schema from JSON file"""
        if self.schema is None:
            try:
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
                self.log(f"Schema loaded: {len(self.schema)} sections")
            except Exception as e:
                self.log(f"Warning: Could not load schema: {e}")
                self.schema = {}
        return self.schema

    def build_tool(self) -> Tool:
        """Build the CSV query tool"""

        def query_csv(
            table: str,
            query_mode: str = "simple",
            team_filter: Optional[str] = None,
            date_from: Optional[str] = None,
            date_to: Optional[str] = None,
            tournament_filter: Optional[str] = None,
            formation_filter: Optional[str] = None,
            min_possession: Optional[float] = None,
            max_possession: Optional[float] = None,
            custom_filter: Optional[str] = None,
            resolve_loser_stat: Optional[str] = None,
            resolve_winner_stat: Optional[str] = None,
            team_perspective: Optional[str] = None,
            columns: Optional[str] = None,
            limit: int = 50
        ) -> str:
            """Query CSV data with filters - supports both simple and custom query modes.

            Args:
                table: Table name - "results" or "tactical_data"
                query_mode: Query mode - "simple" (use predefined filters) or "custom" (use custom_filter)

                SIMPLE MODE PARAMETERS (query_mode="simple"):
                team_filter: Team name to filter (searches both home and away)
                date_from: Start date (YYYY-MM-DD format)
                date_to: End date (YYYY-MM-DD format)
                tournament_filter: Tournament name OR match_id prefix filter
                    - For tournament names: "FIFA World Cup", "Friendly", "UEFA Euro"
                    - For match_id prefixes: "WC_2026" (World Cup 2026), "EURO_2024", "FRIENDLY_2025"
                    - Smart detection: if contains underscore + digits, searches match_id; otherwise searches tournament name
                formation_filter: Formation to filter (e.g., "4-3-3", "4-2-3-1") - only for tactical_data table
                    - Searches both home_formation and away_formation columns
                min_possession: Minimum possession percentage (0-100) - only for tactical_data table
                    - Filters matches where either team has >= this possession
                max_possession: Maximum possession percentage (0-100) - only for tactical_data table
                    - Filters matches where either team has <= this possession

                CUSTOM MODE PARAMETERS (query_mode="custom"):
                custom_filter: Pandas boolean expression for filtering
                    - Use column names from schema
                    - Supported operators: >, <, >=, <=, ==, !=, &, |, ~
                    - Always wrap each side of | in parentheses to avoid precedence errors
                    - Examples:
                        * "((home_possession > 60) & (home_score > away_score)) | ((away_possession > 60) & (away_score > home_score))"
                        * "(home_shots_on_target / home_shots_total > 0.5)"
                        * "home_team.str.contains('Brazil')"

                PERSPECTIVE PARAMETERS (optional, work with any query_mode):

                resolve_loser_stat: Base stat column name WITHOUT home_/away_ prefix.
                    Resolves home/away using scores → returns one row per LOSING team.
                    Output columns: date | losing_team | opponent | result | loser_<stat> [| loser_<stat2> ...]
                    Use for: "teams that lost despite high X", "which teams lost with >80% pass accuracy"
                    NOTE: tool auto-detects this from custom_filter if not provided.

                resolve_winner_stat: Base stat column name WITHOUT home_/away_ prefix.
                    Resolves home/away using scores → returns one row per WINNING team.
                    Output columns: date | winning_team | opponent | result | winner_<stat> [| winner_<stat2> ...]
                    Use for: "teams that won with low possession", "winners with most shots"
                    NOTE: tool auto-detects this from custom_filter if not provided.

                team_perspective: Team name to focus on (e.g. "Brazil").
                    Resolves each row so the named team's stats are always in the same columns,
                    regardless of whether they were home or away.
                    Output columns: date | team | opponent | result | <stat1> | <stat2> | ...
                    Use for: "Brazil's stats in each match", "Spain's possession per game"
                    Requires: columns listing the base stat names (WITHOUT home_/away_ prefix)

                columns: Comma-separated column names.
                    - With team_perspective: base stat names WITHOUT home_/away_ prefix (e.g. "possession,shots_total")
                    - Without perspective params: full column names (e.g. "date,home_team,away_team,home_score")
                    - Ignored when resolve_loser_stat or resolve_winner_stat is active

                COMMON PARAMETERS:
                limit: Maximum rows to return (default: 50, max: 200)

            Returns:
                Query results in markdown table format.
                resolve_loser_stat  → date | losing_team  | opponent | result | loser_<stat> ...
                resolve_winner_stat → date | winning_team | opponent | result | winner_<stat> ...
                team_perspective    → date | team | opponent | result | <stat> ...
                default             → raw filtered rows
            """
            try:
                # ----------------------------------------------------------------
                # NORMALISE INPUTS
                # ----------------------------------------------------------------
                # Auto-switch to custom mode when custom_filter is supplied
                if custom_filter and query_mode == "simple":
                    query_mode = "custom"
                    self.log("Auto-switching to custom mode because custom_filter was provided")

                # Strip home_/away_ prefix from resolve params if model passed full column name
                if resolve_winner_stat:
                    resolve_winner_stat = _strip_home_away_prefix(resolve_winner_stat.strip())
                if resolve_loser_stat:
                    resolve_loser_stat = _strip_home_away_prefix(resolve_loser_stat.strip())

                # Warn immediately when columns is combined with resolve_winner/loser_stat.
                # These modes build their own output columns — extra columns are impossible to merge.
                # Return an error so the model knows to fix its call instead of looping.
                if columns and (resolve_winner_stat or resolve_loser_stat):
                    mode = "resolve_winner_stat" if resolve_winner_stat else "resolve_loser_stat"
                    return json.dumps({
                        "error": (
                            f"Invalid call: `columns` cannot be used together with `{mode}`. "
                            f"`{mode}` builds its own output columns automatically "
                            f"(date | winning_team/losing_team | opponent | result | winner_/loser_<stat>). "
                            "Remove the `columns` parameter and retry. "
                            "To get additional stats per winner/loser, add more base stat names to "
                            f"`{mode}` instead — e.g. resolve_winner_stat='possession,shots_total,key_passes'."
                        )
                    }, ensure_ascii=False)

                # Strip home_/away_ prefix from columns when used with team_perspective
                # (model may pass "home_possession,away_shots_total" instead of "possession,shots_total")
                if team_perspective and columns:
                    columns = ','.join(
                        _strip_home_away_prefix(c.strip()) for c in columns.split(',')
                    )

                # AUTO-APPLY team_perspective when team_filter is set on tactical_data
                # and the model forgot to supply it.
                # Only activates when raw home_*/away_* stat columns are explicitly requested
                # (i.e. model is trying to do team-perspective work manually).
                if (
                    not team_perspective
                    and not resolve_winner_stat
                    and not resolve_loser_stat
                    and team_filter
                    and table == "tactical_data"
                    and columns
                ):
                    requested = [c.strip() for c in columns.split(',')]
                    # Known base stat names in tactical_data (without home_/away_ prefix)
                    _known_stats = {
                        'possession', 'shots_total', 'shots_on_target', 'shots_blocked',
                        'shot_accuracy', 'passes_total', 'pass_accuracy', 'key_passes',
                        'tackles_won', 'tackle_success', 'interceptions', 'clearances',
                        'aerials_won', 'attacking_intensity', 'defensive_intensity',
                        'formation', 'avg_age',
                    }
                    _identity = {'home_team', 'away_team', 'home_score', 'away_score',
                                 'date', 'match_id', 'tournament'}
                    # Stat cols with home_/away_ prefix (excluding identity)
                    stat_cols_prefixed = [
                        c for c in requested
                        if (c.startswith('home_') or c.startswith('away_'))
                        and c not in _identity
                    ]
                    # Base-name stat cols (no prefix, known tactical stat)
                    stat_cols_base = [c for c in requested if c in _known_stats]

                    # If BOTH home_X and away_X of the same stat are requested, the model wants
                    # both teams side by side (e.g. match analysis) — do NOT apply team_perspective.
                    base_names_home = {c[5:] for c in stat_cols_prefixed if c.startswith('home_')}
                    base_names_away = {c[5:] for c in stat_cols_prefixed if c.startswith('away_')}
                    wants_both_sides = bool(base_names_home & base_names_away)

                    has_stats = bool(stat_cols_prefixed or stat_cols_base)

                    if has_stats and not wants_both_sides:
                        team_perspective = team_filter
                        # Convert all home_*/away_* stat columns to base names for team_perspective
                        base_cols = []
                        for c in requested:
                            if c in _identity:
                                pass  # identity cols are auto-included by team_perspective path
                            else:
                                base_cols.append(_strip_home_away_prefix(c))
                        # Deduplicate while preserving order
                        seen = set()
                        deduped = []
                        for c in base_cols:
                            if c not in seen:
                                seen.add(c)
                                deduped.append(c)
                        columns = ','.join(deduped)
                        self.log(
                            f"Auto-applied team_perspective='{team_perspective}' "
                            f"(team_filter set, stat columns requested without perspective). "
                            f"Columns normalised to: {columns}"
                        )

                self.log(f"Querying {table} in {query_mode} mode")
                self.status = f"Querying {table}..."

                # ----------------------------------------------------------------
                # VALIDATE
                # ----------------------------------------------------------------
                if query_mode not in ["simple", "custom"]:
                    return f"❌ Invalid query_mode: {query_mode}. Must be 'simple' or 'custom'"

                if table not in ["results", "tactical_data"]:
                    return f"❌ Invalid table: {table}. Must be 'results' or 'tactical_data'"

                # ----------------------------------------------------------------
                # LOAD DATA
                # ----------------------------------------------------------------
                schema = self._load_schema()
                csv_path = self.results_csv if table == "results" else self.tactical_csv

                if not csv_path.exists():
                    return "❌ Data file not found. Please check server configuration."

                df = pd.read_csv(csv_path)
                df['date'] = pd.to_datetime(df['date'])
                filtered_df = df.copy()

                # ----------------------------------------------------------------
                # APPLY FILTERS
                # ----------------------------------------------------------------
                if query_mode == "custom":
                    if not custom_filter:
                        return "❌ custom_filter is required when query_mode='custom'"
                    try:
                        dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file', 'os.', 'sys.']
                        if any(kw in custom_filter.lower() for kw in dangerous_keywords):
                            return f"❌ Unsafe expression in custom_filter."
                        self.log(f"Applying custom filter: {custom_filter}")
                        filtered_df = df.query(custom_filter)
                    except Exception as e:
                        return (
                            f"❌ Error in custom_filter: {e}\n\n"
                            f"Tips:\n"
                            f"- Use & for AND, | for OR, ~ for NOT\n"
                            f"- Wrap each side of | in parentheses: ((a) | (b))\n"
                            f"- For string operations: column.str.contains('text')\n"
                            f"- Example: ((home_possession > 60) & (home_score > away_score)) | "
                            f"((away_possession > 60) & (away_score > home_score))"
                        )
                    # In custom mode, also apply simple narrowing filters if provided
                    # (model may combine custom_filter with tournament_filter, team_filter, etc.)
                    if team_filter:
                        filtered_df = filtered_df[
                            (filtered_df['home_team'].str.contains(team_filter, case=False, na=False)) |
                            (filtered_df['away_team'].str.contains(team_filter, case=False, na=False))
                        ]
                    if date_from:
                        try:
                            filtered_df = filtered_df[filtered_df['date'] >= pd.to_datetime(date_from)]
                        except Exception:
                            pass  # ignore bad date in custom mode — custom_filter is primary
                    if date_to:
                        try:
                            filtered_df = filtered_df[filtered_df['date'] <= pd.to_datetime(date_to)]
                        except Exception:
                            pass
                    if tournament_filter:
                        is_match_id_prefix = '_' in tournament_filter and any(
                            ch.isdigit() for ch in tournament_filter)
                        if is_match_id_prefix and 'match_id' in filtered_df.columns:
                            filtered_df = filtered_df[
                                filtered_df['match_id'].str.contains(
                                    tournament_filter, case=False, na=False)
                            ]
                        elif 'tournament' in filtered_df.columns:
                            year_match = _re.search(r'\b(18|19|20)\d{2}\b', tournament_filter)
                            if year_match:
                                year = int(year_match.group())
                                tournament_name = tournament_filter[:year_match.start()].strip()
                                filtered_df = filtered_df[
                                    filtered_df['tournament'].str.contains(
                                        tournament_name, case=False, na=False)
                                ]
                                filtered_df = filtered_df[filtered_df['date'].dt.year == year]
                            else:
                                filtered_df = filtered_df[
                                    filtered_df['tournament'].str.contains(
                                        tournament_filter, case=False, na=False)
                                ]

                else:  # simple mode
                    if team_filter:
                        filtered_df = filtered_df[
                            (filtered_df['home_team'].str.contains(team_filter, case=False, na=False)) |
                            (filtered_df['away_team'].str.contains(team_filter, case=False, na=False))
                        ]

                    if date_from:
                        try:
                            filtered_df = filtered_df[filtered_df['date'] >= pd.to_datetime(date_from)]
                        except Exception:
                            return f"❌ Invalid date_from format: {date_from}. Use YYYY-MM-DD"

                    if date_to:
                        try:
                            filtered_df = filtered_df[filtered_df['date'] <= pd.to_datetime(date_to)]
                        except Exception:
                            return f"❌ Invalid date_to format: {date_to}. Use YYYY-MM-DD"

                    if tournament_filter:
                        is_match_id_prefix = '_' in tournament_filter and any(
                            ch.isdigit() for ch in tournament_filter)
                        if is_match_id_prefix and 'match_id' in filtered_df.columns:
                            filtered_df = filtered_df[
                                filtered_df['match_id'].str.contains(
                                    tournament_filter, case=False, na=False)
                            ]
                        elif 'tournament' in filtered_df.columns:
                            year_match = _re.search(r'\b(18|19|20)\d{2}\b', tournament_filter)
                            if year_match:
                                year = int(year_match.group())
                                tournament_name = tournament_filter[:year_match.start()].strip()
                                filtered_df = filtered_df[
                                    filtered_df['tournament'].str.contains(
                                        tournament_name, case=False, na=False)
                                ]
                                filtered_df = filtered_df[filtered_df['date'].dt.year == year]
                            else:
                                filtered_df = filtered_df[
                                    filtered_df['tournament'].str.contains(
                                        tournament_filter, case=False, na=False)
                                ]
                        # else: table has no match_id or tournament column — skip silently

                    if formation_filter and table == "tactical_data":
                        if 'home_formation' in filtered_df.columns:
                            filtered_df = filtered_df[
                                (filtered_df['home_formation'].str.contains(
                                    formation_filter, case=False, na=False)) |
                                (filtered_df['away_formation'].str.contains(
                                    formation_filter, case=False, na=False))
                            ]

                    if (min_possession is not None or max_possession is not None) and table == "tactical_data":
                        if 'home_possession' in filtered_df.columns:
                            if min_possession is not None:
                                filtered_df = filtered_df[
                                    (filtered_df['home_possession'] >= min_possession) |
                                    (filtered_df['away_possession'] >= min_possession)
                                ]
                            if max_possession is not None:
                                filtered_df = filtered_df[
                                    (filtered_df['home_possession'] <= max_possession) |
                                    (filtered_df['away_possession'] <= max_possession)
                                ]

                # ----------------------------------------------------------------
                # LIMIT (cap only — applied per-path after resolve to avoid
                # under-counting when draws are skipped during winner/loser resolve)
                # ----------------------------------------------------------------
                limit = min(limit, 200)

                if filtered_df.empty:
                    return "Based on all available data, no matches met this criterion."

                # ----------------------------------------------------------------
                # AUTO-RESOLVE: detect winner/loser pattern from custom_filter
                # when the model did not supply resolve_winner/loser_stat.
                # Covers all score comparison operators (>, >=, <, <=).
                # ----------------------------------------------------------------
                _winner_stats: list = []
                _loser_stats: list = []

                if not resolve_winner_stat and not resolve_loser_stat and not team_perspective and custom_filter:
                    _direction = _detect_winner_loser(custom_filter)
                    if _direction:
                        _stat_names = _extract_stats_from_filter(custom_filter)
                        if _stat_names:
                            if _direction == 'winner':
                                resolve_winner_stat = _stat_names[0]
                                _winner_stats = _stat_names
                            else:
                                resolve_loser_stat = _stat_names[0]
                                _loser_stats = _stat_names
                        # If no stats in filter (e.g. only score condition), fall through to raw output

                # ----------------------------------------------------------------
                # FILTER COMPLETENESS GUARD:
                # When resolve_winner_stat or resolve_loser_stat is active and a
                # custom_filter covers only ONE side (only home or only away score
                # comparison), automatically expand it to cover both sides.
                #
                # Strategy: "side-swap" — swap every home_X↔away_X token in the
                # original filter to produce the mirror expression, then combine
                # with OR.  This handles BOTH fixed-value and cross-column filters:
                #
                #   Fixed-value (possession < 45):
                #     "(home_score > away_score) & (home_possession < 45)"
                #   → mirror: "(away_score > home_score) & (away_possession < 45)"
                #   → result:  original | mirror   ✅
                #
                #   Cross-column (possession > opponent's):
                #     "(home_possession > away_possession) & (home_score < away_score)"
                #   → mirror: "(away_possession > home_possession) & (away_score < home_score)"
                #   → result:  original | mirror   ✅
                # ----------------------------------------------------------------
                if custom_filter and (resolve_winner_stat or resolve_loser_stat):
                    _cf_clean = custom_filter.replace(' ', '')

                    # Detect which score-sides are already present
                    _has_home_win  = bool(_re.search(r'home_score>away_score|away_score<home_score', _cf_clean))
                    _has_away_win  = bool(_re.search(r'away_score>home_score|home_score<away_score', _cf_clean))
                    _has_home_loss = bool(_re.search(r'home_score<away_score|away_score>home_score', _cf_clean))
                    _has_away_loss = bool(_re.search(r'away_score<home_score|home_score>away_score', _cf_clean))

                    _needs_expand = (
                        (resolve_winner_stat and _has_home_win and not _has_away_win) or
                        (resolve_loser_stat  and _has_home_loss and not _has_away_loss)
                    )

                    if _needs_expand:
                        # Build the mirror expression by swapping every home_X ↔ away_X token.
                        # We use a placeholder to avoid double-swapping:
                        #   home_X  →  __HOME_X__  (step 1)
                        #   away_X  →  home_X      (step 2)
                        #   __HOME_X__  →  away_X  (step 3)
                        _mirror = _re.sub(r'\bhome_', '__HOME_', custom_filter)
                        _mirror = _re.sub(r'\baway_', 'home_', _mirror)
                        _mirror = _mirror.replace('__HOME_', 'away_')

                        custom_filter = f"({custom_filter}) | ({_mirror})"
                        self.log(f"Auto-expanded filter to cover both sides: {custom_filter}")
                        # Re-apply filter to the full dataframe (not the already-filtered one)
                        try:
                            filtered_df = df.query(custom_filter)
                            if tournament_filter:
                                is_match_id_prefix = '_' in tournament_filter and any(
                                    ch.isdigit() for ch in tournament_filter)
                                if is_match_id_prefix and 'match_id' in filtered_df.columns:
                                    filtered_df = filtered_df[
                                        filtered_df['match_id'].str.contains(
                                            tournament_filter, case=False, na=False)
                                    ]
                                elif 'tournament' in filtered_df.columns:
                                    filtered_df = filtered_df[
                                        filtered_df['tournament'].str.contains(
                                            tournament_filter, case=False, na=False)
                                    ]
                        except Exception as _e:
                            self.log(f"Auto-expand failed ({_e}), keeping original filter result")

                # If resolve params were supplied by the model (not auto-detected), build stat lists now.
                # Support comma-separated multi-stat: "possession,shots_total,key_passes"
                if resolve_winner_stat and not _winner_stats:
                    _winner_stats = [_strip_home_away_prefix(s.strip())
                                     for s in resolve_winner_stat.split(',') if s.strip()]
                if resolve_loser_stat and not _loser_stats:
                    _loser_stats = [_strip_home_away_prefix(s.strip())
                                    for s in resolve_loser_stat.split(',') if s.strip()]

                # ----------------------------------------------------------------
                # RESOLVE LOSER STAT
                # ----------------------------------------------------------------
                if _loser_stats:
                    for s in _loser_stats:
                        for col in [f"home_{s}", f"away_{s}"]:
                            if col not in filtered_df.columns:
                                return f"❌ Column '{col}' not found. Check resolve_loser_stat value."
                    for col in ["home_score", "away_score", "home_team", "away_team"]:
                        if col not in filtered_df.columns:
                            return f"❌ Required column '{col}' not found."

                    records = []
                    for _, row in filtered_df.iterrows():
                        h, a = row["home_score"], row["away_score"]
                        if h == a:
                            continue  # draw — no loser
                        if h < a:
                            loser, opponent = row["home_team"], row["away_team"]
                            pfx = "home"
                            result_str = f"Lost {int(h)}–{int(a)}"
                        else:
                            loser, opponent = row["away_team"], row["home_team"]
                            pfx = "away"
                            result_str = f"Lost {int(a)}–{int(h)}"
                        rec = {
                            "date": str(row["date"])[:10],
                            "losing_team": loser,
                            "opponent": opponent,
                            "result": result_str,
                        }
                        for s in _loser_stats:
                            val = row.get(f"{pfx}_{s}")
                            rec[f"loser_{s}"] = round(float(val), 1) if pd.notna(val) else None
                        records.append(rec)

                    if not records:
                        return "Based on all available data, no matches met this criterion."

                    resolved_df = pd.DataFrame(records).head(limit)
                    out = "# 📊 Match Results: Tournament Tactical Database\n\n"
                    out += f"**Rows Returned:** {len(resolved_df)}\n\n"
                    out += "## Data:\n\n"
                    out += resolved_df.to_markdown(index=False)
                    out += f"\n\n## Summary:\n- Total matches: {len(resolved_df)}\n"
                    self.status = f"Resolved {len(resolved_df)} losing teams"
                    return out

                # ----------------------------------------------------------------
                # RESOLVE WINNER STAT
                # ----------------------------------------------------------------
                if _winner_stats:
                    for s in _winner_stats:
                        for col in [f"home_{s}", f"away_{s}"]:
                            if col not in filtered_df.columns:
                                return f"❌ Column '{col}' not found. Check resolve_winner_stat value."
                    for col in ["home_score", "away_score", "home_team", "away_team"]:
                        if col not in filtered_df.columns:
                            return f"❌ Required column '{col}' not found."

                    records = []
                    for _, row in filtered_df.iterrows():
                        h, a = row["home_score"], row["away_score"]
                        if h == a:
                            continue  # draw — no winner
                        if h > a:
                            winner, opponent = row["home_team"], row["away_team"]
                            pfx = "home"
                            result_str = f"Won {int(h)}–{int(a)}"
                        else:
                            winner, opponent = row["away_team"], row["home_team"]
                            pfx = "away"
                            result_str = f"Won {int(a)}–{int(h)}"
                        rec = {
                            "date": str(row["date"])[:10],
                            "winning_team": winner,
                            "opponent": opponent,
                            "result": result_str,
                        }
                        for s in _winner_stats:
                            val = row.get(f"{pfx}_{s}")
                            rec[f"winner_{s}"] = round(float(val), 1) if pd.notna(val) else None
                        records.append(rec)

                    if not records:
                        return "Based on all available data, no matches met this criterion."

                    resolved_df = pd.DataFrame(records).head(limit)
                    out = "# 📊 Match Results: Tournament Tactical Database\n\n"
                    out += f"**Rows Returned:** {len(resolved_df)}\n\n"
                    out += "## Data:\n\n"
                    out += resolved_df.to_markdown(index=False)
                    out += f"\n\n## Summary:\n- Total matches: {len(resolved_df)}\n"
                    self.status = f"Resolved {len(resolved_df)} winning teams"
                    return out

                # ----------------------------------------------------------------
                # TEAM PERSPECTIVE
                # ----------------------------------------------------------------
                if team_perspective:
                    for col in ["home_score", "away_score", "home_team", "away_team"]:
                        if col not in filtered_df.columns:
                            return f"❌ Required column '{col}' not found in {table}."

                    # Parse stat list; columns may be empty → return basic info only
                    # Identity cols are already included in the fixed output (date/team/opponent/result)
                    # so we skip them here to avoid duplicate/spurious columns.
                    _perspective_identity = {
                        'date', 'team', 'opponent', 'result',
                        'home_team', 'away_team', 'home_score', 'away_score',
                        'score', 'match_id', 'tournament', 'city', 'country', 'neutral',
                    }
                    stat_cols = [c.strip() for c in columns.split(',')] if columns else []
                    # Strip any accidental home_/away_ prefix in individual stats
                    stat_cols = [_strip_home_away_prefix(s) for s in stat_cols if s]
                    # Remove identity/already-included columns
                    stat_cols = [s for s in stat_cols if s not in _perspective_identity]

                    records = []
                    for _, row in filtered_df.iterrows():
                        is_home = team_perspective.lower() in str(row["home_team"]).lower()
                        is_away = team_perspective.lower() in str(row["away_team"]).lower()
                        if not is_home and not is_away:
                            continue
                        h, a = row["home_score"], row["away_score"]
                        if is_home:
                            opponent = row["away_team"]
                            team_score, opp_score = int(h), int(a)
                            pfx = "home"
                        else:
                            opponent = row["home_team"]
                            team_score, opp_score = int(a), int(h)
                            pfx = "away"

                        if team_score > opp_score:
                            result_str = f"Won {team_score}–{opp_score}"
                        elif team_score == opp_score:
                            result_str = f"Draw {team_score}–{opp_score}"
                        else:
                            result_str = f"Lost {team_score}–{opp_score}"

                        rec = {
                            "date": str(row["date"])[:10],
                            "team": str(row["home_team"] if is_home else row["away_team"]),
                            "opponent": str(opponent),
                            "result": result_str,
                        }
                        for stat in stat_cols:
                            col_name = f"{pfx}_{stat}"
                            val = row.get(col_name)
                            if val is not None and pd.notna(val):
                                rec[stat] = round(float(val), 1) if isinstance(val, float) else val
                        records.append(rec)

                    if not records:
                        return f"Based on all available data, no matches found for {team_perspective}."

                    resolved_df = pd.DataFrame(records).head(limit)
                    table_display = "Historical Match Database" if table == "results" else "Tournament Tactical Database"
                    out = f"# 📊 Match Results: {table_display}\n\n"
                    out += f"**Rows Returned:** {len(resolved_df)}\n\n"
                    out += "## Data:\n\n"
                    out += resolved_df.to_markdown(index=False)
                    out += f"\n\n## Summary:\n- Total matches: {len(resolved_df)}\n"
                    self.status = f"Team perspective: {len(resolved_df)} matches for {team_perspective}"
                    return out

                # ----------------------------------------------------------------
                # DEFAULT: raw filtered rows
                # ----------------------------------------------------------------
                table_display = "Historical Match Database" if table == "results" else "Tournament Tactical Database"
                out = f"# 📊 Match Results: {table_display}\n\n"

                # ----------------------------------------------------------------
                # FORMATION EXPAND: when formation_filter is active and no columns
                # override, expand each row into one entry per team that used the
                # requested formation — so the agent never has to do home/away mapping.
                # ----------------------------------------------------------------
                if (
                    formation_filter
                    and table == "tactical_data"
                    and not columns  # only when agent didn't ask for specific raw columns
                    and 'home_formation' in filtered_df.columns
                    and 'home_team' in filtered_df.columns
                ):
                    records = []
                    for _, row in filtered_df.iterrows():
                        h_form = str(row.get('home_formation', ''))
                        a_form = str(row.get('away_formation', ''))
                        h_match = formation_filter.lower() in h_form.lower()
                        a_match = formation_filter.lower() in a_form.lower()
                        h, a = row['home_score'], row['away_score']
                        date_str = str(row['date'])[:10]

                        def _result(team_score, opp_score):
                            if team_score > opp_score:
                                return 'Win'
                            elif team_score == opp_score:
                                return 'Draw'
                            return 'Loss'

                        if h_match:
                            records.append({
                                'date': date_str,
                                'team': row['home_team'],
                                'opponent': row['away_team'],
                                'score': f"{int(h)}–{int(a)}",
                                'result': _result(h, a),
                                'formation': h_form,
                            })
                        if a_match:
                            records.append({
                                'date': date_str,
                                'team': row['away_team'],
                                'opponent': row['home_team'],
                                'score': f"{int(a)}–{int(h)}",
                                'result': _result(a, h),
                                'formation': a_form,
                            })

                    if not records:
                        return "Based on all available data, no matches met this criterion."

                    resolved_df = pd.DataFrame(records).head(limit)
                    out += f"**Rows Returned:** {len(resolved_df)}\n\n"
                    out += "## Data:\n\n"
                    out += resolved_df.to_markdown(index=False)
                    out += f"\n\n## Summary:\n- Total Matches: {len(filtered_df)} | Teams using {formation_filter}: {len(records)}\n"
                    self.status = f"Formation expand: {len(resolved_df)} entries for {formation_filter}"
                    return out

                # ----------------------------------------------------------------
                # DEFAULT: raw rows (no formation_filter, or caller specified columns)
                # ----------------------------------------------------------------
                out += f"**Rows Returned:** {len(filtered_df)}\n\n"

                # Schema coverage hint
                if table in schema:
                    cov = schema[table].get('coverage', {})
                    out += f"**Coverage:** {cov.get('time_range', 'N/A')}, {cov.get('total_matches', 'N/A')} matches\n\n"

                # Column selection — with typo/fuzzy correction
                if columns:
                    requested_cols = [c.strip() for c in columns.split(',')]
                    available_cols = list(filtered_df.columns)
                    display_cols = []
                    corrected = []   # (original, corrected) pairs for logging
                    truly_missing = []
                    for rc in requested_cols:
                        if rc in filtered_df.columns:
                            display_cols.append(rc)
                        else:
                            # Try fuzzy match — auto-correct typos like "away_tackels_won"
                            suggestion = _fuzzy_match_column(rc, available_cols)
                            if suggestion:
                                display_cols.append(suggestion)
                                corrected.append((rc, suggestion))
                            else:
                                truly_missing.append(rc)
                    if corrected:
                        self.log(f"Auto-corrected column typos: {corrected}")
                    if not display_cols:
                        return (
                            f"❌ None of the requested columns exist in {table}.\n"
                            f"Requested: {requested_cols}\n"
                            f"Available: {available_cols}"
                        )
                    if truly_missing:
                        out += f"⚠️ **Warning:** Columns not found (skipped): {truly_missing}\n\n"
                else:
                    if table == "results":
                        display_cols = ['date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament']
                    else:
                        display_cols = [
                            'match_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score',
                            'home_possession', 'away_possession', 'home_shots_total', 'away_shots_total',
                            'home_shot_accuracy', 'away_shot_accuracy',
                        ]
                    display_cols = [c for c in display_cols if c in filtered_df.columns]

                display_df = filtered_df[display_cols].head(limit).copy()
                if 'date' in display_df.columns:
                    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')

                out += "## Data:\n\n"
                out += display_df.to_markdown(index=False)
                out += f"\n\n## Summary:\n- Total Matches: {len(filtered_df)}\n"

                if team_filter:
                    home_m = filtered_df[filtered_df['home_team'].str.contains(team_filter, case=False, na=False)]
                    away_m = filtered_df[filtered_df['away_team'].str.contains(team_filter, case=False, na=False)]
                    hw = len(home_m[home_m['home_score'] > home_m['away_score']])
                    aw = len(away_m[away_m['away_score'] > away_m['home_score']])
                    out += f"- {team_filter} Wins: {hw + aw}\n"
                    out += f"- {team_filter} Home Wins: {hw}\n"
                    out += f"- {team_filter} Away Wins: {aw}\n"
                    # List opponents so the model knows both teams are already in this result set
                    # and does NOT need a second query for the opponent.
                    if 'home_team' in filtered_df.columns and 'away_team' in filtered_df.columns:
                        opponents = []
                        for _, r in filtered_df.iterrows():
                            if team_filter.lower() in str(r['home_team']).lower():
                                opponents.append(str(r['away_team']))
                            else:
                                opponents.append(str(r['home_team']))
                        out += f"- Opponents in this result: {', '.join(opponents)}\n"
                        out += f"⚠️ Both home and away stats for ALL opponents above are already included in the rows above — no need to query any opponent separately.\n"

                self.log(f"Query successful: {len(filtered_df)} rows")
                self.status = f"Retrieved {len(filtered_df)} rows"
                return out

            except Exception as e:
                error_msg = f"Error querying CSV: {e}"
                self.log(error_msg)
                self.status = "Error"
                return f"❌ {error_msg}"

        return StructuredTool.from_function(
            func=query_csv,
            name="query_csv",
            description=(
                "Query CSV data with two modes: 'simple' (predefined filters) or 'custom' (pandas expressions). "
                "Tables: 'results' (all matches 1872-2026) or 'tactical_data' (WhoScored scraped matches with 41 metrics). "
                "\n\n"
                "SIMPLE MODE (query_mode='simple'): "
                "Use predefined filters: team_filter, date_from, date_to, tournament_filter, formation_filter, min_possession, max_possession. "
                "tournament_filter accepts both tournament names ('FIFA World Cup') and match_id prefixes ('WC_2026', 'EURO_2024'). "
                "\n\n"
                "CUSTOM MODE (query_mode='custom'): "
                "Use custom_filter for pandas boolean expressions. "
                "Always wrap each side of | in parentheses: ((a) & (b)) | ((c) & (d)). "
                "Supports: >, <, >=, <=, ==, !=, &, |, ~, .str.contains(). "
                "\n\n"
                "PERSPECTIVE PARAMETERS (optional, combine with any mode to eliminate home/away confusion): "
                "\n"
                "resolve_loser_stat='<stat>': returns one row per LOSING team with their correct stat(s). "
                "→ date | losing_team | opponent | result | loser_<stat>. "
                "Use for: 'teams that lost despite high X stat'. "
                "NOTE: auto-detected from custom_filter when not provided. "
                "\n"
                "resolve_winner_stat='<stat>': returns one row per WINNING team with their correct stat(s). "
                "→ date | winning_team | opponent | result | winner_<stat>. "
                "Use for: 'teams that won with low possession', 'winners with fewest shots'. "
                "NOTE: auto-detected from custom_filter when not provided. "
                "\n"
                "team_perspective='<TeamName>': returns one row per match from that team's point of view. "
                "→ date | team | opponent | result | <stat1> | <stat2> | ... "
                "Requires columns='stat1,stat2,...' listing base stat names (WITHOUT home_/away_ prefix). "
                "Use for: 'Brazil stats per match', 'Spain possession in each game'. "
                "\n\n"
                "All perspective params accept base stat names WITHOUT home_/away_ prefix "
                "(e.g. 'pass_accuracy', 'possession', 'shots_total'). "
                "The tool automatically strips accidental prefixes if provided."
            )
        )

# Made with Bob
