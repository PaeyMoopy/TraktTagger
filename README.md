# TraktTagger
<a href="https://www.paypal.com/ncp/payment/DKGKXXEYNDS7S" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

This is a simple Python script that uses Trakt lists to make Radarr tags dynamic.

To use, clone the repo or download the file, then edit the .py

You **Must** have a Trakt account for this, and set up a Client ID and Secret. Do this here: https://trakt.tv/oauth/applications
Once you have added the Client ID and Secret, add your Radarr information. 

The lists used must match API format. The **EASIEST** way to do this is to press the "Share" button on the list and copy the link. 
  Example: 
      The list you want to use: https://trakt.tv/users/linaspurinis/lists/top-watched-movies-of-the-week-60?sort=rank,asc
      The link when shared: https://trakt.tv/lists/6703173
      The link to add to the .py file: https://api.trakt.tv/lists/6703173/items

      Enter the final link in your browser to see if it worked, a wall of text is a good thing! This has only been tested on public lists.

The Trakt Lists function works like this:
{"url": "https://api.trakt.tv/lists/6703173/items", "tag_name": "topmoviesweek", "expired_tag_name": "delete"},
URL is as described above.
tag_name should be changed from "topmoviesweek" to whatever you want EVERY ITEM in the Trakt list to be tagged as in Radarr. 
expired_tag_name is whatever anything CURRENTLY tagged as the tag_name gets replaced to, once that item is NO LONGER in the Trakt list. 
You can set this as None to have it simply remove the tag, rather than replacing it. Like this: "expired_tag_name": None},

This is designed to do EXACTLY what you tell it to do. Make sure you fully understand how it works or test it on a small library before full deployment.
