from flask import Flask, render_template, request, jsonify
import pandas as pd
import re
from urllib.parse import unquote
import logging
import os
from flask import make_response

# 로깅 설정
app = Flask(__name__)

## csv, excel 파일 경로 설정 (vercel 디렉토리 구조로)
BASE_DIR = os.path.dirname(__file__)  # api/ 폴더의 절대경로
def load_csv(filename):
    return pd.read_csv(os.path.join(BASE_DIR, filename))
def load_excel(filename):
    return pd.read_excel(os.path.join(BASE_DIR, filename), engine='openpyxl')
# pd.read_csv -> load_csv 변경
# pd.read_csv -> load_excel 변경

# ============================================
# 1. 공통 유틸 – 은행 로고 경로 -----------------------------------
# ============================================
LOGO_DIR = "bank_logos"          # static/bank_logos/ 하위 폴더명

def _slug(bank_name: str) -> str:
    """공백‧괄호 제거 → 파일명 슬러그"""
    return re.sub(r"[\s()]+", "", str(bank_name))

def logo_filename(bank_name):
    filename = bank_logo_map.get(bank_name)
    return f"bank_logos/{filename}" if filename else "bank_logos/default.png"

# ✔ 예금/적금 데이터 로드
deposit_tier1 = load_csv('예금_1금융권_포함.csv')
deposit_tier2 = load_csv('예금_2금융권.csv')
savings_tier1 = load_csv('적금_1금융권_포함.csv')
savings_tier2 = load_csv('적금_2금융권.csv')

# ✔ 지역 컬럼 매핑 추가
def normalize_name(name):
    s = str(name)
    s = re.sub(r'[㈜\s\-()]', '', s)  # 괄호, 공백, 하이픈 제거
    s = s.replace('저축은행', '').replace('은행', '').lower()
    return s

region_map_raw = {
    # 1금융권
    '국민은행':'서울','신한은행':'서울','우리은행':'서울','하나은행':'서울','농협은행':'서울',
    'SC제일은행':'서울','씨티은행':'서울','카카오뱅크':'경기','케이뱅크':'서울','토스뱅크':'서울',
    '아이엠은행':'대구','부산은행':'부산','경남은행':'경남','광주은행':'광주','전북은행':'전북','제주은행':'제주',
    # 2금융권 저축은행
    'BNK저축은행':'부산','CK저축은행':'강원','DH저축은행':'부산','HB저축은행':'서울',
    'IBK저축은행':'서울','JT저축은행':'서울','JT친애저축은행':'서울','KB저축은행':'서울',
    'MS저축은행':'서울','OK저축은행':'서울','OSB저축은행':'서울','SBI저축은행':'서울',
    '고려저축은행':'부산','국제저축은행':'부산','금화저축은행':'경기','남양저축은행':'경기',
    '다올저축은행':'서울','대명상호저축은행':'대구','대백저축은행':'대구','대신저축은행':'부산',
    '대아상호저축은행':'부산','대원저축은행':'부산','대한저축은행':'서울','더블저축은행':'서울',
    '더케이저축은행':'서울','동양저축은행':'서울','동원제일저축은행':'부산','드림저축은행':'대구',
    '디비저축은행':'서울','라온저축은행':'대전','머스트삼일저축은행':'서울','모아저축은행':'인천',
    '민국저축은행':'경기','바로저축은행':'서울','부림저축은행':'부산','삼정저축은행':'부산',
    '삼호저축은행':'서울','상상인저축은행':'서울','상상인플러스저축은행':'서울','세람저축은행':'전북',
    '센트럴저축은행':'서울','솔브레인저축은행':'대전','스마트저축은행':'광주','스카이저축은행':'서울',
    '스타저축은행':'서울','신한저축은행':'서울','아산저축은행':'충남','안국저축은행':'서울',
    '안양저축은행':'경기','애큐온저축은행':'서울','에스앤티저축은행':'경남','엔에이치저축은행':'서울',
    '영진저축은행':'대구','예가람저축은행':'서울','오성저축은행':'경기','오투저축은행':'서울',
    '우리금융저축은행':'서울','우리저축은행':'서울','웰컴저축은행':'서울','유니온저축은행':'서울',
    '유안타저축은행':'서울','융창저축은행':'서울','인성저축은행':'부산','인천저축은행':'인천',
    '조은저축은행':'광주','조흥저축은행':'서울','진주저축은행':'경남','참저축은행':'대전',
    '청주저축은행':'충북','키움예스저축은행':'서울','키움저축은행':'서울','페퍼저축은행':'서울',
    '평택저축은행':'경기','푸른저축은행':'서울','하나저축은행':'서울','한국투자저축은행':'서울',
    '한성저축은행':'서울','한화저축은행':'서울','흥국저축은행':'서울'
}
region_map = {normalize_name(k): v for k, v in region_map_raw.items()}
# 로고 매핑 딕셔너리 생성
logo_df = load_csv('logo_bank.csv')
bank_logo_map = dict(zip(logo_df['은행명'], logo_df['로고파일명']))
print(logo_df)

# 예금/적금 데이터에 정제명, 지역, 로고 추가
for df in [deposit_tier1, deposit_tier2, savings_tier1, savings_tier2]:
    df['정제명'] = df['금융회사명'].apply(normalize_name)
    df['지역'] = df['정제명'].map(region_map).fillna('기타')
    df['logo'] = df['금융회사명'].apply(logo_filename)  # ✅ 로고 경로 추가

# 정제명 & 지역 컬럼 삽입
for df in [deposit_tier1, deposit_tier2, savings_tier1, savings_tier2]:
    df['정제명'] = df['금융회사명'].apply(normalize_name)
    df['지역'] = df['정제명'].map(region_map).fillna('기타')
    df["logo"]  = df["금융회사명"].apply(logo_filename)
def clean_loan_data(file):
    df = load_csv(file)
    df = df.rename(columns=lambda x: x.strip())
    df = df.rename(columns={
        '금리': '최저 금리(%)',
        '한도': '대출한도',
        '상환 방식': '상환 방식',  
        '가입 대상': '가입대상',
        '만기이자': '만기이자',
        '저축기간(개월)': '저축기간(개월)'
    })
    required = ['금융회사명', '상품명', '최저 금리(%)', '대출한도', '상환 방식', '가입대상', '저축기간(개월)', '만기이자']
    for c in required:
        if c not in df:
            df[c] = '정보 없음'
    df.dropna(subset=['금융회사명', '상품명'], inplace=True)
    df.fillna('정보 없음', inplace=True)
    return df


loan_files = ['새희망홀씨_정리완료.csv','소액_비상금대출_정리완료.csv','무직자대출_정리완료.csv','사잇돌_정리완료.csv','햇살론_정제완료_v3.csv']
loan_data = pd.concat([clean_loan_data(f) for f in loan_files], ignore_index=True)

def classify_loan_type(name):
    name = str(name).lower()
    name = re.sub(r'[^가-힣a-z0-9]', '', name)  # 괄호, 공백, 특수문자 제거

    if '햇살론_' in name :
        return '햇살론'
    elif '비상금' in name :
        return '비상금대출'
    elif '새희망홀씨' in name:
        return '새희망홀씨'
    elif '무직자' in name:
        return '무직자대출'
    elif '사잇돌' in name:
        return '사잇돌'
    elif '신용대출' in name:
        return '신용대출'
    else:
        if '햇살' in name:
            return '햇살론'
        return '기타'

loan_data['대출유형'] = loan_data['상품명'].apply(classify_loan_type)
loan_data["logo"] = loan_data["금융회사명"].apply(logo_filename)
# 지역 기본 필터 함수
def filter_products(df, period, bank, region):
    if period:
        df = df[df['저축기간(개월)'] == int(period)]
    if bank:
        keys = bank.split('|')
        df = df[df['금융회사명'].isin(keys)]
    if region:
        df = df[df['지역'] == region]
    return df

# ✔ 대출 라우트
@app.route('/loans')
def loans_page():
    selected_types = request.args.getlist('loanType')
    input_amount = request.args.get('amount', type=int)

    df = loan_data.copy()
    df['상품유형'] = df['상품명'].apply(classify_loan_type)
    # ✅ 로그 확인
    print("✔ 대출유형 분포:")
    print(df['상품유형'].value_counts())  # 햇살론, 기타 등 몇 개인지 찍힘
    logging.info(df['상품유형'].value_counts())
    # ✅ 금액이 있으면 계산금액 컬럼 추가
    if input_amount:
        def compute_total(row):
            try:
            # 🔧 금리 문자열에서 % 제거 및 공백 제거
                rate_str = str(row['최저 금리(%)']).replace('%', '').strip()
                rate = float(rate_str) / 100
                return int(input_amount * (1 + rate))
            except Exception as e:
                print("계산 오류:", e, "| 금리 값:", row['최저 금리(%)'])
                return None
        df['계산금액'] = df.apply(compute_total, axis=1)
    else:
        df['계산금액'] = None

    # ✅ 필터링
    if selected_types and '전체' not in selected_types:
        filtered_df = df[df['상품유형'].isin(selected_types)]
    else:
        filtered_df = df

    # ✅ 페이지네이션
    page = request.args.get('page', 1, type=int)
    page_size = 15
    start = (page - 1) * page_size
    end = start + page_size
    total_pages = (len(filtered_df) + page_size - 1) // page_size

    return render_template(
        'loans_list.html',
        products=filtered_df.iloc[start:end].to_dict('records'),
        selected_types=selected_types,
        input_amount=input_amount,
        current_page=page,
        total_pages=total_pages
    )



# ✔ 금융용어사전 로드 및 초성 기준
terms_df = load_excel('통계용어사전.xlsx')
def get_initial_consonant(word):
    if not word: return ''
    c = word[0]
    if '가' <= c <= '힣':
        cho=['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
        return cho[(ord(c)-ord('가'))//588]
    return 'A-Z' if re.match(r'[A-Za-z]', c) else c
terms_df['초성'] = terms_df['용어'].apply(get_initial_consonant)

car_df = load_csv('naver_car_prices.csv')

# 필터 유틸 함수
def filter_products(df, period, bank, region):
    if period:
        df = df[df['저축기간(개월)'] == int(period)]
    if bank:
        keys = bank.split('|')
        df = df[df['금융회사명'].isin(keys)]
    if region:
        df = df[df['지역'] == region]
    return df

# ✔ 홈
@app.route('/')
def home():
    return render_template('home_menu.html')

# ✔ 예금 라우트
@app.route('/deposits')
def deposits_page():
    periods = sorted(pd.concat([deposit_tier1, deposit_tier2])['저축기간(개월)'].unique())
    banks = {
        '1금융권': sorted(deposit_tier1['금융회사명'].unique()),
        '2금융권': sorted(deposit_tier2['금융회사명'].unique())
    }
    regions = sorted(pd.concat([deposit_tier1, deposit_tier2])['지역'].unique())
    return render_template('filter_page.html', product_type='예금', product_type_url='deposits', periods=periods, banks=banks, regions=regions)

@app.route('/deposits/detail/<bank>/<product_name>')
def deposits_detail(bank, product_name):
    bank = unquote(bank)
    product_name = unquote(product_name)

    df = pd.concat([deposit_tier1, deposit_tier2])
    matched = df[(df['상품명'] == product_name) & (df['금융회사명'] == bank)]

    if matched.empty:
        return "상품을 찾을 수 없습니다.", 404

    prod = matched.iloc[0]
    return render_template('product_detail.html', product=prod, product_type='예금', product_type_url='deposits')

@app.route('/api/deposits')
def api_deposits():
    period = request.args.get('period')
    bank = request.args.get('bank')
    region = request.args.get('region')

    data = pd.concat([deposit_tier1, deposit_tier2], ignore_index=True)
    filtered = filter_products(data, period, bank, region)

    # ✅ 중복 제거: 상품명 + 금융회사명 기준
    filtered = filtered.drop_duplicates(subset=['상품명', '금융회사명'])

    products = filtered.sort_values(by='최고우대금리(%)', ascending=False).to_dict('records')
    return jsonify({'products': products, 'total': len(products)})

# ✔ 적금 라우트
@app.route('/savings')
def savings_page():
    periods = sorted(pd.concat([savings_tier1, savings_tier2])['저축기간(개월)'].unique())
    banks = {
        '1금융권': sorted(savings_tier1['금융회사명'].unique()),
        '2금융권': sorted(savings_tier2['금융회사명'].unique())
    }
    regions = sorted(pd.concat([savings_tier1, savings_tier2])['지역'].unique())
    return render_template('filter_page.html', product_type='적금', product_type_url='savings', periods=periods, banks=banks, regions=regions)

@app.route('/savings/detail/<bank>/<product_name>')
def savings_detail(bank, product_name):
    bank = unquote(bank)
    product_name = unquote(product_name)

    df = pd.concat([savings_tier1, savings_tier2])
    matched = df[(df['상품명'] == product_name) & (df['금융회사명'] == bank)]

    if matched.empty:
        return "상품을 찾을 수 없습니다.", 404

    prod = matched.iloc[0]
    return render_template('product_detail.html', product=prod, product_type='적금', product_type_url='savings')

@app.route('/api/savings')
def api_savings():
    period = request.args.get('period')
    bank = request.args.get('bank')
    region = request.args.get('region')

    print("🔍 적금 요청 - 기간:", period, "| 은행:", bank, "| 지역:", region)

    data = pd.concat([savings_tier1, savings_tier2], ignore_index=True)
    print("전체 적금 상품 수:", len(data))

    filtered = filter_products(data, period, bank, region)
    print("필터 후 적금 수:", len(filtered))

    filtered = filtered.drop_duplicates(subset=['상품명', '금융회사명'])

    # ✅ NaN 처리 필수!
    filtered = filtered.fillna("정보 없음")

    products = filtered.sort_values(by='최고우대금리(%)', ascending=False).to_dict('records')
    return jsonify({'products': products, 'total': len(products)})


@app.route('/loans/detail/<product_name>')
def loans_detail(product_name):
    prod = loan_data[loan_data['상품명'] == product_name].iloc[0]
    return render_template('product_detail.html', product=prod, product_type='대출', product_type_url='loans')

@app.route('/api/product_detail/<product_type>/<product_key>')
def api_product_detail(product_type, product_key):
    product_key = unquote(product_key)
    product_name, bank_name = product_key.split('--')

    # 데이터프레임 선택
    if product_type == 'deposits':
        df = pd.concat([deposit_tier1, deposit_tier2])
    elif product_type == 'savings':
        df = pd.concat([savings_tier1, savings_tier2])
    elif product_type == 'loans':
        df = loan_data
    else:
        return "잘못된 product_type입니다.", 400

    # 상품 검색
    matched = df[(df['상품명'] == product_name) & (df['금융회사명'] == bank_name)]
    if matched.empty:
        return "상품을 찾을 수 없습니다.", 404

    product = matched.iloc[0]
    return render_template('product_modal.html', product=product, product_type=product_type)

@app.route('/savings/page/<int:page>')
def savings_page_list(page):
    page_size = 15
    df = pd.concat([savings_tier1, savings_tier2], ignore_index=True)
    total_products = len(df)
    total_pages = (total_products + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size

    page_products = df.iloc[start:end].to_dict('records')
    return render_template(
        'products_list.html',
        product_type='적금',
        product_type_url='savings',
        products=page_products,
        current_page=page,
        total_pages=total_pages
    )

@app.route('/deposits/page/<int:page>')
def deposits_page_list(page):
    page_size = 15
    df = pd.concat([deposit_tier1, deposit_tier2], ignore_index=True)
    total_products = len(df)
    total_pages = (total_products + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size

    page_products = df.iloc[start:end].to_dict('records')
    return render_template(
        'products_list.html',
        product_type='예금',
        product_type_url='deposits',
        products=page_products,
        current_page=page,
        total_pages=total_pages
    )


# ✔ 모아플러스 홈
@app.route('/plus')
def plus_home(): return render_template('plus_home.html')

# ✔ 모아플러스 - 금융사전
@app.route('/plus/terms')
def terms_home():
    query = request.args.get('query', '').strip()
    initial = request.args.get('initial', '').strip()
    selected = request.args.get('selected', '').strip()
    page = int(request.args.get('page', 1))

    if query:
        filtered = terms_df[terms_df['용어'].str.contains(query)]
        category = f"검색결과: {query}"
    elif initial:
        filtered = terms_df[terms_df['초성'] == initial]
        category = initial
    else:
        filtered = terms_df.copy()
        category = "전체"

    filtered = filtered[['용어', '설명']].sort_values('용어')
    terms = filtered.to_dict('records')

    # 페이징 처리
    page_size = 15
    total_pages = (len(terms) + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size

    selected_term = None
    if selected:
        selected_term = next((t for t in terms if t['용어'] == selected), None)

    return render_template(
        'terms_home.html',
        categories=sorted(terms_df['초성'].unique()),
        terms=terms,
        category=category,
        query=query,
        selected=selected,
        selected_term=selected_term,
        current_page=page,
        total_pages=total_pages,
        start=start,
        end=end
    )
@app.route('/plus/youth')
def plus_youth_policy(): return render_template('youth_policy.html')

@app.route('/plus/calculator')
def plus_calculator(): return render_template('calculator_home.html')

@app.route('/plus/region-data')
def region_data():
    region = request.args.get('region')
    region = region.replace("특별시", "").replace("광역시", "").replace("도", "").strip()

    # CSV 컬럼명: '시도', '가격'
    house_df = load_csv('주택_시도별_보증금.csv')
    avg_prices = house_df.groupby('시도')['가격'].mean().round(1).to_dict()
    price = avg_prices.get(region, '정보없음')

    # 적금 추천
    savings = pd.concat([savings_tier1, savings_tier2])
    top_savings = savings[savings['지역'] == region].sort_values(by='최고우대금리(%)', ascending=False).head(5)
    products = top_savings[['상품명', '금융회사명', '최고우대금리(%)']].to_dict('records')

    return jsonify({'price': price, 'products': products})

@app.template_filter('extract_rate')
def extract_rate(val):
    if isinstance(val, str):
        m = re.search(r'[\d.]+', val)
        return m.group(0) if m else '0'
    return str(val)

# ✔ car-roadmap 라우트에 적금 가입 가능 기간도 추가
@app.route('/plus/car-roadmap')
def car_roadmap():
    # 평균가 계산
    grouped = car_df.groupby(['차종', '모델명'])['평균가'].mean().round(0).astype(int).reset_index()

    # 이미지 매핑 딕셔너리
    image_map = {
        '레이': 'ray.png',
        '캐스퍼': 'kester.png',
        '모닝': 'moring.png',
        '기아 K3': 'kia_k3.png',
        '현대 아반떼': 'avante.png',
        '현대 쏘나타': 'sonata.png',
        '르노코리아 XM3': 'renault_xm3.png',
        '현대 코나': 'kona.png',
        '기아 셀토스': 'seltos.png',
    }

    # car_list 구성
    car_list = []
    for _, row in grouped.iterrows():
        name = row['모델명']
        car_list.append({
            '카테고리': row['차종'],
            '모델명': name,
            '평균가격': row['평균가'],
            '이미지파일명': image_map.get(name, 'default.png')
        })

    savings_df = pd.concat([savings_tier1, savings_tier2], ignore_index=True)
    savings_df = savings_df.dropna(subset=['상품명', '금융회사명', '최고우대금리(%)', '저축기간(개월)'])
    savings_df['금리'] = savings_df['최고우대금리(%)'].astype(float)
    savings_df['기간'] = savings_df['저축기간(개월)'].astype(int)
    savings_products = savings_df[['상품명', '금융회사명', '금리', '기간']].drop_duplicates().to_dict('records')
    period_options = sorted(savings_df['기간'].unique().tolist())

    return render_template('car_roadmap.html',
                           car_list=car_list,
                           savings_products=savings_products,
                           period_options=period_options)


@app.route('/plus/region')
def plus_region_map():
    return render_template('region_map.html')

@app.route('/plus/travel', methods=['GET'])
def travel_home():
    travel_df = load_csv('travel.csv')
    cities = travel_df['도시'].tolist()
    return render_template('travel_select.html', cities=cities)

@app.route('/plus/travel-plan', methods=['GET', 'POST'])
def travel_plan():
    travel_df = load_csv("travel.csv")
    cities = travel_df['도시'].tolist()

    if request.method == 'POST':
        selected_city = request.form['city']
        months = int(request.form['months'])

        # 선택된 도시의 정보 필터링
        info = travel_df[travel_df['도시'] == selected_city].iloc[0]

        total_cost = int(info['총예상경비'])
        monthly_saving = total_cost // months

        travel_plan = {
            'city': selected_city,
            'country': info['국가'],
            'theme': info['테마'],
            'reason': info['추천이유'],
            'days': info['추천일정'],
            'airfare': int(info['예상항공료']),
            'accommodation': int(info['숙박비']),
            'food': int(info['식비']),
            'total': total_cost,
            'monthly': monthly_saving
        }

        selected_months = months

        # 추천 적금 상품: 기간 일치 + 금리 높은 순으로 상위 5개
        savings_df = pd.concat([savings_tier1, savings_tier2], ignore_index=True)
        recommended_products = savings_df[savings_df['저축기간(개월)'] == months] \
            .sort_values(by='최고우대금리(%)', ascending=False) \
            .drop_duplicates(subset=['상품명', '금융회사명']) \
            .head(5).to_dict('records')
        
        return render_template('travel_result.html',
                city=travel_plan['city'],
                country=travel_plan['country'],
                theme=travel_plan['theme'],
                reason=travel_plan['reason'],
                days=travel_plan['days'],
                airfare=travel_plan['airfare'],
                accommodation=travel_plan['accommodation'],
                food=travel_plan['food'],
                total_cost=travel_plan['total'],
                months=selected_months,
                monthly_saving=travel_plan['monthly'],
                products=recommended_products
            )

    # GET 요청일 때는 도시 리스트만 넘겨서 폼 렌더링
    return render_template('travel_select.html', cities=cities)

@app.route('/plus/compare', methods=['GET', 'POST'])
def compare_savings():
    if request.method == 'POST':
        product_type = request.form.get('product_type', 'savings')
        df = pd.concat(
            [deposit_tier1, deposit_tier2] if product_type == 'deposits' else [savings_tier1, savings_tier2],
            ignore_index=True
        )

        bank1 = request.form.get('bank1', '').strip()
        product1 = request.form.get('product1', '').strip()
        bank2 = request.form.get('bank2', '').strip()
        product2 = request.form.get('product2', '').strip()
        amount_raw = request.form.get('amount', '').strip()
        months_raw = request.form.get('months', '').strip()

        if not amount_raw.isdigit() or not months_raw.isdigit():
            return "금액 또는 저축 기간이 숫자로 입력되지 않았습니다.", 400

        amount = int(amount_raw)
        months = int(months_raw)

        try:
            item1 = df[(df['금융회사명'] == bank1) & (df['상품명'] == product1)].iloc[0]
            item2 = df[(df['금융회사명'] == bank2) & (df['상품명'] == product2)].iloc[0]
        except IndexError:
            return "선택한 상품 정보를 찾을 수 없습니다.", 404

        def calc_total(item):
            try:
                rate = float(item['최고우대금리(%)']) / 100
            except:
                rate = 0.0
            before_tax = amount * months + amount * (months + 1) / 2 * rate / 12
            tax = before_tax * 0.154
            after_tax = before_tax - tax
            return {
                '상품명': item['상품명'],
                '금융회사명': item['금융회사명'],
                '금리': item['최고우대금리(%)'],
                '세전이자': round(before_tax - amount * months),
                '이자과세': round(tax),
                '세후이자': round(after_tax - amount * months),
                '실수령액': round(after_tax),
                'logo': item.get('logo', 'bank_logos/default.png')
            }

        result1 = calc_total(item1)
        result2 = calc_total(item2)
        gap = abs(result1['실수령액'] - result2['실수령액'])
        better = result1['금융회사명'] if result1['실수령액'] > result2['실수령액'] else result2['금융회사명']

        grouped = df.groupby('금융회사명')['상품명'].unique().apply(list).to_dict()
        bank_list = sorted(df['금융회사명'].unique())  # ✅ 추가

        return render_template(
            'compare_form.html',
            product_map=grouped,
            result1=result1,
            result2=result2,
            gap=gap,
            better=better,
            selected_type=product_type,
            bank_list=bank_list  # ✅ 추가
        )

    # GET 요청 처리
    selected_type = request.args.get('type', 'savings')
    df = pd.concat(
        [deposit_tier1, deposit_tier2] if selected_type == 'deposits' else [savings_tier1, savings_tier2],
        ignore_index=True
    )
    grouped = df.groupby('금융회사명')['상품명'].unique().apply(list).to_dict()
    bank_list = sorted(df['금융회사명'].unique())  # ✅ 추가

    return render_template(
        'compare_form.html',
        product_map=grouped,
        result1=None,
        result2=None,
        gap=None,
        better=None,
        selected_type=selected_type,
        bank_list=bank_list  # ✅ 추가
    )


@app.template_filter('format_currency')
def format_currency(value, symbol='₩'):
    try:
        return f"{symbol}{int(value):,}"
    except:
        return value


# 상품을 모아 페이지
@app.route('/plus/roadmap')
def roadmap():
    return render_template('plus_roadmap.html')

# 가이드 모아 페이지
@app.route('/guide')
def guide_moa():
    return render_template('guide_moa.html')

# 대출 설문 페이지
@app.route('/loan/survey')
def loan_survey():
    return render_template('loan_survey.html')


@app.route("/loan/recommend", methods=["POST"])
def loan_recommend():
    purpose = request.form.get("purpose")
    income = request.form.get("income")
    credit = request.form.get("credit")

    recommendations = []

    # 조건별 추천 로직
    if income == "정규직":
        if credit in ["1~4등급", "5~6등급"]:
            recommendations.append("새희망홀씨 대출")
        if credit in ["5~6등급", "7등급이하"]:
            recommendations.append("햇살론")
        if credit in ["1~4등급", "5~6등급"]:
            recommendations.append("사잇돌 대출")

    elif income == "자영업자":
        if credit in ["5~6등급", "7등급이하"]:
            recommendations.append("햇살론")
        if credit in ["1~4등급", "5~6등급"]:
            recommendations.append("사잇돌 대출")

    elif income == "무직":
        if credit in ["1~4등급", "5~6등급"]:
            recommendations.append("소액 비상금 대출")
            recommendations.append("무직자 대출")

    return render_template("loan_result.html", recommendations=recommendations)

