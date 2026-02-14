import trafilatura

url = "https://gbhackers.com/zoom-client-security-flaws/"

downloaded = trafilatura.fetch_url(url)
text = trafilatura.extract(
    downloaded,
    include_links=False,
    include_images=False
)

print(text)
