해당 데이터를 보여주는 주소
https://www.saramin.co.kr/zf_user/search/recruit?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword=%EB%A7%88%EC%BC%80%ED%84%B0&recruitPage=2&recruitSort=relation&recruitPageCount=40&inner_com_type=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&show_applied=&quick_apply=&except_read=&ai_head_hunting=

실제 데이터를 가져오는 정보
5. 한페이지가 성공적으로 수집되는지 확인하고 sqlitedb파일로 저장하고 JSON데이터는 별도의 컬럼으로 저장할 것

* 한페이지가 성공적으로 수집되었다면, 1~10페이지까지 수집하고 수집이 잘 되었는지 확인하고 결과 리포트를 보여줄 것
* 해당 정보를 수집하는 목적은 기업명, 채용공고 세부내용, 채용조건 등 채용공고 주요 데이터를 모두 수집하는 것입니다.

6. 채용공고 목록이 수집이 되었다면 채용공고 상세페이지 정보를 수집할 것. 상세페이지는 별도의 테이블로 구성할 것

추후 채용공고와 상세페이지를 조인해서 채용공고 정보를 분석할 것

* 수집 요청을 보낼때는 0.1~1초씩 쉬었다가 수집하게 할 것 네트워크 부담을 줄일 것

7. 데이터베이스에 저장할 때는 중복데이터가 발생하지 않도록 기존데이터가 있다면 업데이트 하는 방법으로 수집할 것

1) HTTP 
Request URL
https://www.saramin.co.kr/zf_user/search/recruit?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword=%EB%A7%88%EC%BC%80%ED%84%B0&recruitPage=2&recruitSort=relation&recruitPageCount=40&inner_com_type=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&show_applied=&quick_apply=&except_read=&ai_head_hunting=
Request Method
GET
Status Code
200 OK
Remote Address
182.162.86.29:443
Referrer Policy
strict-origin-when-cross-origin
accept-ch
Sec-CH-UA-Platform-Version
cache-control
no-store, no-cache, must-revalidate
content-encoding
gzip
content-type
text/html; charset=UTF-8
critical-ch
Sec-CH-UA-Platform-Version
date
Sat, 27 Jun 2026 06:47:55 GMT
expires
Thu, 19 Nov 1981 08:52:00 GMT
pragma
no-cache
server
SWS
set-cookie
RSRVID=web31|aj9yH|aj9sk; path=/
transfer-encoding
chunked
accept
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
accept-encoding
gzip, deflate, br, zstd
accept-language
ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7
cache-control
max-age=0
connection
keep-alive
cookie
PCID=17554864216358143340984; ab180ClientId=b80ec89c-e9c2-4efe-9cf0-419b3dcc53f7; Mtype=P; saramin_last_login_provider=naver; _ga_DBVYV88LS9csn=VDJ5REsrWGFJVmdnY2RoeTB2YkMvZz09=GS2.1.s1768233669$o1$g0$t1768233669$j60$l0$h0; airbridge_user__saramin=%7B%22externalUserID%22%3A%2213720210%22%2C%22alias%22%3A%7B%22amplitude_id%22%3A%2213720210%22%7D%7D; saramin_login_tab_default=p; AMP_a687efd08d=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJDYVV5bWRudkcyYmpNTzdrYjNtSnJ6JTIyJTJDJTIydXNlcklkJTIyJTNBJTIyMTM3MjAyMTAlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzc2Njg2NDE0MzYyJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc3NjY4NjQxNDM2NCUyQyUyMmxhc3RFdmVudElkJTIyJTNBNCUyQyUyMnBhZ2VDb3VudGVyJTIyJTNBMCU3RA==; HideEditConditionTooltip=y; _ga_DBVYV88LS9=GS2.1.s1777689639$o7$g1$t1777689665$j34$l0$h0; ab.storage.deviceId.a2ac6b71-3416-464a-ac48-ef2cff5c2026=%7B%22g%22%3A%227370b821-d22d-fe39-302a-7f224487414d%22%2C%22c%22%3A1755486553296%2C%22l%22%3A1780316655818%7D; ab.storage.userId.a2ac6b71-3416-464a-ac48-ef2cff5c2026=%7B%22g%22%3A%2213720210%22%2C%22c%22%3A1761491761236%2C%22l%22%3A1780316655819%7D; amp_a687ef=QHmcO52-IXKquDl3xqLIFi.MTM3MjAyMTA=..1jq1i8k5s.1jq1m06gf.h.4j.54; ab.storage.sessionId.a2ac6b71-3416-464a-ac48-ef2cff5c2026=%7B%22g%22%3A%22d162b38d-171e-30ba-53c1-c3b88300379f%22%2C%22e%22%3A1780322373972%2C%22c%22%3A1780316655817%2C%22l%22%3A1780320573972%7D; _ga_L2PN791WR5=GS2.1.s1780317607$o30$g1$t1780320677$j60$l0$h0; _ga_0PN5NFZW7P=GS2.1.s1780317607$o30$g1$t1780320677$j60$l0$h0; PHPSESSID=267la9qosv9ilqac71fma1jg4o2cvpu86tq437o9eqbe0g7alt; _gid=GA1.3.1313774138.1782541454; _gcl_au=1.1.92811635.1782541455; airbridge_migration_metadata__saramin=%7B%22version%22%3A%221.11.12%22%7D; _ga_58W0W855T7=GS2.1.s1782541454$o34$g0$t1782541457$j57$l0$h0; RSRVID=web31|aj9xb|aj9sk; cto_bundle=WjJHC19mUUFGbGdoUkxPdGF0SiUyRlA5elpvb1ZxV3o0dnBGT1ppWjNKTjNvZHdOZWNtSEUzVzFKSTlQVGhPWGVveHJKT054UUlkN3BTUFE0dlVXTDY2QlJ4eFNhS2dmNTRXdSUyQnF5UmZlOFRkViUyRmhZbmhwcGhhWVM0MVpwY1REVVBMQW1ja3QzUTdzdjdDb1pZMWprcldXVDFoTnclM0QlM0Q; _ga=GA1.1.1716532447.1755486523; _ga_GR2XRGQ0FK=GS2.1.s1782541454$o50$g1$t1782542698$j58$l0$h0; _ga_E0LMXXGRZK=GS2.1.s1782541458$o3$g1$t1782542698$j58$l0$h0; airbridge_session__saramin=%7B%22id%22%3A%224ae92da8-8a5a-4825-be09-51176ad077ae%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1782541455375%2C%22end%22%3A1782542698804%7D; _ga_X6JZ0HCBFC=GS2.1.s1782541454$o46$g1$t1782542744$j60$l0$h0
host
www.saramin.co.kr
referer
https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword=%EB%A7%88%EC%BC%80%ED%84%B0
sec-ch-ua
"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"
sec-ch-ua-mobile
?0
sec-ch-ua-platform
"Windows"
sec-ch-ua-platform-version
"19.0.0"
sec-fetch-dest
document
sec-fetch-mode
navigate
sec-fetch-site
same-origin
sec-fetch-user
?1
upgrade-insecure-requests
1
user-agent
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36

3) Payload 정보
search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword=%EB%A7%88%EC%BC%80%ED%84%B0&recruitPage=2&recruitSort=relation&recruitPageCount=40&inner_com_type=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&show_applied=&quick_apply=&except_read=&ai_head_hunting=
4) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)

    <head>
        <meta charset="utf-8"/>
        <title>마케터 채용정보 | 총 22,772건의 검색결과 - 사람인</title>
        <meta name="naver-site-verification" content="86455485e27cab6986d130e4c3b90c5b516820d1">
        <meta name="naver" content="nosublinks">
        <meta http-equiv="Content-Language" content="ko-KR">
        <meta http-equiv="X-UA-Compatible" content="IE=Edge">
        <meta name="viewport" content="width=1280">
        <meta name="keywords" content="마케터, 취업, 구인, 구직, 아르바이트, 헤드헌팅, 알바, 자격증, 취업정보, 취업 정보, 취업뉴스, 취업 속보, 취업 뉴스, 취업상담실, 해외취업, 취업센터, 취업성공, 취업교육센터, 취업포털, 취업사이트, 채용, 채용포털, 채용정보, 고용정보, 알바, 일자리, 구인, 구인정보, 구직, 이력서, Work, Job, Career, cnldjq, rndls, rnwlr, dkfmqkdlxm, dkfqk, Recruit, 전직, 재취업, 여성취업, 정보통신취업, IT취업, 임원, CEO, 리쿠르트, 리크루트, 기업, 대기업, 중소기업, 벤처기업, 사람인, Saramin, tkfkadls, 인터넷 채용 시스템">
        <meta name="Description" content="마케터 검색결과 총22,772건 - 마케터에 대해 궁금하신가요? 관련 채용정보 22,772건을 사람인에서 확인해보세요!">
        <meta name="writer" content="사람인">
        <meta name="classification" content="GENERAL">
        <meta name="revisit" content="1 days">
        <meta name="distribution" content="GLOBAL">
        <meta property="og:title" content="마케터 채용정보 | 총 22,772건의 검색결과 - 사람인">
        <meta property="og:site_name" content="사람인">
        <meta property="og:type" content="website">
5) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장할 것