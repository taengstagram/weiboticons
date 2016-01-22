
This generates json files that list the emoticons returned by the Weibo API endpoint http://open.weibo.com/wiki/2/emotions

List of Generated Files:

- [weibo_emojis.nolegacy.full.json](weibo_emojis.nolegacy.full.json) ([minified](weibo_emojis.nolegacy.full.min.json)) - list of current Weibo emoji phrases and their full image links .
- [weibo_emojis.full.json](weibo_emojis.full.json) ([minified](weibo_emojis.full.min.json)) - list of Weibo emoji phrases and their full image links, includes legacy emojis that the Weibo API no longer returns.
- [weibo_emojis.relative.json](weibo_emojis.relative.json) ([minified](weibo_emojis.relative.min.json)) - list of Weibo emoji phrases and their relative image links (includes legacy). This is useful if you intend to use a self-hosted mirror of the emoji images.

To generate the json files, use the [weibo_emoji_scraper.py](weibo_emoji_scraper.py) python script.

``python weibo_emoji_scraper.py --key "<YOUR_WEIBO_KEY>" --secret "<YOUR_WEIBO_SECRET>" --token "<YOUR_wEIBO_TOKEN>"``

Included also is a [simple js library](libs/js/weiboticons.js) ([minified](libs/js/weiboticons.min.js)) that you can use to convert Weibo emoji phrases into their images:
```javascript
weibo_emoji_text = 'Aweseome! [害羞][赞]';
new_text = weiboticons.replace(weibo_emoji_text); // 'Awesome! <img class="weiboticon" title="[害羞]" src="http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/6e/shamea_org.gif"><img class="weiboticon" title="[赞]" src="http://img.t.sinajs.cn/t4/appstyle/expression/ext/normal/d0/z2_org.gif">';
```
