import json

# Load the Marathon results
with open('data/historical/results/results_2025_marathon.json', 'r') as f:
    data = json.load(f)

print(f"=== 2025 Marathon Results ===")
print(f"Finishers: {data['total_finishers']}")
print(f"DNF: {data['total_dnf']}")
print(f"DNS: {data['total_dns']}")
print(f"Total participants: {len(data['finishers'])}")

# Verify counts match
finished = [f for f in data['finishers'] if f['status'] == 'Finished']
dnf = [f for f in data['finishers'] if f['status'] == 'DNF']
dns = [f for f in data['finishers'] if f['status'] == 'DNS']

print(f"\nVerification:")
print(f"  Actual Finished: {len(finished)}")
print(f"  Actual DNF: {len(dnf)}")
print(f"  Actual DNS: {len(dns)}")

print(f"\nSample Finisher:")
if finished:
    f = finished[0]
    print(f"  {f['first_name']} {f['last_name']} - Place {f['place']} - {f['finish_time_formatted']}")

print(f"\nSample DNF:")
if dnf:
    d = dnf[0]
    print(f"  {d['first_name']} {d['last_name']} - Place {d['place']}")

print(f"\nSample DNS:")
if dns:
    d = dns[0]
    print(f"  {d['first_name']} {d['last_name']} - Place {d['place']}")
