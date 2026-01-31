# Advertising Campaign Data Dictionary

This document defines each field in the advertising campaign dataset, including its meaning, data type, and additional details.

| Field Name           | Data Type       | Description |
|----------------------|-----------------|-------------|
| campaign_item_id     | STRING / UUID   | Unique identifier for each advertising campaign. Used to differentiate individual campaigns across all records. |
| no_of_days           | INTEGER         | Number of days the campaign has been active. Calculated from campaign start date to current data capture date. |
| time                 | DATETIME        | Timestamp when the data snapshot was captured (in campaign's time zone). |
| ext_service_id       | STRING          | Unique identifier for each advertising platform used (e.g., Google Ads, Facebook Ads). |
| ext_service_name     | STRING          | Name of the advertising platform (e.g., "Google Ads", "Meta Ads"). |
| creative_id          | STRING / UUID   | Unique identifier for the creative asset used in the ad (image, video, etc.). |
| creative_height      | INTEGER         | Height of the creative asset in pixels. |
| creative_width       | INTEGER         | Width of the creative asset in pixels. |
| search_tags          | STRING / ARRAY  | Search terms or keywords used for targeting the ads. Can be a comma-separated list or array. |
| template_id          | STRING          | Identifier for the template used to generate the creative asset. |
| landing_page         | STRING (URL)    | Destination URL where users are directed after clicking the ad. |
| advertiser_id        | STRING / UUID   | Unique identifier for the advertiser running the campaign. |
| advertiser_name      | STRING          | Name of the advertiser, including location details (city, state, country). |
| network_id           | STRING / UUID   | Identifier for the advertising agency or network managing the campaign. |
| advertiser_currency  | STRING          | ISO currency name in which the advertiser operates (e.g., "US Dollar"). |
| channel_id           | STRING / UUID   | Identifier for the advertising channel used (display, search, social, video). |
| channel_name         | STRING          | Name/type of the advertising channel (e.g., "Display", "Search", "Social", "Mobile Video"). |
| max_bid_cpm          | DECIMAL(10,4)   | Maximum cost per thousand impressions (CPM) bid value set for campaign optimization. |
| campaign_budget_usd  | DECIMAL(15,2)   | Total allocated budget for the campaign, expressed in USD. |
| impressions          | BIGINT          | Total number of times the ad was displayed. |
| clicks               | BIGINT          | Total number of times the ad was clicked by users. |
| currency_code        | STRING          | ISO currency code representing the advertiser's local currency (e.g., "USD", "EUR"). |
| exchange_rate        | DECIMAL(10,6)   | Conversion rate from the advertiser's currency to USD at the time of data capture. |
| media_cost_usd       | DECIMAL(15,2)   | Amount spent on media buying on the given day, expressed in USD. |
| position_in_content  | STRING          | Placement of the ad on the webpage or platform (e.g., "Top Banner", "Sidebar", "In-Feed"). |
| unique_reach         | BIGINT          | Number of unique users who saw the ad. |
| total_reach          | BIGINT          | Total number of times the ad content was viewed, including repeated views by the same users. |
| cmi_currency_code    | STRING          | ISO currency code in which the campaign's budget and bids are set. |
| time_zone            | STRING          | Time zone in which the campaign operates (e.g., "America/New_York"). |
| weekday_cat          | STRING          | Categorization of the date as "Weekday" or "Weekend". |
| keywords             | STRING / ARRAY  | Keywords used for ad targeting in search engines. Can be a comma-separated list or array. |

**Notes:**
- Date/time fields should follow ISO 8601 format.
- Currency codes should follow ISO 4217 standards.
- Numeric fields for costs should use two decimal places unless higher precision is needed.
