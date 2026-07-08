1.해당 데이터를 보여주는 주소
https://www.saramin.co.kr/zf_user/jobs/list/job-category?page=2&cat_kewd=1429&search_optional_item=n&search_done=y&panel_count=y&preview=y&isAjaxRequest=0&page_count=50&sort=RL&type=job-category&is_param=1&isSearchResultEmpty=1&isSectionHome=0&searchParamCount=1#searchTitle

2.실제 데이터를 가져오는 정보
한페이지가 성공적으로 수집되는지 확인하고 sqlitedb파일로 저장하고 JSON데이터는 별도의 컬럼으로 저장할 것
* 한페이지가 성공적으로 수집되었다면, 1~10페이지까지 수집하고 수집이 잘 되었는지 확인하고 결과 리포트를 보여줄 것
* 해당 정보를 수집하는 목적은 기업명, 채용공고 세부내용, 채용조건 등 채용공고 주요 데이터를 모두 수집하는 것입니다.

3. 채용공고 목록이 수집이 되었다면 채용공고 상세페이지 정보를 수집할 것. 상세페이지는 별도의 테이블로 구성할 것
추후 채용공고와 상세페이지를 조인해서 채용공고 정보를 분석할 것
* 수집 요청을 보낼때는 0.1~1초씩 쉬었다가 수집하게 할 것 네트워크 부담을 줄일 것

4. 데이터베이스에 저장할 때는 중복데이터가 발생하지 않도록 기존데이터가 있다면 업데이트 하는 방법으로 수집할 것

1) HTTP 
Request URL
https://www.saramin.co.kr/zf_user/jobs/list/job-category?page=2&cat_kewd=1429&search_optional_item=n&search_done=y&panel_count=y&preview=y&isAjaxRequest=0&page_count=50&sort=RL&type=job-category&is_param=1&isSearchResultEmpty=1&isSectionHome=0&searchParamCount=1
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
Sat, 04 Jul 2026 04:35:15 GMT
expires
Thu, 19 Nov 1981 08:52:00 GMT
link
</js/libs/require-2.3.2.min.js>; rel=preload; as=script; nopush, </js/search-panel/Main.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/Common.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/Util.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/EventBinding.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/Preview.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/Template.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/DepthAbstract.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/AutoComplete.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/TabStyleAbstract.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/SearchHistory.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/main/JobCategory.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/main/Area.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/main/Keyword.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Career.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Education.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/RecentlySearch.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Salary.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Age.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Gender.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Subway.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/WorkType.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/License.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Major.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/JobGrade.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Preference.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Industry.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/CompanyType.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/JobType.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/WorkDay.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/Welfare.js?ts=20260702112921>; rel=preload; as=script; nopush, </js/search-panel/components/option/ExceptKeyword.js?ts=20260702112921>; rel=preload; as=script; nopush
pragma
no-cache
server
SWS
set-cookie
RSRVID=web20|akiNh|akiL/; path=/
transfer-encoding
chunked
accept
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
accept-encoding
gzip, deflate, br, zstd
accept-language
ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7
connection
keep-alive
cookie
PCID=17554864216358143340984; ab180ClientId=b80ec89c-e9c2-4efe-9cf0-419b3dcc53f7; Mtype=P; saramin_last_login_provider=naver; _ga_DBVYV88LS9csn=VDJ5REsrWGFJVmdnY2RoeTB2YkMvZz09=GS2.1.s1768233669$o1$g0$t1768233669$j60$l0$h0; airbridge_user__saramin=%7B%22externalUserID%22%3A%2213720210%22%2C%22alias%22%3A%7B%22amplitude_id%22%3A%2213720210%22%7D%7D; saramin_login_tab_default=p; AMP_a687efd08d=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJDYVV5bWRudkcyYmpNTzdrYjNtSnJ6JTIyJTJDJTIydXNlcklkJTIyJTNBJTIyMTM3MjAyMTAlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzc2Njg2NDE0MzYyJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc3NjY4NjQxNDM2NCUyQyUyMmxhc3RFdmVudElkJTIyJTNBNCUyQyUyMnBhZ2VDb3VudGVyJTIyJTNBMCU3RA==; HideEditConditionTooltip=y; _ga_DBVYV88LS9=GS2.1.s1777689639$o7$g1$t1777689665$j34$l0$h0; _gcl_au=1.1.92811635.1782541455; airbridge_migration_metadata__saramin=%7B%22version%22%3A%221.11.12%22%7D; ab.storage.deviceId.a2ac6b71-3416-464a-ac48-ef2cff5c2026=%7B%22g%22%3A%227370b821-d22d-fe39-302a-7f224487414d%22%2C%22c%22%3A1755486553296%2C%22l%22%3A1782547407555%7D; ab.storage.userId.a2ac6b71-3416-464a-ac48-ef2cff5c2026=%7B%22g%22%3A%2213720210%22%2C%22c%22%3A1761491761236%2C%22l%22%3A1782547407555%7D; _ga_X6JZ0HCBFC=deleted; amp_a687ef=QHmcO52-IXKquDl3xqLIFi.MTM3MjAyMTA=..1js41lon1.1js42pft4.q.6n.7h; ab.storage.sessionId.a2ac6b71-3416-464a-ac48-ef2cff5c2026=%7B%22g%22%3A%223b71dc5e-6e9c-07e5-8375-b33d5cca5163%22%2C%22e%22%3A1782550378308%2C%22c%22%3A1782547407554%2C%22l%22%3A1782548578308%7D; PHPSESSID=mnknml43oiue78r128bd6pedi98auqsdrfhu1263qq67n16jua; _gid=GA1.3.1404274534.1783139323; _ga_E0LMXXGRZK=GS2.1.s1783139328$o6$g1$t1783139350$j38$l0$h0; _ga_58W0W855T7=GS2.1.s1783139323$o36$g1$t1783139452$j58$l0$h0; _ga=GA1.1.1716532447.1755486523; cto_bundle=kqg1HV9mUUFGbGdoUkxPdGF0SiUyRlA5elpvb2ZvUmZpOTI4SnRVbnA4RlN1V2lrOSUyQk5SMUt3bTJnY1NFQkFxZENRNUVMY3d2dmU1SXFLdUhidm4xNElaZ0plV0puUDFGQ3lwQjZnR2ZZMnolMkZOMHlwWmgyckhvVEdrSDFRUDA0V0lJVVlXaWl1NzUwZ05hJTJGNndOckxkU3VFV0E5USUzRCUzRA; airbridge_session__saramin=%7B%22id%22%3A%22d9467212-84a9-4cd9-9b3c-45e2fc31a02e%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1783139323693%2C%22end%22%3A1783139555225%7D; RSRVID=web20|akiM6|akiL/; _ga_GR2XRGQ0FK=GS2.1.s1783139323$o53$g1$t1783139564$j60$l0$h0; _ga_L2PN791WR5=GS2.1.s1783139351$o34$g1$t1783139564$j60$l0$h0; _ga_0PN5NFZW7P=GS2.1.s1783139554$o34$g0$t1783139564$j50$l0$h0; _ga_X6JZ0HCBFC=GS2.1.s1783139323$o2$g1$t1783139714$j60$l0$h0; _gali=default_list_wrap
host
www.saramin.co.kr
referer
https://www.saramin.co.kr/zf_user/jobs/list/job-category?cat_kewd=1429&panel_type=&search_optional_item=n&search_done=y&panel_count=y&preview=y
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
page=2&cat_kewd=1429&search_optional_item=n&search_done=y&panel_count=y&preview=y&isAjaxRequest=0&page_count=50&sort=RL&type=job-category&is_param=1&isSearchResultEmpty=1&isSectionHome=0&searchParamCount=1

4) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)
              외                    
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="col recruit_info">
                                                    <ul>
                                                        <li>
                                                            <p class="work_place">서울 용산구</p>
                                                        </li>
                                                        <li>
                                                            <p class="career">경력 1년↑ · 계약직</p>
                                                        </li>
                                                        <li>
                                                            <p class="education">학력무관</p>
                                                        </li>
                                                    </ul>
                                                </div>
                                                <div class="col support_info">
                                                    <button class="sri_btn_md" title="클릭하면 입사지원할 수 있는 창이 뜹니다." onclick="try{quickApplyForm(&#39;54190979&#39;,&#39;&#39;,&#39;t_category=jobcategory_recruit&t_content=general&#39;, &#39;&#39;); return false;} catch (e) {}; return false;" onmousedown="try{n_trackEvent(&#39;apply&#39;,&#39;list&#39;,&#39;quick_apply&#39;);}catch(e){}">
                                                        <span class="sri_btn_immediately">입사지원</span>
                                                    </button>
                                                    <p class="support_detail">
                                                        <span class="date">~07.16(목)</span>
                                                        <span class="deadlines">17일 전 등록</span>
                                                    </p>
                                                </div>
                                            </div>
                                            <div class="similar_recruit"></div>
                                        </div>
                                        <div id="rec-54281518" class="list_item">
                                            <div class="box_item">
                                                <div class="col company_nm">
                                                    <span class="str_tit">앨리스몽드</span>
                                                    <button type="button" csn="THhnTEhBUjNvOWJ0TlF3czlLNDZwdz09" title="관심기업 등록" del_fl="n" aria-pressed="false" class="interested_corp" onclick="try{Saramin.btnJob(&#39;favor&#39;, this, &#39;&#39;, &#39;list&#39;);}catch(e){}" first_nudge="off">
                                                        <span>관심기업 등록</span>
                                                    </button>
                                                </div>
                                                <div class="col notification_info">
                                                    <div class="job_tit">
                                                        <a class="str_tit " id="rec_link_54281518" onclick="s_trackApply(this, &#39;jobcategory_recruit&#39;, &#39;general&#39;);" title="앨리스몽드 본점  웨딩디렉터를 모집합니다." href="/zf_user/jobs/relay/view?view_type=list&amp;rec_idx=54281518" target="_blank" onmousedown="">
                                                            <span>앨리스몽드 본점  웨딩디렉터를 모집합니다.</span>
                                                        </a>
                                                        <button type="button" onclick="Saramin.btnJob('scrap',this,'','list');" title="스크랩" scraped="n" rec_idx="54281518" imgType="button" class="spr_scrap btn_scrap scrap-54281518 off">
                                                            <span class="blind">스크랩</span>
                                                        </button>
                                                    </div>
                                                    <div class="job_meta">
                                                        <span class="job_sector">
                                                            <span>웨딩플래너</span>
                                                            <span>파티플래너</span>
                                                            <span>마케팅기획</span>
                                                            <span>행사기획</span>
                                                            <span>콘텐츠기획</span>
                                                            외                    
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="col recruit_info">
                                                    <ul>
                                                        <li>
                                                            <p class="work_place">서울 용산구</p>
                                                        </li>
                                                        <li>
                                                            <p class="career">신입 · 경력 · 정규직</p>
                                                        </li>
                                                        <li>
                                                            <p class="education">고졸↑</p>
                                                        </li>
                                                    </ul>
                                                </div>
                                                <div class="col support_info">
                                                    <button class="sri_btn_md" title="클릭하면 입사지원할 수 있는 창이 뜹니다." onclick="try{quickApplyForm(&#39;54281518&#39;,&#39;&#39;,&#39;t_category=jobcategory_recruit&t_content=general&#39;, &#39;&#39;); return false;} catch (e) {}; return false;" onmousedown="try{n_trackEvent(&#39;apply&#39;,&#39;list&#39;,&#39;quick_apply&#39;);}catch(e){}">
                                                        <span class="sri_btn_immediately">입사지원</span>
                                                    </button>
                                                    <p class="support_detail">
                                                        <span class="date">~07.25(토)</span>
                                                        <span class="deadlines">8일 전 등록</span>
                                                    </p>
                                                </div>
                                            </div>
                                            <div class="similar_recruit"></div>
                                        </div>
                                        <div id="rec-54277919" class="list_item">
                                            <div class="box_item">
                                                <div class="col company_nm">
                                                    <a href="/zf_user/company-info/view-inner-recruit?csn=dnYvd0ttdmZaWm9QQXhZMTVkMTkyUT09" class="str_tit" target="_blank">(주)하늘을담다                        </a>
                                                    <button type="button" csn="dnYvd0ttdmZaWm9QQXhZMTVkMTkyUT09" title="관심기업 등록" del_fl="n" aria-pressed="false" class="interested_corp" onclick="try{Saramin.btnJob(&#39;favor&#39;, this, &#39;&#39;, &#39;list&#39;);}catch(e){}" first_nudge="off">
                                                        <span>관심기업 등록</span>
                                                    </button>
                                                    <span class="info_stock" title="대기업">대기업</span>
                                                </div>
                                                <div class="col notification_info">
                                                    <div class="job_tit">
                                                        <a class="str_tit " id="rec_link_54277919" onclick="s_trackApply(this, &#39;jobcategory_recruit&#39;, &#39;general&#39;);" title="[카카오그룹/뷰티브랜드] 마케터 경력직 채용" href="/zf_user/jobs/relay/view?view_type=list&amp;rec_idx=54277919" target="_blank" onmousedown="">
                                                            <span>[카카오그룹/뷰티브랜드] 마케터 경력직 채용</span>
                                                        </a>
                                                        <button type="button" onclick="Saramin.btnJob('scrap',this,'','list');" title="스크랩" scraped="n" rec_idx="54277919" imgType="button" class="spr_scrap btn_scrap scrap-54277919 off">
                                                            <span class="blind">스크랩</span>
                                                        </button>
                                                    </div>
                                                    <div class="job_meta">
                                                        <span class="job_sector">
                                                            <span>마케팅기획</span>
                                                            <span>마케팅전략</span>
                                                            <span>인플루언서마케팅</span>
                                                            <span>SNS마케팅</span>
                                                            <span>콘텐츠기획</span>
                                                            외                    
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="col recruit_info">
                                                    <ul>
                                                        <li>
                                                            <p class="work_place">서울 용산구 외</p>
                                                        </li>
                                                        <li>
                                                            <p class="career">경력 2년↑ · 정규직</p>
                                                        </li>
                                                        <li>
                                                            <p class="education">대학(2,3년)↑</p>
                                                        </li>
                                                    </ul>
                                                </div>
                                                <div class="col support_info">
                                                    <button class="sri_btn_md" title="클릭하면 입사지원할 수 있는 창이 뜹니다." onclick="try{quickApplyForm(&#39;54277919&#39;,&#39;&#39;,&#39;t_category=jobcategory_recruit&t_content=general&#39;, &#39;&#39;); return false;} catch (e) {}; return false;" onmousedown="try{n_trackEvent(&#39;apply&#39;,&#39;list&#39;,&#39;quick_apply&#39;);}catch(e){}">
                                                        <span class="sri_btn_immediately">입사지원</span>
                                                    </button>
                                                    <p class="support_detail">
                                                        <span class="date">~07.27(월)</span>
                                                        <span class="deadlines">9일 전 등록</span>
                                                    </p>
                                                </div>
                                            </div>
                                            <div class="similar_recruit"></div>
                                        </div>
                                        <div id="rec-54273351" class="list_item">
                                            <div class="box_item">
                                                <div class="col company_nm">
                                                    <a href="/zf_user/company-info/view-inner-recruit?csn=bHhrQWdRSVlQT1FET1RIWjVabGxtZz09" class="str_tit" target="_blank">사조푸디스트(주)                        </a>
                                                    <button type="button" csn="bHhrQWdRSVlQT1FET1RIWjVabGxtZz09" title="관심기업 등록" del_fl="n" aria-pressed="false" class="interested_corp" onclick="try{Saramin.btnJob(&#39;favor&#39;, this, &#39;&#39;, &#39;list&#39;);}catch(e){}" first_nudge="off">
                                                        <span>관심기업 등록</span>
                                                    </button>
                                                    <span class="main_corp" title="사조그룹">사조그룹</span>
                                                </div>
                                                <div class="col notification_info">
                                                    <div class="job_tit">
                                                        <a class="str_tit " id="rec_link_54273351" onclick="s_trackApply(this, &#39;jobcategory_recruit&#39;, &#39;general&#39;);" title="[사조푸디스트(주)/서울역] 홍보 PR담당 부서장 경력사원 모집" href="/zf_user/jobs/relay/view?view_type=list&amp;rec_idx=54273351" target="_blank" onmousedown="">
                                                            <span>[사조푸디스트(주)/서울역] 홍보 PR담당 부서장 경력사원 모집</span>
                                                        </a>
                                                        <button type="button" onclick="Saramin.btnJob('scrap',this,'','list');" title="스크랩" scraped="n" rec_idx="54273351" imgType="button" class="spr_scrap btn_scrap scrap-54273351 off">
                                                            <span class="blind">스크랩</span>
                                                        </button>
                                                    </div>
                                                    <div class="job_meta">
                                                        <span class="job_sector">
                                                            <span>마케팅기획</span>
                                                            <span>마케팅전략</span>
                                                            <span>광고마케팅</span>
                                                            <span>기업홍보</span>
                                                            <span>디지털마케팅</span>
                                                            외                    
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="col recruit_info">
                                                    <ul>
                                                        <li>
                                                            <p class="work_place">서울 용산구</p>
                                                        </li>
                                                        <li>
                                                            <p class="career">경력무관 · 정규직</p>
                                                        </li>
                                                        <li>
                                                            <p class="education">학력무관</p>
                                                        </li>
                                                    </ul>
                                                </div>
                                                <div class="col support_info">
                                                    <button class="sri_btn_md" title="클릭하면 입사지원할 수 있는 창이 뜹니다." onclick="try{quickApplyForm(&#39;54273351&#39;,&#39;&#39;,&#39;t_category=jobcategory_recruit&t_content=general&#39;, &#39;&#39;); return false;} catch (e) {}; return false;" onmousedown="try{n_trackEvent(&#39;apply&#39;,&#39;list&#39;,&#39;quick_apply&#39;);}catch(e){}">
                                                        <span class="sri_btn_immediately">입사지원</span>
                                                    </button>
                                                    <p class="support_detail">
                                                        <span class="date">D-3</span>
                                                        <span class="deadlines">9일 전 등록</span>
                                                    </p>
                                                </div>
                                            </div>
                                            <div class="similar_recruit"></div>
                                        </div>
                                        <div id="rec-54268931" class="list_item">
                                            <div class="box_item">
                                                <div class="col company_nm">
                                                    <a href="/zf_user/company-info/view-inner-recruit?csn=cjBaQUNDVEg4YUw1cGkraWdJUVJXQT09" class="str_tit" target="_blank">(주)에이치피오                        </a>
                                                    <button type="button" csn="cjBaQUNDVEg4YUw1cGkraWdJUVJXQT09" title="관심기업 등록" del_fl="n" aria-pressed="false" class="interested_corp" onclick="try{Saramin.btnJob(&#39;favor&#39;, this, &#39;&#39;, &#39;list&#39;);}catch(e){}" first_nudge="off">
                                                        <span>관심기업 등록</span>
                                                    </button>
                                                    <span class="main_corp" title="에이치피오그룹">에이치피오그룹</span>
                                                    <span class="info_stock" title="코스닥">코스닥</span>
                                                </div>
                                                <div class="col notification_info">
                                                    <div class="job_tit">
                                                        <a class="str_tit " id="rec_link_54268931" onclick="s_trackApply(this, &#39;jobcategory_recruit&#39;, &#39;general&#39;);" title="[덴프스 Denps] 브랜드 마케터 채용" href="/zf_user/jobs/relay/view?view_type=list&amp;rec_idx=54268931" target="_blank" onmousedown="">
                                                            <span>[덴프스 Denps] 브랜드 마케터 채용</span>
                                                        </a>
                                                        <button type="button" onclick="Saramin.btnJob('scrap',this,'','list');" title="스크랩" scraped="n" rec_idx="54268931" imgType="button" class="spr_scrap btn_scrap scrap-54268931 off">
                                                            <span class="blind">스크랩</span>
                                                        </button>
                                                    </div>
                                                    <div class="job_meta">
                                                        <span class="job_sector">
                                                            <span>브랜드마케팅</span>
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="col recruit_info">
                                                    <ul>
                                                        <li>
                                                            <p class="work_place">서울 용산구</p>
                                                        </li>
                                                        <li>
                                                            <p class="career">경력 7년↑ · 정규직</p>
                                                        </li>
                                                        <li>
                                                            <p class="education">대학(2,3년)↑</p>
                                                        </li>
                                                    </ul>
                                                </div>
                                                <div class="col support_info">
                                                    <button class="sri_btn_md" title="클릭하면 입사지원할 수 있는 창이 뜹니다." onclick="try{quickApplyForm(&#39;54268931&#39;,&#39;&#39;,&#39;t_category=jobcategory_recruit&t_content=general&#39;, &#39;&#39;); return false;} catch (e) {}; return false;" onmousedown="try{n_trackEvent(&#39;apply&#39;,&#39;list&#39;,&#39;quick_apply&#39;);}catch(e){}">
                                                        <span class="sri_btn_immediately">입사지원</span>
                                                    </button>
                                                    <p class="support_detail">
                                                        <span class="date">~07.24(금)</span>
                                                        <span class="deadlines">10일 전 등록</span>
                                                    </p>
                                                </div>
                                            </div>
                                            <div class="similar_recruit"></div>
                                        </div>
                                        <div id="rec-54234868" class="list_item">
                                            <div class="box_item">
                                                <div class="col company_nm">
                                                    <a href="/zf_user/company-info/view-inner-recruit?csn=V0M5dmtiRDdvUll5Z0RsdE9LaDI4QT09" class="str_tit" target="_blank">(주)광고생각                        </a>
                                                    <button type="button" csn="V0M5dmtiRDdvUll5Z0RsdE9LaDI4QT09" title="관심기업 등록" del_fl="n" aria-pressed="false" class="interested_corp" onclick="try{Saramin.btnJob(&#39;favor&#39;, this, &#39;&#39;, &#39;list&#39;);}catch(e){}" first_nudge="off">
                                                        <span>관심기업 등록</span>
                                                    </button>
                                                </div>
                                                <div class="col notification_info">
                                                    <div class="job_tit">
                                                        <a class="str_tit " id="rec_link_54234868" onclick="s_trackApply(this, &#39;jobcategory_recruit&#39;, &#39;general&#39;);" title="[주말/공휴일 출근필수] 가구 업종 바이럴 콘텐츠 마케터 구인" href="/zf_user/jobs/relay/view?view_type=list&amp;rec_idx=54234868" target="_blank" onmousedown="">
                                                            <span>[주말/공휴일 출근필수] 가구 업종 바이럴 콘텐츠 마케터 구인</span>
                                                        </a>
                                                        <button type="button" onclick="Saramin.btnJob('scrap',this,'','list');" title="스크랩" scraped="n" rec_idx="54234868" imgType="button" class="spr_scrap btn_scrap scrap-54234868 off">
                                                            <span class="blind">스크랩</span>
                                                        </button>
                                                    </div>
                                                    <div class="job_meta">
                                                        <span class="job_sector">
                                                            <span>가구</span>
                                                            <span>SNS</span>
                                                            <span>인플루언서</span>
                                                            <span>마케팅기획</span>
                                                            <span>마케팅전략</span>
                                                            외                    
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="col recruit_info">
                                                    <ul>
                                                        <li>
                                                            <p class="work_place">서울 강남구 외</p>
                                                        </li>
                                                        <li>
                                                            <p class="career">신입 · 경력 · 정규직</p>
                                                        </li>
                                                        <li>
                                                            <p class="education">고졸↑</p>
                                                        </li>
                                                    </ul>
                                                </div>
                                                <div class="col support_info">
                                                    <button class="sri_btn_md" title="클릭하면 입사지원할 수 있는 창이 뜹니다." onclick="try{quickApplyForm(&#39;54234868&#39;,&#39;&#39;,&#39;t_category=jobcategory_recruit&t_content=general&#39;, &#39;&#39;); return false;} catch (e) {}; return false;" onmousedown="try{n_trackEvent(&#39;apply&#39;,&#39;list&#39;,&#39;quick_apply&#39;);}catch(e){}">
                                                        <span class="sri_btn_immediately">입사지원</span>
                                                    </button>
                                                    <p class="support_detail">
                                                        <span class="date">~07.20(월)</span>
                                                        <span class="deadlines">14일 전 등록</span>
                                                    </p>
                                                </div>
                                            </div>
                                            <div class="similar_recruit"></div>
                                        </div>
                                        <div id="rec-54254163" class="list_item">
                                            <div class="box_item">
                                                <div class="col company_nm">
                                                    <a href="/zf_user/company-info/view-inner-recruit?csn=aGk2dzEyL042Z0lwNkhncDVPVUkxQT09" class="str_tit" target="_blank">(주)와이낫애드컴퍼니                        </a>
                                                    <button type="button" csn="aGk2dzEyL042Z0lwNkhncDVPVUkxQT09" title="관심기업 등록" del_fl="n" aria-pressed="false" class="interested_corp" onclick="try{Saramin.btnJob(&#39;favor&#39;, this, &#39;&#39;, &#39;list&#39;);}catch(e){}" first_nudge="off">
                                                        <span>관심기업 등록</span>
                                                    </button>
                                                </div>
                                                <div class="col notification_info">
                                                    <div class="job_tit">
                                                        <a class="str_tit " id="rec_link_54254163" onclick="s_trackApply(this, &#39;jobcategory_recruit&#39;, &#39;general&#39;);" title="[WHYNOT] 커머셜 숏폼 크리에이터 (촬영·편집)" href="/zf_user/jobs/relay/view?view_type=list&amp;rec_idx=54254163" target="_blank" onmousedown="">
                                                            <span>[WHYNOT] 커머셜 숏폼 크리에이터 (촬영·편집)</span>
                                                        </a>
                                                        <button type="button" onclick="Saramin.btnJob('scrap',this,'','list');" title="스크랩" scraped="n" rec_idx="54254163" imgType="button" class="spr_scrap btn_scrap scrap-54254163 off">
                                                            <span class="blind">스크랩</span>
                                                        </button>
                                                    </div>
                                                    <div class="job_meta">
                                                        <span class="job_sector">
                                                            <span>촬영감독</span>
                                                            <span>PD/AD/FD</span>
                                                            <span>촬영</span>
                                                            <span>콘텐츠기획</span>
                                                            <span>광고PD</span>
                                                            외                    
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="col recruit_info">
                                                    <ul>
                                                        <li>
                                                            <p class="work_place">서울 용산구</p>
                                                        </li>
                                                        <li>
                                                            <p class="career">경력 2년↑ · 정규직</p>
                                                        </li>
                                                        <li>
                                                            <p class="education">학력무관</p>
                                                        </li>
                                                    </ul>
                                                </div>
                                                <div class="col support_info">
                                                    <button class="sri_btn_md" title="클릭하면 입사지원할 수 있는 창이 뜹니다." onclick="try{quickApplyForm(&#39;54254163&#39;,&#39;&#39;,&#39;t_category=jobcategory_recruit&t_content=general&#39;, &#39;&#39;); return false;} catch (e) {}; return false;" onmousedown="try{n_trackEvent(&#39;apply&#39;,&#39;list&#39;,&#39;quick_apply&#39;);}catch(e){}">
                                                        <span class="sri_btn_immediately">입사지원</span>
                                                    </button>
                                                    <p class="support_detail">
                                                        <span class="date">~08.22(토)</span>
                                                        <span class="deadlines">11일 전 등록</span>
                                                    </p>
                                                </div>

5) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장할 것