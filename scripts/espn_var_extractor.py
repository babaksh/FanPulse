"""
ESPN VAR-Lens Data Extractor with Playwright
Extracts VAR-reviewable decisions from World Cup matches via ESPN

This tool captures the 4 types of decisions that can be reviewed by VAR according to FIFA/IFAB:
1. Goals (and offenses leading up to goals)
2. Penalty decisions
3. Direct red card incidents
4. Mistaken identity

Note: This is NOT a complete referee decisions database - it only includes
decisions that fall under VAR protocol. Yellow cards, regular fouls, and
other non-VAR incidents are excluded.

Usage: python scripts/espn_var_extractor.py
Example URL: https://www.espn.com/soccer/match/_/gameId/760461/uzbekistan-portugal
"""
import asyncio
import json
import sys
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright


def extract_game_id(url):
    """Extract ESPN game ID from URL"""
    match = re.search(r'/gameId/(\d+)', url)
    if match:
        return match.group(1)
    return None


async def scrape_and_extract(match_url):
    """Scrape ESPN and extract VAR events via API interception"""

    game_id = extract_game_id(match_url)
    if not game_id:
        print("[!] Could not extract game ID from URL")
        return None

    print(f"\n{'='*80}")
    print(f"Processing ESPN Game ID: {game_id}")
    print(f"{'='*80}\n")

    async with async_playwright() as p:
        print("[*] Starting browser...")
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        captured_data = {
            'summary': None,
            'plays': None,
            'commentary': None,
        }

        async def handle_response(response):
            url = response.url
            try:
                # Main match summary (has teams, venue, incidents)
                if 'site.web.api.espn.com' in url and 'summary' in url and game_id in url and response.status == 200:
                    data = await response.json()
                    captured_data['summary'] = data
                    print(f"[+] Captured match summary")

                # Play-by-play / commentary
                elif 'site.web.api.espn.com' in url and 'commentary' in url and game_id in url and response.status == 200:
                    data = await response.json()
                    captured_data['commentary'] = data
                    print(f"[+] Captured commentary")

                # Core API plays
                elif 'sports.core.api.espn.com' in url and 'plays' in url and game_id in url and response.status == 200:
                    data = await response.json()
                    captured_data['plays'] = data
                    print(f"[+] Captured plays data")

            except Exception as e:
                if game_id in url:
                    print(f"[!] Error processing {url}: {e}")

        page.on('response', handle_response)

        print(f"[*] Loading page...")
        await page.goto(match_url, wait_until='domcontentloaded', timeout=60000)

        print(f"[*] Waiting for data to load...")
        await asyncio.sleep(8)

        # Scroll to trigger lazy loading
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(3)

        # Try clicking Full Commentary tab to load all commentary
        try:
            await page.click('text=Full Commentary', timeout=3000)
            await asyncio.sleep(4)
        except:
            pass

        # Try clicking commentary/play-by-play tab
        try:
            await page.click('text=Commentary', timeout=2000)
            await asyncio.sleep(4)
        except:
            pass

        await asyncio.sleep(3)

        print(f"\n[*] Captured data summary:")
        print(f"    - Summary:     {'✓' if captured_data['summary'] else '✗'}")
        print(f"    - Commentary:  {'✓' if captured_data['commentary'] else '✗'}")
        print(f"    - Plays:       {'✓' if captured_data['plays'] else '✗'}")

        await browser.close()

        return game_id, captured_data


def extract_var_reviewable_decisions(captured_data):
    """Extract VAR-reviewable decisions from ESPN captured data"""

    summary = captured_data.get('summary', {})
    commentary = captured_data.get('commentary', {})

    if not summary:
        print("[!] No summary data available")
        return None

    # --- Match Info ---
    competition = summary.get('header', {}).get('competitions', [{}])[0]
    competitors = competition.get('competitors', [])

    home_team, away_team = 'Unknown', 'Unknown'
    for c in competitors:
        if c.get('homeAway') == 'home':
            home_team = c.get('team', {}).get('displayName', 'Unknown')
        else:
            away_team = c.get('team', {}).get('displayName', 'Unknown')

    venue_info = competition.get('venue', {})
    venue = venue_info.get('fullName', 'Unknown')
    city = venue_info.get('address', {}).get('city', 'Unknown')

    tournament = summary.get('header', {}).get('league', {}).get('name', 'Unknown')

    date_str = competition.get('date', '')
    try:
        match_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%Y-%m-%d')
    except:
        match_date = datetime.now().strftime('%Y-%m-%d')

    print(f"\n[*] Match: {home_team} vs {away_team}")
    print(f"[*] Date: {match_date}")
    print(f"[*] Tournament: {tournament}")

    # --- Extract Events from scoring plays + key plays ---
    events = []

    # ESPN key plays / scoring summary
    scoring_plays = summary.get('scoringPlays', [])
    key_plays = summary.get('keyPlays', [])
    all_plays = scoring_plays + key_plays

    # Also check rosters for player IDs
    rosters = {}
    for team_roster in summary.get('rosters', []):
        for entry in team_roster.get('entries', []):
            athlete = entry.get('athlete', {})
            rosters[athlete.get('displayName', '')] = athlete.get('id')

    print(f"[*] Analyzing {len(all_plays)} key/scoring plays...\n")

    seen_play_ids = set()

    for play in all_plays:
        play_id = play.get('id', '')
        if play_id in seen_play_ids:
            continue
        seen_play_ids.add(play_id)

        play_type = play.get('type', {}).get('text', '').lower()
        clock = play.get('clock', {}).get('displayValue', '0:00')
        minute = _parse_minute(clock)
        team = play.get('team', {}).get('displayName', '')
        text = play.get('text', '')
        athletes = play.get('participants', [])
        player_name = athletes[0].get('athlete', {}).get('displayName', 'Unknown') if athletes else 'Unknown'
        player_id = athletes[0].get('athlete', {}).get('id') if athletes else None
        is_home = (team == home_team)

        # --- Goal ---
        if 'goal' in play_type and 'own' not in play_type:
            event = {
                'minute': minute,
                'type': 'goal',
                'description': f"Goal by {player_name}",
                'player': player_name,
                'player_id': player_id,
                'is_home': is_home,
                'goal_type': 'regular'
            }
            events.append(event)
            print(f"[+] Goal at {minute}': {player_name}")

        # --- Own Goal ---
        elif 'own goal' in play_type:
            event = {
                'minute': minute,
                'type': 'own_goal',
                'description': f"Own goal by {player_name}",
                'player': player_name,
                'player_id': player_id,
                'is_home': is_home,
                'goal_type': 'ownGoal'
            }
            events.append(event)
            print(f"[+] Own goal at {minute}': {player_name}")

        # --- Penalty ---
        elif 'penalty' in play_type:
            outcome = 'goal' if 'scored' in text.lower() or 'goal' in play_type else 'missed'
            event = {
                'minute': minute,
                'type': 'goal' if outcome == 'goal' else 'penalty_missed',
                'description': f"Penalty {'scored' if outcome == 'goal' else 'missed'} by {player_name}",
                'player': player_name,
                'player_id': player_id,
                'is_home': is_home,
                'goal_type': 'penalty' if outcome == 'goal' else None,
                'note': ''
            }
            events.append(event)
            print(f"[+] Penalty at {minute}': {player_name} ({outcome})")

        # --- Red Card ---
        elif 'red card' in play_type:
            event = {
                'minute': minute,
                'type': 'red_card',
                'description': f"Red card for {player_name}",
                'player': player_name,
                'player_id': player_id,
                'is_home': is_home,
                'note': text if text else ''
            }
            events.append(event)
            print(f"[+] Red card at {minute}': {player_name}")

        # --- VAR ---
        elif 'var' in play_type or 'video review' in play_type or 'video assistant' in text.lower():
            event = {
                'minute': minute,
                'type': 'var_review',
                'description': text if text else 'VAR review conducted',
                'var_decision': {
                    'review_type': _determine_var_type(play_type, text),
                    'player': player_name,
                    'player_id': player_id,
                    'is_home': is_home,
                    'outcome': _determine_var_outcome(play_type, text),
                    'note': text if text else ''
                }
            }
            events.append(event)
            print(f"[+] VAR at {minute}': {text[:80]}")

    # --- Extract VAR from commentary text ---
    var_from_commentary = _extract_var_from_commentary(commentary, home_team, away_team)
    for var_event in var_from_commentary:
        # Avoid duplicates by minute
        existing_minutes = [e['minute'] for e in events if e['type'] == 'var_review']
        if var_event['minute'] not in existing_minutes:
            events.append(var_event)
            print(f"[+] VAR from commentary at {var_event['minute']}': {var_event['description'][:80]}")

    # Sort by minute descending (like SofaScore extractor)
    events.sort(key=lambda x: x['minute'], reverse=True)

    return {
        'match_info': {
            'home_team': home_team,
            'away_team': away_team,
            'date': match_date,
            'tournament': tournament,
            'venue': venue,
            'city': city
        },
        'events': events
    }


def _parse_minute(clock_str):
    """Parse ESPN clock string like '14:00' to minute integer"""
    try:
        parts = clock_str.replace("'", '').split(':')
        return int(parts[0])
    except:
        return 0


def _determine_var_type(play_type, text):
    """Determine VAR review_type from ESPN play type and text"""
    text_lower = text.lower()
    play_lower = play_type.lower()

    if 'penalty' in text_lower or 'penalty' in play_lower:
        if 'not' in text_lower or 'denied' in text_lower or 'overturned' in text_lower:
            return 'penaltyNotAwarded'
        return 'penaltyAwarded'
    elif 'goal' in text_lower or 'goal' in play_lower:
        if 'disallow' in text_lower or 'overturned' in text_lower or 'ruled out' in text_lower:
            return 'goalAwarded'
        return 'goalAwarded'
    elif 'red card' in text_lower or 'red card' in play_lower:
        return 'cardUpgrade'
    elif 'mistaken' in text_lower or 'identity' in text_lower:
        return 'mistakenIdentity'
    return 'review'


def _determine_var_outcome(play_type, text):
    """Determine VAR outcome from ESPN play type and text"""
    text_lower = text.lower()

    if 'goal' in text_lower:
        if 'disallow' in text_lower or 'ruled out' in text_lower or 'overturned' in text_lower or 'foul' in text_lower or 'offside' in text_lower:
            return 'goal_disallowed'
        return 'goal_confirmed'
    elif 'penalty' in text_lower:
        if 'not awarded' in text_lower or 'no penalty' in text_lower or 'overturned' in text_lower:
            return 'penalty_not_awarded'
        return 'penalty_awarded'
    elif 'red' in text_lower:
        return 'card_upgraded'
    return 'reviewed'


def _extract_var_from_commentary(commentary, home_team, away_team):
    """Scan ESPN commentary entries for VAR mentions"""
    var_events = []
    if not commentary:
        return var_events

    entries = commentary.get('commentary', []) or commentary.get('items', [])

    var_keywords = ['var', 'video review', 'video assistant referee', 'offside check',
                    'penalty check', 'goal check', 'overturned', 'disallowed', 'ruled out']

    for entry in entries:
        text = entry.get('text', '') or entry.get('comment', '')
        if not text:
            continue

        text_lower = text.lower()
        if any(kw in text_lower for kw in var_keywords):
            clock = entry.get('clock', {}).get('displayValue', '0') if isinstance(entry.get('clock'), dict) else str(entry.get('clock', '0'))
            minute = _parse_minute(clock)

            event = {
                'minute': minute,
                'type': 'var_review',
                'description': text[:200],
                'var_decision': {
                    'review_type': _determine_var_type('var', text),
                    'player': 'Unknown',
                    'player_id': None,
                    'is_home': None,
                    'outcome': _determine_var_outcome('var', text),
                    'note': text
                }
            }
            var_events.append(event)

    return var_events


def save_files(game_id, captured_data, var_data):
    """Save raw and processed VAR-reviewable decisions data"""

    # Save raw data
    os.makedirs('data/espn_json', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_file = f"data/espn_json/espn_{game_id}_{timestamp}.json"

    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(captured_data, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Saved raw data: {raw_file}")

    # Save VAR-reviewable decisions
    if var_data and var_data['events']:
        os.makedirs('data/referee_decisions', exist_ok=True)

        info = var_data['match_info']
        home = info['home_team'].replace(' ', '_').upper()
        away = info['away_team'].replace(' ', '_').upper()
        date = info['date']

        tournament = info['tournament']
        if 'World Cup' in tournament or 'WC' in tournament:
            code = 'WC'
        elif 'Champions' in tournament:
            code = 'UCL'
        else:
            code = 'MATCH'

        filename = f"data/referee_decisions/{code}_{date}_{home}_{away}.json"

        output = {
            'match_id': f"{code}_{date}_{home}_{away}",
            'match_info': info,
            'var_protocol_note': "This file contains only VAR-reviewable decisions according to FIFA/IFAB protocol: Goals, Penalties, Red Cards, and Mistaken Identity. Yellow cards and other non-VAR incidents are excluded.",
            'events': var_data['events']
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"[+] Saved VAR-reviewable decisions: {filename}")
        print(f"\n[*] Total VAR-reviewable events: {len(var_data['events'])}")
        print(f"[*] Events with VAR review: {sum(1 for e in var_data['events'] if 'var_decision' in e or e.get('var_reviewed'))}")
        print(f"[*] Goals: {sum(1 for e in var_data['events'] if e['type'] in ['goal', 'own_goal'])}")
        print(f"[*] Penalties: {sum(1 for e in var_data['events'] if e['type'] == 'penalty')}")
        print(f"[*] Red cards: {sum(1 for e in var_data['events'] if e['type'] == 'red_card')}")

        return filename

    return None


async def main():
    print("\n" + "="*80)
    print("ESPN VAR-Lens Data Extractor")
    print("="*80)
    print("\nExtracts VAR-reviewable decisions (Goals, Penalties, Red Cards, Mistaken Identity)")
    print("Note: Yellow cards and non-VAR incidents are excluded per FIFA/IFAB protocol")
    print("\nPlease enter the ESPN match URL:")
    print("Example: https://www.espn.com/soccer/match/_/gameId/760461/uzbekistan-portugal")
    print("\nURL: ", end="")

    match_url = input().strip()

    if not match_url:
        print("\n[!] No URL provided. Exiting.")
        sys.exit(1)

    # Scrape
    result = await scrape_and_extract(match_url)
    if not result:
        sys.exit(1)

    game_id, captured_data = result

    # Extract
    if not captured_data['summary']:
        print("\n[!] No summary data captured")
        print("[!] This could mean:")
        print("    1. The page didn't load completely - try increasing wait time")
        print("    2. ESPN changed their API structure")
        print("\n[*] Saving raw captured data for debugging...")

        os.makedirs('data/espn_json', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        debug_file = f"data/espn_json/debug_{game_id}_{timestamp}.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(captured_data, f, indent=2, ensure_ascii=False)
        print(f"[+] Debug data saved: {debug_file}")
    else:
        var_data = extract_var_reviewable_decisions(captured_data)

        if not var_data or not var_data['events']:
            print("\n[!] No VAR-reviewable decisions found")
            print("[*] This match may not have any goals, penalties, red cards, or mistaken identity incidents")
        else:
            save_files(game_id, captured_data, var_data)

    print(f"\n{'='*80}")
    print("Complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
