"""
AI-Powered Sugya Extraction CLI Tool

Usage:
    python extract_sugyot_ai.py --tractate Berakhot --start-page 2a --limit 50
    python extract_sugyot_ai.py --help
"""
import os
os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI", "neo4j+s://8260863b.databases.neo4j.io")
os.environ["NEO4J_USER"] = os.getenv("NEO4J_USER", "neo4j")
os.environ["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD", "IJYDpas_0uO5jbjB6Upk7uiEn_Gs-nb9vyO3oUH6v5c")

import argparse
from ai.sugya_extractor import get_sugya_extractor
import json

def main():
    parser = argparse.ArgumentParser(
        description='AI-Powered Sugya Extraction from Talmudic Texts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from Berakhot starting at page 2a
  python extract_sugyot_ai.py --tractate Berakhot --start-page 2a --limit 50
  
  # Extract with custom settings
  python extract_sugyot_ai.py --tractate Shabbat --start-page 10a --limit 100
  
  # Quick test extraction (default settings)
  python extract_sugyot_ai.py

Notes:
  - Requires OPENAI_API_KEY in .env file
  - Without API key, will use simulated AI analysis
  - Results are saved to Neo4j database
  - Process may take several minutes
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Extract from ALL tractates in the database (automatic discovery)'
    )
    
    parser.add_argument(
        '--tractate',
        type=str,
        default='Berakhot',
        help='Talmudic tractate to analyze (default: Berakhot, ignored if --all is used)'
    )
    
    parser.add_argument(
        '--start-page',
        type=str,
        default='2a',
        help='Starting page reference (default: 2a, empty for all pages)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of texts to analyze per tractate (default: 50)'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        help='Export results to JSON file (optional)'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🤖 AI-POWERED SUGYA EXTRACTION")
    print("=" * 80)
    
    if args.all:
        print("Mode: EXTRACT FROM ALL TRACTATES (Automatic Discovery)")
        print(f"Limit per tractate: {args.limit}")
    else:
        print(f"Mode: Single Tractate")
        print(f"Tractate: {args.tractate}")
        print(f"Starting page: {args.start_page}")
        print(f"Limit: {args.limit}")
    
    print("=" * 80)
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-openai-api-key-here":
        print("\n⚠️  WARNING: OPENAI_API_KEY not found in environment")
        print("   AI extraction will use simulated analysis")
        print("   Set your API key in backend/.env to enable real AI analysis")
        print()
        
        response = input("Continue with simulated analysis? (y/n): ")
        if response.lower() != 'y':
            print("Extraction cancelled.")
            return
    else:
        print("✅ OpenAI API key found - using GPT-4 for analysis")
    
    # Run extraction
    extractor = get_sugya_extractor()
    
    if args.all:
        # Extract from ALL tractates
        stats = extractor.extract_all_sugyot(
            limit_per_tractate=args.limit
        )
    else:
        # Extract from single tractate
        stats = extractor.extract_and_save_all(
            tractate=args.tractate,
            start_page=args.start_page,
            limit=args.limit
        )
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 80)
    
    if args.all:
        # Summary for all tractates
        print(f"Tractates Found: {stats.get('tractates_found', 0)}")
        print(f"Tractates Processed: {stats.get('tractates_processed', 0)}")
        print(f"Total Extracted: {stats.get('total_extracted', 0)}")
        print(f"Successfully Saved: {stats.get('total_saved', 0)}")
        print(f"Failed: {stats.get('total_failed', 0)}")
        
        print("\n📋 Details by Tractate:")
        for detail in stats.get('tractate_details', []):
            if 'error' in detail:
                print(f"  ❌ {detail['tractate']}: {detail['error']}")
            else:
                print(f"  ✅ {detail['tractate']}: Extracted {detail['extracted']}, Saved {detail['saved']}")
    else:
        # Summary for single tractate
        print(f"Tractate: {stats.get('tractate', 'N/A')}")
        print(f"Start Page: {stats.get('start_page', 'N/A')}")
        print(f"Total Extracted: {stats.get('total_extracted', 0)}")
        print(f"Successfully Saved: {stats.get('saved', 0)}")
        print(f"Failed: {stats.get('failed', 0)}")
    
    print("=" * 80)
    
    # Export if requested
    if args.export:
        with open(args.export, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results exported to: {args.export}")
    
    # Next steps
    print("\n📖 Next Steps:")
    print("   1. View sugyot in Neo4j Browser")
    print("   2. Start backend: uvicorn main:app --reload")
    print("   3. Test API: http://localhost:8000/docs")
    print("   4. Use frontend to explore extracted sugyot")
    print()

if __name__ == "__main__":
    main()

