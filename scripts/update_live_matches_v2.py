#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced script to update tactical_stats.csv with automatic tournament detection
Supports all major international competitions across all confederations

Usage:
    # Update with today's matches (auto-detect tournament)
    python scripts/update_live_matches_v2.py --today
    
    # Update with specific date
    python scripts/update_live_matches_v2.py --date 2026-06-15
    
    # Update with specific date, skip existing matches (saves API calls)
    python scripts/update_live_matches_v2.py --date 2026-06-15 --skip-existing
    
    # Update with specific fixture IDs
    python scripts/update_live_matches_v2.py --fixtures 12345 67890
    
    # Force specific tournament type (override auto-detection)
    python scripts/update_live_matches_v2.py --today --force-tournament WC2026
"""

import os
import sys
import argparse
import requests
import pandas as pd
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "match_data" / "tactical_stats.csv"
BACKUP_PATH = PROJECT_ROOT / "data" / "match_data" / "tactical_stats_backup.csv"


class TournamentDetector:
    """Intelligent tournament detection based on API-Football league data"""
    
    # Tournament mapping: league_name patterns -> prefix
    TOURNAMENT_PATTERNS = {
        # FIFA World Cup
        'world cup': {
            'prefix': 'WC',
            'priority': 1,
            'description': 'FIFA World Cup'
        },
        
        # Continental Championships
        'euro': {
            'prefix': 'EURO',
            'priority': 2,
            'description': 'UEFA European Championship'
        },
        'copa america': {
            'prefix': 'COPA',
            'priority': 2,
            'description': 'Copa América'
        },
        'africa cup': {
            'prefix': 'AFCON',
            'priority': 2,
            'description': 'Africa Cup of Nations'
        },
        'asian cup': {
            'prefix': 'AFC',
            'priority': 2,
            'description': 'AFC Asian Cup'
        },
        'gold cup': {
            'prefix': 'GOLD',
            'priority': 2,
            'description': 'CONCACAF Gold Cup'
        },
        'ofc nations': {
            'prefix': 'OFC',
            'priority': 2,
            'description': 'OFC Nations Cup'
        },
        
        # World Cup Qualifiers (by confederation)
        'world cup - qualification': {
            'prefix': 'WCQ',
            'priority': 3,
            'description': 'World Cup Qualifiers'
        },
        'uefa - qualification': {
            'prefix': 'UEFAQ',
            'priority': 3,
            'description': 'UEFA Qualifiers'
        },
        'conmebol - qualification': {
            'prefix': 'CONMEBOLQ',
            'priority': 3,
            'description': 'CONMEBOL Qualifiers'
        },
        'caf - qualification': {
            'prefix': 'CAFQ',
            'priority': 3,
            'description': 'CAF Qualifiers'
        },
        'afc - qualification': {
            'prefix': 'AFCQ',
            'priority': 3,
            'description': 'AFC Qualifiers'
        },
        'concacaf - qualification': {
            'prefix': 'CONCACAFQ',
            'priority': 3,
            'description': 'CONCACAF Qualifiers'
        },
        
        # UEFA Nations League
        'uefa nations league': {
            'prefix': 'UNL',
            'priority': 4,
            'description': 'UEFA Nations League'
        },
        
        # CONMEBOL Copa América Qualifiers
        'conmebol - copa america': {
            'prefix': 'COPAQ',
            'priority': 4,
            'description': 'Copa América Qualifiers'
        },
        
        # Friendlies
        'friendly': {
            'prefix': 'FRIENDLY',
            'priority': 10,
            'description': 'International Friendly'
        },
        'friendlies': {
            'prefix': 'FRIENDLY',
            'priority': 10,
            'description': 'International Friendly'
        },
    }
    
    @classmethod
    def detect_tournament(cls, league_name: str, league_season: int) -> Tuple[str, str]:
        """
        Detect tournament type from league name and season
        
        Returns:
            Tuple[prefix, description]
        """
        league_lower = league_name.lower()
        
        # Check each pattern
        for pattern, info in cls.TOURNAMENT_PATTERNS.items():
            if pattern in league_lower:
                # Add season year to prefix
                prefix = f"{info['prefix']}{league_season}"
                return prefix, info['description']
        
        # Default: Unknown tournament
        return f"INTL{league_season}", "International Match"
    
    @classmethod
    def get_all_supported_tournaments(cls) -> List[str]:
        """Get list of all supported tournament types"""
        return [info['description'] for info in cls.TOURNAMENT_PATTERNS.values()]


class LiveMatchUpdater:
    """Enhanced updater with automatic tournament detection"""
    
    def __init__(self):
        self.api_key = os.getenv('API_FOOTBALL_KEY')
        if not self.api_key:
            raise ValueError("❌ API_FOOTBALL_KEY not found in .env file")
        
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        
        self.detector = TournamentDetector()
        
        print(f"✅ API Key loaded")
        print(f"📁 CSV Path: {CSV_PATH}")
        print(f"\n🏆 Supported Tournaments:")
        for tournament in self.detector.get_all_supported_tournaments():
            print(f"   - {tournament}")
    
    
    def fetch_fixture_data(self, fixture_id: int, force_tournament: Optional[str] = None) -> Optional[Dict]:
        """Fetch complete fixture data with automatic tournament detection"""
        print(f"\n🔍 Fetching fixture {fixture_id}...")
        
        # Rate limiting
        time.sleep(6)
        
        # Get fixture details
        details_url = f"{self.base_url}/fixtures"
        details_params = {'id': fixture_id}
        
        try:
            response = requests.get(details_url, headers=self.headers, params=details_params)
            response.raise_for_status()
            details_data = response.json()
            
            if not details_data['response']:
                print(f"❌ No details found for fixture {fixture_id}")
                return None
            
            details = details_data['response'][0]
            
            # Check match status - only process finished matches
            match_status = details['fixture']['status']['short']
            if match_status not in ['FT', 'AET', 'PEN']:
                print(f"⚠️  Match not finished yet (Status: {match_status})")
                print(f"   Skipping - will be available after match ends")
                return None
            
            # Extract league info for tournament detection
            league_info = details['league']
            league_name = league_info['name']
            league_season = league_info['season']
            
            # Detect tournament (or use forced tournament)
            if force_tournament:
                tournament_prefix = force_tournament
                tournament_desc = "Forced Tournament"
                print(f"🔧 Using forced tournament: {tournament_prefix}")
            else:
                tournament_prefix, tournament_desc = self.detector.detect_tournament(
                    league_name, league_season
                )
                print(f"🏆 Detected: {tournament_desc} ({tournament_prefix})")
            
            # Get fixture statistics
            time.sleep(6)
            
            stats_url = f"{self.base_url}/fixtures/statistics"
            stats_params = {'fixture': fixture_id}
            
            response = requests.get(stats_url, headers=self.headers, params=stats_params)
            response.raise_for_status()
            stats_data = response.json()
            
            if not stats_data['response']:
                print(f"⚠️  No statistics found for fixture {fixture_id}")
                return None
            
            stats = stats_data['response']
            
            # Convert to our format with detected tournament
            match_data = self._convert_to_csv_format(
                fixture_id, details, stats, tournament_prefix
            )
            
            if match_data:
                print(f"✅ [{tournament_prefix}] {match_data['home_team']} {match_data['home_score']}-{match_data['away_score']} {match_data['away_team']}")
            
            return match_data
            
        except Exception as e:
            print(f"❌ Error fetching fixture {fixture_id}: {e}")
            return None
    
    def _get_stat(self, statistics: List[Dict], stat_name: str) -> Optional[float]:
        """Extract statistic value"""
        for stat in statistics:
            if stat['type'] == stat_name:
                value = stat['value']
                if value is None:
                    return None
                if isinstance(value, str) and '%' in value:
                    return float(value.replace('%', ''))
                return float(value) if value else None
        return None
    
    def _convert_to_csv_format(self, fixture_id: int, details: Dict, stats: List[Dict], 
                               tournament_prefix: str) -> Optional[Dict]:
        """Convert API data to CSV format with tournament prefix"""
        fixture = details['fixture']
        teams = details['teams']
        goals = details['goals']
        
        home_stats = stats[0]['statistics'] if len(stats) > 0 else []
        away_stats = stats[1]['statistics'] if len(stats) > 1 else []
        
        # Create match_id with tournament prefix
        date_str = fixture['date'].split('T')[0].replace('-', '_')
        home_team = teams['home']['name'].replace(' ', '_')
        away_team = teams['away']['name'].replace(' ', '_')
        match_id = f"{tournament_prefix}_{date_str}_{home_team}_{away_team}"
        
        return {
            'match_id': match_id,
            'date': fixture['date'].split('T')[0],
            'home_team': teams['home']['name'],
            'away_team': teams['away']['name'],
            'home_score': goals['home'] or 0,
            'away_score': goals['away'] or 0,
            'home_formation': details.get('lineups', [{}])[0].get('formation') if details.get('lineups') else None,
            'away_formation': details.get('lineups', [{}])[1].get('formation') if len(details.get('lineups', [])) > 1 else None,
            'home_possession': self._get_stat(home_stats, 'Ball Possession'),
            'away_possession': self._get_stat(away_stats, 'Ball Possession'),
            'home_shots': self._get_stat(home_stats, 'Total Shots'),
            'away_shots': self._get_stat(away_stats, 'Total Shots'),
            'home_shots_on_target': self._get_stat(home_stats, 'Shots on Goal'),
            'away_shots_on_target': self._get_stat(away_stats, 'Shots on Goal'),
            'home_shots_off_target': self._get_stat(home_stats, 'Shots off Goal'),
            'away_shots_off_target': self._get_stat(away_stats, 'Shots off Goal'),
            'home_shots_blocked': self._get_stat(home_stats, 'Blocked Shots'),
            'away_shots_blocked': self._get_stat(away_stats, 'Blocked Shots'),
            'home_shots_insidebox': self._get_stat(home_stats, 'Shots insidebox'),
            'away_shots_insidebox': self._get_stat(away_stats, 'Shots insidebox'),
            'home_shots_outsidebox': self._get_stat(home_stats, 'Shots outsidebox'),
            'away_shots_outsidebox': self._get_stat(away_stats, 'Shots outsidebox'),
            'home_xg': None,  # Not available in API-Football
            'away_xg': None,
            'home_passes': self._get_stat(home_stats, 'Total passes'),
            'away_passes': self._get_stat(away_stats, 'Total passes'),
            'home_pass_accuracy': self._get_stat(home_stats, 'Passes %'),
            'away_pass_accuracy': self._get_stat(away_stats, 'Passes %'),
            'home_tackles': None,
            'away_tackles': None,
            'home_interceptions': None,
            'away_interceptions': None,
            'home_clearances': None,
            'away_clearances': None,
            'home_corners': self._get_stat(home_stats, 'Corner Kicks'),
            'away_corners': self._get_stat(away_stats, 'Corner Kicks'),
            'home_offsides': self._get_stat(home_stats, 'Offsides'),
            'away_offsides': self._get_stat(away_stats, 'Offsides'),
            'home_fouls': self._get_stat(home_stats, 'Fouls'),
            'away_fouls': self._get_stat(away_stats, 'Fouls'),
            'home_yellow_cards': self._get_stat(home_stats, 'Yellow Cards'),
            'away_yellow_cards': self._get_stat(away_stats, 'Yellow Cards'),
            'home_red_cards': self._get_stat(home_stats, 'Red Cards'),
            'away_red_cards': self._get_stat(away_stats, 'Red Cards'),
            'home_goalkeeper_saves': self._get_stat(home_stats, 'Goalkeeper Saves'),
            'away_goalkeeper_saves': self._get_stat(away_stats, 'Goalkeeper Saves'),
            'venue': fixture.get('venue', {}).get('name'),
            'referee': fixture.get('referee'),
            'attendance': None
        }
    
    def get_fixtures_by_date(self, date: str, international_only: bool = True, skip_existing: bool = False) -> List[int]:
        """
        Get all fixture IDs for a specific date
        
        Args:
            date: Date in YYYY-MM-DD format
            international_only: Filter for international matches only
            skip_existing: Skip fixtures that already exist in CSV (saves API calls)
            
        Returns:
            List of fixture IDs
        """
        print(f"\n🔍 Searching for matches on {date}...")
        
        # Load existing matches if skip_existing is enabled
        existing_matches = {}  # {(date, home, away): match_id}
        if skip_existing and CSV_PATH.exists():
            try:
                df_existing = pd.read_csv(CSV_PATH)
                for _, row in df_existing.iterrows():
                    key = (row['date'], row['home_team'], row['away_team'])
                    existing_matches[key] = row['match_id']
                print(f"📋 Loaded {len(existing_matches)} existing matches for comparison")
            except Exception as e:
                print(f"⚠️  Could not load existing matches: {e}")
        
        url = f"{self.base_url}/fixtures"
        params = {'date': date}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            fixtures = data['response']
            
            # Filter for international matches only
            if international_only:
                international_fixtures = []
                for f in fixtures:
                    try:
                        league_type = f.get('league', {}).get('type', '')
                        league_name = f.get('league', {}).get('name', '')
                        
                        # Check if it's an international match
                        if (league_type == 'Cup' or
                            'World Cup' in league_name or
                            'International' in league_name or
                            'Friendlies' in league_name or
                            'Qualification' in league_name or
                            'Nations League' in league_name or
                            'Euro' in league_name or
                            'Copa America' in league_name or
                            'Africa Cup' in league_name or
                            'Asian Cup' in league_name or
                            'Gold Cup' in league_name):
                            international_fixtures.append(f)
                    except (KeyError, TypeError) as e:
                        print(f"⚠️  Skipping fixture due to missing data: {e}")
                        continue
                
                fixtures = international_fixtures
                print(f"🌍 Filtering for international matches only")
            
            fixture_ids = []
            skipped_count = 0
            print(f"✅ Found {len(fixtures)} matches:")
            
            for fixture in fixtures:
                try:
                    home = fixture['teams']['home']['name']
                    away = fixture['teams']['away']['name']
                    league = fixture['league']['name']
                    status = fixture['fixture']['status']['short']
                    
                    # Check if match already exists (if skip_existing is enabled)
                    if skip_existing and existing_matches:
                        key = (date, home, away)
                        if key in existing_matches:
                            skipped_count += 1
                            print(f"   ⏭️  SKIPPED (exists): {home} vs {away} | {league} ({status})")
                            continue
                    
                    fixture_ids.append(fixture['fixture']['id'])
                    print(f"   - {home} vs {away} | {league} ({status})")
                except (KeyError, TypeError) as e:
                    print(f"⚠️  Skipping fixture due to missing data: {e}")
                    continue
            
            if skipped_count > 0:
                print(f"\n📊 Summary: {len(fixture_ids)} new matches, {skipped_count} skipped (already in CSV)")
            
            if not fixture_ids:
                if skipped_count > 0:
                    print(f"⚠️  All matches already exist in CSV")
                else:
                    print(f"⚠️  No international matches found on {date}")
            
            return fixture_ids
            
        except Exception as e:
            print(f"❌ Error fetching fixtures: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_csv(self, fixture_ids: List[int], max_matches: Optional[int] = None, 
                   force_tournament: Optional[str] = None):
        """Update CSV with new match data"""
        if not fixture_ids:
            print("❌ No fixtures to update")
            return
        
        # Limit number of matches if specified
        if max_matches and len(fixture_ids) > max_matches:
            print(f"⚠️  Limiting to first {max_matches} matches (out of {len(fixture_ids)})")
            fixture_ids = fixture_ids[:max_matches]
        
        # Load existing data
        if CSV_PATH.exists():
            df_existing = pd.read_csv(CSV_PATH)
            print(f"\n📊 Current CSV: {len(df_existing)} matches")
        else:
            df_existing = pd.DataFrame()
            print(f"\n📊 Creating new CSV file")
        
        # Fetch and add new matches
        new_matches = []
        total = len(fixture_ids)
        for idx, fixture_id in enumerate(fixture_ids, 1):
            print(f"\n[{idx}/{total}] Processing fixture {fixture_id}...")
            match_data = self.fetch_fixture_data(fixture_id, force_tournament)
            if match_data:
                # Check if already exists by match_id OR by date+teams combination
                if not df_existing.empty:
                    # Check 1: Exact match_id match
                    if match_data['match_id'] in df_existing['match_id'].values:
                        print(f"⚠️  Match already exists (same match_id): {match_data['match_id']}")
                        print(f"   Use --update flag to update existing matches")
                        continue
                    
                    # Check 2: Same date and teams (different prefix)
                    duplicate = df_existing[
                        (df_existing['date'] == match_data['date']) &
                        (df_existing['home_team'] == match_data['home_team']) &
                        (df_existing['away_team'] == match_data['away_team'])
                    ]
                    
                    if not duplicate.empty:
                        existing_match_id = duplicate.iloc[0]['match_id']
                        print(f"⚠️  Match already exists (same date/teams): {existing_match_id}")
                        print(f"    Skipping new match_id: {match_data['match_id']}")
                        print(f"   Use --update flag to update existing matches")
                        continue
                
                new_matches.append(match_data)
        
        if not new_matches:
            print("\n⚠️  No new matches to add")
            return
        
        # Combine and save
        df_new = pd.DataFrame(new_matches)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        df_combined.to_csv(CSV_PATH, index=False)
        
        print(f"\n✅ CSV updated successfully!")
        print(f"   - Previous: {len(df_existing)} matches")
        print(f"   - Added: {len(new_matches)} matches")
        print(f"   - Total: {len(df_combined)} matches")
        print(f"\n📁 File: {CSV_PATH}")
        
        # Show tournament breakdown
        print(f"\n🏆 Tournament Breakdown:")
        for match in new_matches:
            prefix = match['match_id'].split('_')[0]
            print(f"   - {prefix}: {match['home_team']} vs {match['away_team']}")


def main():
    parser = argparse.ArgumentParser(description='Update tactical_stats.csv with automatic tournament detection')
    parser.add_argument('--today', action='store_true', help='Fetch today\'s matches')
    parser.add_argument('--date', type=str, help='Fetch matches for specific date (YYYY-MM-DD)')
    parser.add_argument('--fixtures', type=int, nargs='+', help='Specific fixture IDs to fetch')
    parser.add_argument('--max', type=int, default=None, help='Maximum number of matches to fetch')
    parser.add_argument('--force-tournament', type=str, help='Force specific tournament prefix (e.g., WC2026, EURO2024)')
    parser.add_argument('--skip-existing', action='store_true', help='Skip matches that already exist in CSV (saves API calls)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔴 ENHANCED LIVE MATCH DATA UPDATER v2.0")
    print("🤖 With Automatic Tournament Detection")
    print("=" * 70)
    
    updater = LiveMatchUpdater()
    
    fixture_ids = []
    
    if args.today:
        today = datetime.now().strftime('%Y-%m-%d')
        fixture_ids = updater.get_fixtures_by_date(today, international_only=True, skip_existing=args.skip_existing)
    
    elif args.date:
        fixture_ids = updater.get_fixtures_by_date(args.date, international_only=True, skip_existing=args.skip_existing)
    
    elif args.fixtures:
        fixture_ids = args.fixtures
        print(f"\n📋 Using provided fixture IDs: {fixture_ids}")
    
    else:
        print("\n❌ Please specify one of: --today, --date, --fixtures")
        parser.print_help()
        return
    
    if fixture_ids:
        updater.update_csv(fixture_ids, max_matches=args.max, force_tournament=args.force_tournament)
    
    print("\n" + "=" * 70)
    print("✅ Update complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()

# Made with Bob - Enhanced Edition