"""
Streamlit 대시보드 메인 앱 진입점입니다.
Streamlit Secrets 및 .env 파일로부터 네이버 API 인증 키를 우선 로드하여 공통 세션 상태를 활성화하고,
대시보드 메인 화면 및 사이드바 가이드를 구성합니다.
"""

import os
import streamlit as st

# .env 파일 로드 (로컬 환경용, python-dotenv 패키지 미설치 시 예외 방지)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 페이지 설정
st.set_page_config(
    page_title="네이버 API 통합 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    # 1. Streamlit Secrets 우선 조회, 없으면 환경변수(.env) 조회
    env_client_id = ""
    env_client_secret = ""
    
    try:
        if "NAVER_CLIENT_ID" in st.secrets:
            env_client_id = st.secrets["NAVER_CLIENT_ID"].strip()
        if "NAVER_CLIENT_SECRET" in st.secrets:
            env_client_secret = st.secrets["NAVER_CLIENT_SECRET"].strip()
    except Exception:
        pass

    # st.secrets에 값이 없으면 환경 변수(.env)에서 로드 시도
    if not env_client_id:
        env_client_id = os.environ.get("NAVER_CLIENT_ID", "").strip()
    if not env_client_secret:
        env_client_secret = os.environ.get("NAVER_CLIENT_SECRET", "").strip()
    
    # 세션 상태 초기화 및 연동
    if "client_id" not in st.session_state:
        st.session_state["client_id"] = env_client_id
    if "client_secret" not in st.session_state:
        st.session_state["client_secret"] = env_client_secret

    # 현재 실시간 환경변수/설정 변경사항 반영을 위해 세션이 비어있으면 값 할당
    if not st.session_state["client_id"] and env_client_id:
        st.session_state["client_id"] = env_client_id
    if not st.session_state["client_secret"] and env_client_secret:
        st.session_state["client_secret"] = env_client_secret

    st.title("📊 네이버 API 통합 분석 대시보드")
    
    # 사이드바 UI 구성
    st.sidebar.header("🔑 API 인증 설정")
    
    is_authenticated = bool(st.session_state["client_id"] and st.session_state["client_secret"])
    
    if is_authenticated:
        st.sidebar.success("✅ 네이버 API 인증 완료")
        
        # 환경변수/Secrets 기반 로드인지 확인
        if (st.session_state["client_id"] == env_client_id and 
                st.session_state["client_secret"] == env_client_secret):
            
            # secrets 우선 검증
            has_secrets = False
            try:
                if "NAVER_CLIENT_ID" in st.secrets and st.session_state["client_id"] == st.secrets["NAVER_CLIENT_ID"]:
                    has_secrets = True
            except Exception:
                pass
                
            if has_secrets:
                st.sidebar.info("💡 Streamlit Secrets 설정을 자동으로 로드했습니다.")
            else:
                st.sidebar.info("💡 `.env` 파일로부터 API 키를 자동으로 로드했습니다.")
        else:
            st.sidebar.info("💡 사용자가 직접 입력한 임시 키를 적용했습니다.")
            
        # 마스킹하여 키 정보 일부 노출
        masked_id = st.session_state["client_id"][:4] + "*" * (len(st.session_state["client_id"]) - 4) if len(st.session_state["client_id"]) > 4 else "****"
        st.sidebar.text(f"연동 ID: {masked_id}")
        
        # 원할 경우 재설정할 수 있는 리셋 버튼 제공
        if st.sidebar.button("인증 키 정보 초기화"):
            st.session_state["client_id"] = ""
            st.session_state["client_secret"] = ""
            st.sidebar.warning("인증 정보가 초기화되었습니다. 다시 로드하거나 입력해 주세요.")
            st.rerun()
    else:
        st.sidebar.error("❌ API 인증 필요")
        st.sidebar.warning(
            "배포 환경의 Streamlit Secrets 설정이나 로컬의 `.env` 파일에 `NAVER_CLIENT_ID`와 `NAVER_CLIENT_SECRET`을 설정해 주세요."
        )
        
        # 수동/임시 입력 폼 제공
        st.sidebar.markdown("---")
        st.sidebar.subheader("임시 인증 키 입력")
        temp_id = st.sidebar.text_input("Client ID", type="password", key="input_client_id")
        temp_secret = st.sidebar.text_input("Client Secret", type="password", key="input_client_secret")
        
        if st.sidebar.button("임시 인증 적용"):
            if temp_id and temp_secret:
                st.session_state["client_id"] = temp_id.strip()
                st.session_state["client_secret"] = temp_secret.strip()
                st.sidebar.success("임시 인증이 적용되었습니다!")
                st.rerun()
            else:
                st.sidebar.error("Client ID와 Secret을 모두 입력해 주세요.")
                
    # 메인 컨텐츠 영역
    st.markdown("""
    이 대시보드는 네이버 오픈 API를 활용하여 다양한 데이터를 조회하고 시각적으로 분석하는 도구입니다.
    왼쪽 사이드바에서 API 인증 상태를 확인하고, 서브 페이지를 통해 각 분석 기능을 이용해 보세요.
    """)
    
    # 인증 상태에 따른 메인 가이드 표시
    if is_authenticated:
        st.info("🎉 API 인증이 성공적으로 완료되었습니다! 왼쪽 메뉴에서 분석 도구를 선택하여 시작하세요.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### 제공 기능 안내
            - 📈 **검색어 트렌드** (DataLab API)
            - 🛍️ **쇼핑 검색** (최신 상품 및 최저/최고가 분석)
            - 📝 **블로그 검색** (포스팅 수집 및 분석)
            """)
        with col2:
            st.markdown("""
            - ☕ **카페 검색** (카페글 동향 분석)
            - 📰 **뉴스 검색** (뉴스 수집 및 관련도 분석)
            """)
    else:
        st.warning("""
        ### ⚠️ 분석 서비스를 이용하시려면 API 인증이 필요합니다.
        
        **[인증 설정 방법 (배포 환경)]**
        - Streamlit Community Cloud의 **App Settings > Secrets** 메뉴에 아래 설정을 입력해 주세요:
          ```toml
          NAVER_CLIENT_ID = "여러분의_Client_ID"
          NAVER_CLIENT_SECRET = "여러분의_Client_Secret"
          ```
        
        **[인증 설정 방법 (로컬 환경)]**
        1. 프로젝트 루트 폴더에서 `.env` 파일을 엽니다.
        2. `NAVER_CLIENT_ID`와 `NAVER_CLIENT_SECRET` 값을 기입합니다.
           ```env
           NAVER_CLIENT_ID=여러분의_Client_ID
           NAVER_CLIENT_SECRET=여러분의_Client_Secret
           ```
        3. 저장한 뒤, 브라우저 화면을 새로고침 하거나 왼쪽 사이드바에서 임시 인증 정보를 입력해 주세요.
        """)

if __name__ == "__main__":
    main()
