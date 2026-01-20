#!/usr/bin/env python3
"""
Historical Analysis Generator
Analyzes 2015-2025 Barkley Fall Classic results and generates insights.
"""

import json
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path("data/historical/results")
ANALYSIS_DIR = Path("data/historical/analysis")
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


def load_all_results():
    """Load all historical results from JSON files."""
    results = {}
    
    for year in range(2015, 2026):
        results[year] = {}
        
        for distance in ['50k', 'marathon']:
            file_path = RESULTS_DIR / f"results_{year}_{distance}.json"
            if file_path.exists():
                with open(file_path) as f:
                    results[year][distance] = json.load(f)
    
    return results


def calculate_metrics(results):
    """Calculate comprehensive metrics across all years and distances."""
    metrics = {
        'overall': {},
        'by_year': {},
        'by_distance': {},
        'trends': {}
    }
    
    # Overall metrics
    total_participants = 0
    total_finishers = 0
    
    for year, year_data in results.items():
        metrics['by_year'][year] = {}
        
        for distance, data in year_data.items():
            if not data:
                continue
            # Calculate totals (starters exclude DNS)
            total_starters = (
                data.get('total_finishers', 0)
                + data.get('total_dnf', 0)
                + data.get('total_disqualified', 0)
            )
            finishers = data.get('total_finishers', 0)

            finish_rate = (finishers / total_starters * 100) if total_starters > 0 else 0
            
            metrics['by_year'][year][distance] = {
                'participants': total_starters,
                'finishers': finishers,
                'dnf': data.get('total_dnf', 0),
                'dns': data.get('total_dns', 0),
                'disqualified': data.get('total_disqualified', 0),
                'finish_rate': round(finish_rate, 1)
            }
            
            # Add to overall
            total_participants += total_starters
            total_finishers += finishers
    
    metrics['overall'] = {
        'total_participants': total_participants,
        'total_finishers': total_finishers,
        'overall_finish_rate': round(total_finishers / total_participants * 100, 1) if total_participants > 0 else 0,
        'years_tracked': sorted(results.keys()),
        'years_count': len(results)
    }
    
    # Marathon specific trends
    marathon_rates = []
    for year in sorted(results.keys()):
        if 'marathon' in results[year] and metrics['by_year'][year].get('marathon'):
            marathon_rates.append({
                'year': year,
                'rate': metrics['by_year'][year]['marathon']['finish_rate']
            })
    
    if marathon_rates:
        metrics['trends']['marathon_finish_rates'] = marathon_rates
        metrics['trends']['hardest_year'] = min(marathon_rates, key=lambda x: x['rate'])
        metrics['trends']['easiest_year'] = max(marathon_rates, key=lambda x: x['rate'])
        metrics['trends']['avg_marathon_finish_rate'] = round(
            sum(m['rate'] for m in marathon_rates) / len(marathon_rates), 1
        )
    
    # 50K specific trends
    fiftyK_rates = []
    for year in sorted(results.keys()):
        if '50k' in results[year] and metrics['by_year'][year].get('50k'):
            fiftyK_rates.append({
                'year': year,
                'rate': metrics['by_year'][year]['50k']['finish_rate']
            })
    
    if fiftyK_rates:
        metrics['trends']['50k_finish_rates'] = fiftyK_rates
        metrics['trends']['avg_50k_finish_rate'] = round(
            sum(m['rate'] for m in fiftyK_rates) / len(fiftyK_rates), 1
        )
    
    return metrics


def generate_insights(metrics):
    """Generate human-readable insights from metrics."""
    insights = {
        'summary': [],
        'marathon': [],
        '50k': [],
        'trends': []
    }
    
    overall = metrics['overall']
    trends = metrics['trends']
    
    # Summary insights
    insights['summary'].append(
        f"Over {overall['years_count']} years, {overall['total_participants']:,} "
        f"runners participated with {overall['total_finishers']:,} finishers "
        f"({overall['overall_finish_rate']}% finish rate)"
    )
    
    # Marathon insights
    if 'marathon_finish_rates' in trends:
        avg = trends['avg_marathon_finish_rate']
        hardest = trends['hardest_year']
        easiest = trends['easiest_year']
        
        insights['marathon'].append(f"Average marathon finish rate: {avg}%")
        insights['marathon'].append(
            f"Hardest year: {hardest['year']} ({hardest['rate']}% finish rate)"
        )
        insights['marathon'].append(
            f"Easiest year: {easiest['year']} ({easiest['rate']}% finish rate)"
        )
    
    # 50K insights
    if '50k_finish_rates' in trends:
        avg = trends['avg_50k_finish_rate']
        insights['50k'].append(f"Average 50K finish rate: {avg}%")
        insights['50k'].append("50K is significantly easier than Marathon")
    
    return insights


def main():
    print("🏔️ Barkley Historical Analysis Generator")
    print("=" * 60)
    
    # Load data
    print("\nLoading historical results...")
    results = load_all_results()
    print(f"✓ Loaded data for {len(results)} years")
    
    # Calculate metrics
    print("Calculating metrics...")
    metrics = calculate_metrics(results)
    print(f"✓ Processed {metrics['overall']['total_participants']:,} total participants")
    
    # Generate insights
    print("Generating insights...")
    insights = generate_insights(metrics)
    
    # Save analysis
    analysis_file = ANALYSIS_DIR / "barkley_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'metrics': metrics,
            'insights': insights
        }, f, indent=2)
    
    print(f"✓ Saved analysis to {analysis_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"\nOverall Metrics:")
    print(f"  • Total Participants: {metrics['overall']['total_participants']:,}")
    print(f"  • Total Finishers: {metrics['overall']['total_finishers']:,}")
    print(f"  • Overall Finish Rate: {metrics['overall']['overall_finish_rate']}%")
    
    if insights['marathon']:
        print(f"\nMarathon Insights:")
        for insight in insights['marathon']:
            print(f"  • {insight}")
    
    if insights['50k']:
        print(f"\n50K Insights:")
        for insight in insights['50k']:
            print(f"  • {insight}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete! Historical data is ready.")
    print("=" * 60)


if __name__ == "__main__":
    main()
