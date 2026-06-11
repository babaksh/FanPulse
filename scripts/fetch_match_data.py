#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified script to fetch match data from API-Football

This script combines all fetch functionality into one tool:
- Fetch single or multiple matches by fixture ID
- Fetch World Cup 2022 matches (all, key matches, or knockout stage)
- Fetch recent matches for national teams
- Fetch matches by date

Usage Examples:
    # Fetch a single match
    python scripts/fetch_match_data.py --fixture-id 215662
    
    # Fetch multiple matches
    python scripts/fetch_match_data.py --fixture-ids 215662 215663 215664
    
    # Fetch World Cup 2022 matches
    python scripts/fetch_match_data.py --world-cup-2022 --key-matches
    python scripts/fetch_match_data.py --world-cup-2022 --knockout
    python scripts/fetch_match_data.py --world-cup-2022 --all
    
    # Fetch national team matches
    python scripts/fetch_match_data.py --team brazil --last 3
    python scripts/fetch_match_data.py --hosts --last 2
    
    # Fetch matches by date
    python scripts/fetch_match_data.py --date 2026-06-15
    python scripts/fetch_match_data.py --today
"""

import os
import sys
import json
import argparse
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# National teams and their API-Football IDs
NATIONAL_TEAMS = {
    'brazil': 6, 'argentina': 26, 'france': 2, 'germany': 25,
    'spain': 9, 'england': 10, 'portugal': 27, 'netherlands': 1118,
    'italy': 768, 'belgium': 1, 'croatia': 3, 'uruguay': 7,
    'colombia': 8, 'mexico': 16, 'usa': 2384, 'canada': 1530,
}

HOST_NATIONS = ['usa', 'mexico', 'canada']
TOP_CONTENDERS = ['brazil', 'argentina', 'france', 'germany', 'spain', 'england']

# All World Cup 2022 fixture IDs (in chronological order)
WC_2022_FIXTURES = [
    855736, 855735, 855734, 866681, 855737, 855738, 855739, 871850,
    855740, 855741, 871851, 855742, 855743, 855744, 855745, 855746,
    866682, 855747, 855748, 855749, 871852, 855750, 855751, 855752,
    871853, 855753, 855754, 855755, 855756, 855757, 855758, 855759,
    855760, 855761, 855762, 866683, 871854, 855763, 855765, 855764,
    855766, 855767, 855768, 871855, 855769, 855770, 855772, 855771,
    976533, 976642, 976643, 976534, 977344, 977705, 977345, 977706,
    978072, 977794, 978088, 978036, 978279, 978488, 979138, 979139
]


class APIFootballFetcher:
    """Unified API-Football data fetcher"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key"""
        self.api_key = api_key or os.getenv('API_FOOTBALL_KEY')
        if not self.api_key:
            raise ValueError(
                "API key not found. Set API_FOOTBALL_KEY in .env file "
                "or pass api_key parameter"
            )
        
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        
        self.csv_path = project_root / "data" / "match_data" / "tactical_stats.csv"
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    def fetch_fixture_statistics(self, fixture_id: int) -> Optional[Dict]:
        """Fetch statistics for a specific fixture"""
        url = f"{self.base_url}/fixtures/statistics"
        params = {'fixture': fixture_id}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['response']:
                return data['response']
            else:
                print(f"⚠️  No statistics found for fixture {fixture_id}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching fixture {fixture_id}: {e}")
            return None
    
    def fetch_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """Fetch basic details for a fixture"""
        url = f"{self.base_url}/fixtures"
        params = {'id': fixture_id}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['response']:
                return data['response'][0]
            else:
                print(f"⚠️  No details found for fixture {fixture_id}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching fixture details {fixture_id}: {e}")
            return None
    
    def fetch_fixtures_by_date(self, date: str) -> List[int]:
        """Fetch all fixture IDs for a specific date"""
        url = f"{self.base_url}/fixtures"
        params = {'date': date}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            fixture_ids = [fixture['fixture']['id'] for fixture in data['response']]
            print(f"✅ Found {len(fixture_ids)} fixtures on {date}")
            return fixture_ids
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching fixtures for {date}: {e}")
            return []
    
    def fetch_team_fixtures(self, team_name: str, last_n: int = 5) -> List[int]:
        """Fetch last N fixtures for a specific team"""
        if team_name.lower() not in NATIONAL_TEAMS:
            print(f"❌ Team '{team_name}' not found. Available teams:")
            for name in sorted(NATIONAL_TEAMS.keys()):
                print(f"   - {name}")
            return []
        
        team_id = NATIONAL_TEAMS[team_name.lower()]
        print(f"\n🔍 Fetching recent matches for {team_name.upper()}...")
        
        # Get fixtures from last 90 days
        today = datetime.now()
        start_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/fixtures"
        params = {
            'team': team_id,
            'from': start_date,
            'to': end_date,
            'last': last_n
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['response']:
                fixture_ids = [fixture['fixture']['id'] for fixture in data['response']]
                print(f"✅ Found {len(fixture_ids)} fixtures for {team_name}")
                
                for fixture in data['response']:
                    home = fixture['teams']['home']['name']
                    away = fixture['teams']['away']['name']
                    date = fixture['fixture']['date'].split('T')[0]
                    print(f"   - {date}: {home} vs {away}")
                
                return fixture_ids
            else:
                print(f"⚠️  No fixtures found for {team_name}")
                return []
                
        except Exception as e:
            print(f"❌ Failed to fetch fixtures for {team_name}: {e}")
            return []
    
    def get_stat_value(self, statistics: List[Dict], stat_name: str) -> Optional[float]:
        """Extract a specific statistic value"""
        for stat in statistics:
            if stat['type'] == stat_name:
                value = stat['value']
                if value is None:
                    return None
                if isinstance(value, str) and '%' in value:
                    return float(value.replace('%', ''))
                return float(value) if value else None
        return None
    
    def convert_to_match_data(self, fixture_id: int) -> Optional[Dict]:
        """Convert API-Football data to CSV format"""
        details = self.fetch_fixture_details(fixture_id)
        stats = self.fetch_fixture_statistics(fixture_id)
        
        if not details or not stats:
            return None
        
        fixture = details['fixture']
        teams = details['teams']
        goals = details['goals']
        
        home_stats = stats[0]['statistics'] if len(stats) > 0 else []
        away_stats = stats[1]['statistics'] if len(stats) > 1 else []
        
        match_data = {
            'match_id': f"API_{fixture_id}",
            'date': fixture['date'].split('T')[0],
            'home_team': teams['home']['name'],
            'away_team': teams['away']['name'],
            'home_score': goals['home'] or 0,
            'away_score': goals['away'] or 0,
            'home_formation': details.get('lineups', [{}])[0].get('formation', 'N/A') if details.get('lineups') else 'N/A',
            'away_formation': details.get('lineups', [{}])[1].get('formation', 'N/A') if len(details.get('lineups', [])) > 1 else 'N/A',
            'home_possession': self.get_stat_value(home_stats, 'Ball Possession'),
            'away_possession': self.get_stat_value(away_stats, 'Ball Possession'),
            'home_shots': self.get_stat_value(home_stats, 'Total Shots'),
            'away_shots': self.get_stat_value(away_stats, 'Total Shots'),
            'home_shots_on_target': self.get_stat_value(home_stats, 'Shots on Goal') or 0,
            'away_shots_on_target': self.get_stat_value(away_stats, 'Shots on Goal') or 0,
            'home_shots_off_target': self.get_stat_value(home_stats, 'Shots off Goal'),
            'away_shots_off_target': self.get_stat_value(away_stats, 'Shots off Goal'),
            'home_shots_blocked': self.get_stat_value(home_stats, 'Blocked Shots'),
            'away_shots_blocked': self.get_stat_value(away_stats, 'Blocked Shots'),
            'home_shots_insidebox': self.get_stat_value(home_stats, 'Shots insidebox'),
            'away_shots_insidebox': self.get_stat_value(away_stats, 'Shots insidebox'),
            'home_shots_outsidebox': self.get_stat_value(home_stats, 'Shots outsidebox'),
            'away_shots_outsidebox': self.get_stat_value(away_stats, 'Shots outsidebox'),
            'home_xg': None,
            'away_xg': None,
            'home_passes': self.get_stat_value(home_stats, 'Total passes'),
            'away_passes': self.get_stat_value(away_stats, 'Total passes'),
            'home_pass_accuracy': self.get_stat_value(home_stats, 'Passes %'),
            'away_pass_accuracy': self.get_stat_value(away_stats, 'Passes %'),
            'home_tackles': None,
            'away_tackles': None,
            'home_interceptions': None,
            'away_interceptions': None,
            'home_clearances': None,
            'away_clearances': None,
            'home_corners': self.get_stat_value(home_stats, 'Corner Kicks'),
            'away_corners': self.get_stat_value(away_stats, 'Corner Kicks'),
            'home_offsides': self.get_stat_value(home_stats, 'Offsides'),
            'away_offsides': self.get_stat_value(away_stats, 'Offsides'),
            'home_fouls': self.get_stat_value(home_stats, 'Fouls'),
            'away_fouls': self.get_stat_value(away_stats, 'Fouls'),
            'home_yellow_cards': self.get_stat_value(home_stats, 'Yellow Cards'),
            'away_yellow_cards': self.get_stat_value(away_stats, 'Yellow Cards'),
            'home_red_cards': self.get_stat_value(home_stats, 'Red Cards'),
            'away_red_cards': self.get_stat_value(away_stats, 'Red Cards'),
            'home_goalkeeper_saves': self.get_stat_value(home_stats, 'Goalkeeper Saves'),
            'away_goalkeeper_saves': self.get_stat_value(away_stats, 'Goalkeeper Saves'),
            'venue': fixture.get('venue', {}).get('name', 'N/A'),
            'referee': fixture.get('referee', 'N/A'),
            'attendance': None
        }
        
        return match_data
    
    def append_to_csv(self, match_data: Dict) -> bool:
        """Append match data to CSV file"""
        try:
            df_new = pd.DataFrame([match_data])
            
            if self.csv_path.exists():
                df_existing = pd.read_csv(self.csv_path)
                
                if match_data['match_id'] in df_existing['match_id'].values:
                    print(f"⚠️  Match {match_data['match_id']} already exists")
                    return False
                
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_combined = df_new
                print(f"✅ Creating new CSV file: {self.csv_path}")
            
            df_combined.to_csv(self.csv_path, index=False)
            print(f"✅ Added: {match_data['home_team']} vs {match_data['away_team']}")
            return True
            
        except Exception as e:
            print(f"❌ Error appending to CSV: {e}")
            return False
    
    def fetch_and_save(self, fixture_ids: List[int], delay: float = 2.0) -> int:
        """Fetch multiple fixtures and save to CSV with rate limiting"""
        success_count = 0
        total = len(fixture_ids)
        
        for i, fixture_id in enumerate(fixture_ids, 1):
            print(f"\n[{i}/{total}] Fetching fixture {fixture_id}...")
            match_data = self.convert_to_match_data(fixture_id)
            
            if match_data:
                if self.append_to_csv(match_data):
                    success_count += 1
            
            if i < total:
                print(f"⏳ Waiting {delay}s before next request...")
                time.sleep(delay)
        
        return success_count
    
    def get_existing_fixtures(self) -> set:
        """Get set of already fetched fixture IDs"""
        if not self.csv_path.exists():
            return set()
        
        df = pd.read_csv(self.csv_path)
        existing = set()
        
        for match_id in df['match_id']:
            if match_id.startswith('API_'):
                fixture_id = int(match_id.replace('API_', ''))
                existing.add(fixture_id)
        
        return existing


def main():
    parser = argparse.ArgumentParser(
        description='Unified script to fetch match data from API-Football',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single match
  python scripts/fetch_match_data.py --fixture-id 215662
  
  # Multiple matches
  python scripts/fetch_match_data.py --fixture-ids 215662 215663
  
  # World Cup 2022
  python scripts/fetch_match_data.py --world-cup-2022 --key-matches
  python scripts/fetch_match_data.py --world-cup-2022 --knockout
  
  # National teams
  python scripts/fetch_match_data.py --team brazil --last 3
  python scripts/fetch_match_data.py --hosts --last 2
  
  # By date
  python scripts/fetch_match_data.py --date 2026-06-15
  python scripts/fetch_match_data.py --today
        """
    )
    
    # Main mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--fixture-id', type=int, help='Single fixture ID')
    mode_group.add_argument('--fixture-ids', type=int, nargs='+', help='Multiple fixture IDs')
    mode_group.add_argument('--world-cup-2022', action='store_true', help='Fetch World Cup 2022 matches')
    mode_group.add_argument('--team', type=str, help='Fetch matches for a national team')
    mode_group.add_argument('--hosts', action='store_true', help='Fetch matches for WC 2026 hosts')
    mode_group.add_argument('--top-contenders', action='store_true', help='Fetch matches for top contenders')
    mode_group.add_argument('--date', type=str, help='Fetch matches for date (YYYY-MM-DD)')
    mode_group.add_argument('--today', action='store_true', help='Fetch today\'s matches')
    
    # World Cup 2022 options
    wc_group = parser.add_argument_group('World Cup 2022 options')
    wc_mode = wc_group.add_mutually_exclusive_group()
    wc_mode.add_argument('--all', action='store_true', help='All 64 matches')
    wc_mode.add_argument('--key-matches', action='store_true', help='First 10 matches')
    wc_mode.add_argument('--knockout', action='store_true', help='Last 8 matches (knockout)')
    wc_mode.add_argument('--next', type=int, metavar='N', help='Next N unfetched matches')
    
    # Team options
    parser.add_argument('--last', type=int, default=3, help='Number of recent matches per team (default: 3)')
    
    # General options
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests in seconds (default: 2.0)')
    parser.add_argument('--yes', '-y', action='store_true', help='Auto-confirm without asking')
    parser.add_argument('--api-key', type=str, help='API-Football API key')
    
    args = parser.parse_args()
    
    try:
        fetcher = APIFootballFetcher(api_key=args.api_key)
        fixture_ids = []
        
        # Determine fixture IDs based on mode
        if args.fixture_id:
            fixture_ids = [args.fixture_id]
            
        elif args.fixture_ids:
            fixture_ids = args.fixture_ids
            
        elif args.world_cup_2022:
            existing = fetcher.get_existing_fixtures()
            print(f"📊 Already have {len(existing)} World Cup 2022 matches")
            
            if args.all:
                fixture_ids = WC_2022_FIXTURES
            elif args.key_matches:
                fixture_ids = WC_2022_FIXTURES[:10]
            elif args.knockout:
                fixture_ids = WC_2022_FIXTURES[-8:]
            elif args.next:
                for fid in WC_2022_FIXTURES:
                    if fid not in existing:
                        fixture_ids.append(fid)
                        if len(fixture_ids) >= args.next:
                            break
            else:
                print("❌ Please specify --all, --key-matches, --knockout, or --next N")
                return 1
                
        elif args.team:
            fixture_ids = fetcher.fetch_team_fixtures(args.team, args.last)
            
        elif args.hosts:
            for team in HOST_NATIONS:
                fixture_ids.extend(fetcher.fetch_team_fixtures(team, args.last))
                
        elif args.top_contenders:
            for team in TOP_CONTENDERS:
                fixture_ids.extend(fetcher.fetch_team_fixtures(team, args.last))
                
        elif args.today:
            today = datetime.now().strftime('%Y-%m-%d')
            fixture_ids = fetcher.fetch_fixtures_by_date(today)
            
        elif args.date:
            fixture_ids = fetcher.fetch_fixtures_by_date(args.date)
        
        if not fixture_ids:
            print("❌ No fixtures found")
            return 1
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 Total fixtures to fetch: {len(fixture_ids)}")
        print(f"⏱️  Estimated time: {len(fixture_ids) * args.delay / 60:.1f} minutes")
        print(f"{'='*60}")
        
        # Confirm
        if not args.yes:
            print("\n❓ Proceed with fetching? (y/n): ", end='')
            try:
                response = input().strip().lower()
            except EOFError:
                print("\n❌ Cannot read input. Use --yes flag for auto-confirm.")
                return 1
            
            if response != 'y':
                print("❌ Cancelled")
                return 0
        else:
            print("\n✅ Auto-confirmed with --yes flag")
        
        # Fetch
        print(f"\n🚀 Starting fetch with {args.delay}s delay between requests...\n")
        success_count = fetcher.fetch_and_save(fixture_ids, delay=args.delay)
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully added {success_count}/{len(fixture_ids)} matches")
        print(f"📁 CSV file: {fetcher.csv_path}")
        print(f"{'='*60}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

# Made with Bob