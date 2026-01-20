#!/usr/bin/env python3
"""
Analysis module for Barkley Fall Classic historical results.
Generates trend data, demographics, and finish statistics.
"""

import json
import csv
from pathlib import Path
from collections import Counter, defaultdict
from statistics import mean, stdev, median

DATA_DIR = Path(__file__).parent / "data" / "historical"
RESULTS_DIR = DATA_DIR / "results"
ANALYSIS_DIR = DATA_DIR / "analysis"

# Ensure directories exist
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

class HistoricalAnalyzer:
    def __init__(self, archive_path=None):
        if archive_path is None:
            archive_path = DATA_DIR / "barkley_archive_complete.json"
        
        self.archive_path = archive_path
        self.data = self._load_archive()
    
    def _load_archive(self):
        """Load the complete archive."""
        if not self.archive_path.exists():
            print(f"Archive not found: {self.archive_path}")
            return []
        
        with open(self.archive_path, 'r') as f:
            return json.load(f)
    
    def generate_all_analysis(self):
        """Generate all analysis reports."""
        print("Generating analysis reports...")
        
        self.generate_yearly_summary()
        self.generate_demographic_trends()
        self.generate_finish_statistics()
        self.generate_location_analysis()
        self.generate_age_analysis()
        self.generate_gender_trends()
        self.generate_distance_comparison()
        
        print("✓ All analysis reports generated")
    
    def generate_yearly_summary(self):
        """Generate year-by-year summary statistics."""
        summary = []
        
        for year_data in self.data:
            year = year_data['year']
            distance = year_data.get('distance', 'Unknown')
            finishers = year_data['finishers']
            
            finished = [f for f in finishers if f['status'] == 'Finished']
            
            summary.append({
                'year': year,
                'distance': distance,
                'total_starters': len(finishers),
                'total_finished': len(finished),
                'finish_rate': round(len(finished) / len(finishers) * 100, 1) if finishers else 0,
                'dnf_total': year_data['total_dnf'],
                'dns_total': year_data['total_dns'],
                'avg_finish_time_hours': self._avg_finish_time(finished),
                'median_finish_time_hours': self._median_finish_time(finished),
            })
        
        output_file = ANALYSIS_DIR / "yearly_summary.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"  ✓ Yearly summary: {output_file}")
        return summary
    
    def generate_demographic_trends(self):
        """Analyze demographic changes over time."""
        trends = defaultdict(list)
        
        for year_data in self.data:
            year = year_data['year']
            finished = [f for f in year_data['finishers'] if f['status'] == 'Finished']
            
            ages = [f['age'] for f in finished if f['age']]
            divisions = Counter(f['division'] for f in finished)
            
            trends[year] = {
                'year': year,
                'avg_age': round(mean(ages), 1) if ages else None,
                'median_age': median(ages) if ages else None,
                'gender_distribution': dict(divisions),
                'finisher_count': len(finished),
            }
        
        output_file = ANALYSIS_DIR / "demographic_trends.json"
        with open(output_file, 'w') as f:
            json.dump(dict(trends), f, indent=2)
        
        print(f"  ✓ Demographic trends: {output_file}")
        return trends
    
    def generate_finish_statistics(self):
        """Analyze finish time statistics."""
        stats = []
        
        for year_data in self.data:
            year = year_data['year']
            
            # By distance
            for distance in ['50K', 'Marathon']:
                finished = [
                    f for f in year_data['finishers']
                    if f['distance'] == distance and f['status'] == 'Finished' and f['finish_time_seconds']
                ]
                
                if finished:
                    times = [f['finish_time_seconds'] for f in finished]
                    times_hours = [t / 3600 for t in times]
                    
                    stats.append({
                        'year': year,
                        'distance': distance,
                        'finishers': len(finished),
                        'avg_time_hours': round(mean(times_hours), 2),
                        'median_time_hours': round(median(times_hours), 2),
                        'min_time_hours': round(min(times_hours), 2),
                        'max_time_hours': round(max(times_hours), 2),
                        'stdev_hours': round(stdev(times_hours), 2) if len(times_hours) > 1 else 0,
                    })
        
        output_file = ANALYSIS_DIR / "finish_statistics.json"
        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"  ✓ Finish statistics: {output_file}")
        return stats
    
    def generate_location_analysis(self):
        """Analyze where finishers are from."""
        locations = defaultdict(lambda: {'total': 0, 'finished': 0, 'dnf': 0})
        
        for year_data in self.data:
            for finisher in year_data['finishers']:
                city_state = finisher['city']
                locations[city_state]['total'] += 1
                
                if finisher['status'] == 'Finished':
                    locations[city_state]['finished'] += 1
                elif finisher['status'] == 'DNF':
                    locations[city_state]['dnf'] += 1
        
        # Sort by participation
        sorted_locations = sorted(
            locations.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )
        
        location_data = []
        for loc, stats in sorted_locations[:100]:  # Top 100 locations
            location_data.append({
                'location': loc,
                'total_participants': stats['total'],
                'finishers': stats['finished'],
                'dnf': stats['dnf'],
                'finish_rate': round(stats['finished'] / stats['total'] * 100, 1) if stats['total'] > 0 else 0,
            })
        
        output_file = ANALYSIS_DIR / "location_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(location_data, f, indent=2)
        
        print(f"  ✓ Location analysis: {output_file}")
        return location_data
    
    def generate_age_analysis(self):
        """Analyze age group trends."""
        age_groups = {
            '<20': (0, 20),
            '20-29': (20, 30),
            '30-39': (30, 40),
            '40-49': (40, 50),
            '50-59': (50, 60),
            '60-69': (60, 70),
            '70+': (70, 150),
        }
        
        trends = []
        
        for year_data in self.data:
            year = year_data['year']
            year_trends = {'year': year}
            
            for group_name, (min_age, max_age) in age_groups.items():
                finished = [
                    f for f in year_data['finishers']
                    if f['status'] == 'Finished' and f['age'] and min_age <= f['age'] < max_age
                ]
                total = [
                    f for f in year_data['finishers']
                    if f['age'] and min_age <= f['age'] < max_age
                ]
                
                year_trends[f"{group_name}_finished"] = len(finished)
                year_trends[f"{group_name}_total"] = len(total)
                year_trends[f"{group_name}_rate"] = round(
                    len(finished) / len(total) * 100, 1
                ) if total else 0
            
            trends.append(year_trends)
        
        output_file = ANALYSIS_DIR / "age_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(trends, f, indent=2)
        
        print(f"  ✓ Age analysis: {output_file}")
        return trends
    
    def generate_gender_trends(self):
        """Analyze gender participation and finish rates."""
        trends = []
        
        for year_data in self.data:
            year = year_data['year']
            
            for gender in ['M', 'F', 'X']:
                finished = [
                    f for f in year_data['finishers']
                    if f['division'] == gender and f['status'] == 'Finished'
                ]
                total = [f for f in year_data['finishers'] if f['division'] == gender]
                
                if total:
                    trends.append({
                        'year': year,
                        'gender': gender,
                        'total_participants': len(total),
                        'finishers': len(finished),
                        'finish_rate': round(len(finished) / len(total) * 100, 1),
                    })
        
        output_file = ANALYSIS_DIR / "gender_trends.json"
        with open(output_file, 'w') as f:
            json.dump(trends, f, indent=2)
        
        print(f"  ✓ Gender trends: {output_file}")
        return trends
    
    def generate_distance_comparison(self):
        """Compare 50K vs Marathon performance."""
        comparison = []
        
        for year_data in self.data:
            year = year_data['year']
            
            for distance in ['50K', 'Marathon']:
                finished = [
                    f for f in year_data['finishers']
                    if f['distance'] == distance and f['status'] == 'Finished'
                ]
                started = [f for f in year_data['finishers'] if f['distance'] == distance]
                
                comparison.append({
                    'year': year,
                    'distance': distance,
                    'started': len(started),
                    'finished': len(finished),
                    'finish_rate': round(len(finished) / len(started) * 100, 1) if started else 0,
                })
        
        output_file = ANALYSIS_DIR / "distance_comparison.json"
        with open(output_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        print(f"  ✓ Distance comparison: {output_file}")
        return comparison
    
    def _avg_finish_time(self, finishers):
        """Calculate average finish time in hours."""
        times = [f['finish_time_seconds'] for f in finishers if f['finish_time_seconds']]
        if times:
            return round(mean(times) / 3600, 2)
        return None
    
    def _median_finish_time(self, finishers):
        """Calculate median finish time in hours."""
        times = [f['finish_time_seconds'] for f in finishers if f['finish_time_seconds']]
        if times:
            return round(median(times) / 3600, 2)
        return None

def main():
    analyzer = HistoricalAnalyzer()
    analyzer.generate_all_analysis()

if __name__ == '__main__':
    main()
