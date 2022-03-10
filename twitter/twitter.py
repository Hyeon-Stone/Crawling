from Scweet.scweet import scrape

keyword = "코로나"
data = scrape(words=[keyword], since="2021-11-01", until="2021-11-02", from_account = None, interval=1, headless=False, display_type="Top", save_images=True, lang="ko",
	resume=False, filter_replies=False, proximity=False)

print(data)
data.to_csv(f".\\{keyword}.csv",sep = ",", na_rep = "NaN")