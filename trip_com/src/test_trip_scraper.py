"""
Trip.com 호텔 리뷰 API 테스트 스크립트
"""
import json
from scrapling import Fetcher

def test_fetch():
    url = "https://kr.trip.com/restapi/soa2/34308/getHotelCommentInfo"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "w-payload-source": "1.0.9@102!Nudtz1KLhCAbOX4SO6An9PKnG2KLOSqZOlbn+6FaG6OaKSbpKET2OSVbOrK2+ET5+rApbbbpOSknKr42+rG2KlqIbEVbKtb5+rbSOEb2KE4p+rKpOr4nKrq/K5bpOSqL+rk/OSKZKrVpQlVROShDKFO3GVd3hbb=",
        "x-ctx-country": "KR",
        "x-ctx-currency": "KRW",
        "x-ctx-locale": "ko-KR",
        "x-ctx-ubt-pageid": "10320668147",
        "x-ctx-ubt-pvid": "7",
        "x-ctx-ubt-sid": "9",
        "x-ctx-ubt-vid": "1754985737191.9877n1SlbHlt",
        "x-ctx-user-recognize": "NON_EU",
        "x-ctx-wclient-req": "0af33fe7acb74bcfe9f82cf404544b46"
    }
    
    payload = {
        "hotelId": 58635410,
        "commentFilterOptions": {
            "pageIndex": 1,
            "pageSize": 10,
            "repeatComment": 1
        },
        "sceneTypes": ["CommentList"],
        "head": {
            "platform": "PC",
            "cver": "0",
            "cid": "1754985737191.9877n1SlbHlt",
            "bu": "IBU",
            "group": "trip",
            "aid": "",
            "sid": "",
            "ouid": "",
            "locale": "ko-KR",
            "timezone": "9",
            "currency": "KRW",
            "pageId": "10320668147",
            "vid": "1754985737191.9877n1SlbHlt",
            "guid": "",
            "isSSR": False
        }
    }
    
    fetcher = Fetcher()
    response = fetcher.post(url, headers=headers, json=payload)
    
    print("Status:", response.status)
    if response.status == 200:
        data = response.json()
        print("Data Keys:", data.keys())
        if 'data' in data:
            print("Inner Data Keys:", data['data'].keys())
            if 'groupList' in data['data']:
                groups = data['data']['groupList']
                print(f"Number of groups: {len(groups)}")
                if len(groups) > 0:
                    print("Group keys:", groups[0].keys())
                    if 'commentList' in groups[0]:
                        comments = groups[0]['commentList']
                        print(f"Number of comments in first group: {len(comments)}")
                        if len(comments) > 0:
                            c = comments[0]
                            print("Sample comment keys:", c.keys())
                            print("Sample title:", c.get('title', c.get('subject')))
                            print("Sample content:", c.get('content')[:100] if c.get('content') else None)
                            print("Sample rating:", c.get('rating'))
            else:
                print("No groupList found.")

if __name__ == "__main__":
    test_fetch()
