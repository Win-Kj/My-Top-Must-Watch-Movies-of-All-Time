# import requests
#
# from main import ACCESS_TOKEN
#
# url = "https://api.themoviedb.org/3/search/movie"
#
#
# params = {
#         "query": 'Batman',
#         "include_adult": "false",
#         "language": "en-US",
#         "page": 1
# }
#
# headers = {
#     "accept": "application/json",
#     "Authorization": f"Bearer {ACCESS_TOKEN}"
# }
#
# response = requests.get(url, headers=headers, params=params)
# # print(response.text)
# data = response.json()['results']
# for item in data:
#     title = item['original_title']
#     date = item['release_date']
#     print(f"{title} - {date}")
#
#
