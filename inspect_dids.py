import requests, re
url = 'https://ultrasignup.com/results_event.aspx?did=116578'
h = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}).text
links = sorted(set(re.findall(r'results_event\.aspx\?did=\d+', h)))
print('Found links:', links)
