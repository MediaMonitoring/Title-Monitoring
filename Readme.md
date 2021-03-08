Years ago, I noticed that some of the news headlines change when I re-check them at later stages and I wanted to investigate this. With the help of a developer, we built an algorithm hosted on AWS to scrape the titles of these news articles.

We were surprised by the amount of data that we have collected. In 15 months, New York Times had ~21k articles that had their titles changed, Financial Times ~17k, and Wall Street Journal ~10k.
90% of these articles changed only once which means that they are not unfolding news event updates.

If we consider that these newspapers publish 250 articles a day, then 10% to 20% of the articles' titles are changed.

Digging deeper into the data, I found out that two-thirds of the time the titles had been changed to rectify a typo or for a slight adjustment. However, one-third had a change that is "interesting" that can potentially have an impact on the reader.
Categorising the "interesting" articles is a difficult exercise to automate as it requires a knowledge of the local news.
