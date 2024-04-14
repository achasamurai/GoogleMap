import requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

st.title("施設選びお助けアプリ")
st.markdown("""#### 概要：  
GoogleMap上での評価や口コミ数,価格を指定することで,あなたのニーズにマッチした最大20件の施設を選ぶことができます.""")

st.markdown("""### 1 地点""")
plc=st.text_input("以下に入力してください.ex)札幌駅",value="")

url =f"""https://maps.googleapis.com/maps/api/geocode/json?address={plc}&language=ja&region=jp&key=AIzaSyAM1yTGD0EKlXX5QGtKll_e9F8-JrJlyZE"""
payload={}
headers={}
response = requests.request("GET", url, headers=headers, data=payload)
results=response.json()["results"]
for result in results:
    lat=float(result["geometry"]["location"]["lat"])
    lng=float(result["geometry"]["location"]["lng"])
    lat='{:.013f}'.format(lat)
    lng='{:.013f}'.format(lng)

#半径を指定する場合
st.markdown("""### 2 範囲or最寄り""")
option1 = st.selectbox("以下から1つ選択してください.「指定の範囲内から検索する」を選択した場合は,人通りの多い場所が優先的に選ばれます．", ("指定の範囲内から検索する","地点から最寄りの20件を検索する"),index=0)
##施設の種類
facility_type={
    "飲食店":"restaurant",
    "カフェ":"cafe",
    "お店":"store",
    "バー":"bar",
    "パン屋":"bakery",
    "酒屋":"liquor_store"
}
if option1=="指定の範囲内から検索する":
    rmax=st.number_input("範囲を指定してください.(最大5000m、半角数字のみ)",min_value=0, max_value=5000, value=1000, step=1000)
    st.markdown("""### 3 施設の種類""")
    ty=st.selectbox("以下から一つ選んでください",list(facility_type.keys()))
    typ=facility_type[ty]
    ##　キーワードの入力
    st.markdown("""### 4 キーワード""")
    kyw=st.text_input("入力してください.ex)ラーメン",value="")
    url =f"""https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat}%2C{lng}&language=ja&radius={rmax}&type={typ}&keyword={kyw}&key=AIzaSyAM1yTGD0EKlXX5QGtKll_e9F8-JrJlyZE"""
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    results=response.json()["results"]
    facilities_info=[]
    for result in results:
            facility_info={}
            facility_info["緯度"]=result["geometry"]["location"]["lat"]
            facility_info["経度"]=result["geometry"]["location"]["lng"]
            facility_info["名前"]=result["name"]
            try:
                facility_info["営業中"]=result['opening_hours']["open_now"]
            except:
                facility_info["営業中"]=None
            try:
                facility_info["価格"]=result["price_level"]
            except:
                facility_info["価格"]=None
    
            facility_info["評価"]=result["rating"]
            facility_info["口コミ数"]=result["user_ratings_total"]
            facility_info["id"]=result["place_id"]
            facilities_info.append(facility_info)
           
    df_info=pd.DataFrame(facilities_info)

#最寄りの20件を取得する場合
else:
    st.markdown("""### 3 施設の種類""")
    ty=st.selectbox("以下から一つ選んでください",list(facility_type.keys()))
    typ=facility_type[ty]
    ##　キーワードの入力
    st.markdown("""### 4 キーワード""")
    kyw=st.text_input("入力してください.ex)味噌ラーメン",value="")

    url =f"""https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat}%2C{lng}&language=ja&rankby=distance&type={typ}&keyword={kyw}&key=AIzaSyAM1yTGD0EKlXX5QGtKll_e9F8-JrJlyZE"""
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    results=response.json()["results"]
    facilities_info=[]
    for result in results:
            facility_info={}
            facility_info["緯度"]=result["geometry"]["location"]["lat"]
            facility_info["経度"]=result["geometry"]["location"]["lng"]
            facility_info["名前"]=result["name"]
            try:
                facility_info["営業中"]=result['opening_hours']["open_now"]
            except:
                facility_info["営業中"]=None
            try:
                facility_info["価格"]=result["price_level"]
            except:
                facility_info["価格"]=None
    
            facility_info["評価"]=result.get("rating", 0)
            facility_info["口コミ数"]=result.get("user_ratings_total" , 0)
            facility_info["id"]=result["place_id"]
            facilities_info.append(facility_info)
           
    df_info=pd.DataFrame(facilities_info)

#df_infoから営業中，口コミ数，評価，価格の条件を満たすものを抽出
##営業中
st.markdown("""#### 5.1 営業中か否か""")
option2 = st.selectbox("以下の3つから1つ選択してください",("営業中の施設のみを表示する","どちらも表示する"),index=1)
if option2=="どちらも表示する":
    pass
elif option2=="営業中の施設のみを表示する":
    df_info1=pd.DataFrame()
    df_info2=pd.DataFrame()
    df_info1=df_info[df_info["営業中"]==None]
    df_info2=df_info[df_info["営業中"]==True]
    df_info=pd.concat([df_info1,df_info2])
else:
    df_info1=pd.DataFrame()
    df_info2=pd.DataFrame()
    df_info1=df_info[df_info["営業中"]==None]
    df_info2=df_info[df_info["営業中"]==False]
    df_info=pd.concat([df_info1,df_info2])
##評価
st.markdown("""#### 5.2 評価""")
xmin=st.number_input("評価の下限を0から4で指定してください.(0.1刻み)",min_value=0.0, max_value=4.0, value=3.0, step=0.1)
df_info=df_info[df_info["評価"]>=xmin]

##口コミ数
st.markdown("""#### 5.3 口コミ数""")
ymin=st.number_input("口コミ数の下限を指定してください.(100刻み)",min_value=0,value=0,step=100)
df_info=df_info[df_info["口コミ数"]>=ymin]

##価格
st.markdown("""#### 5.4 価格""")
st.markdown("""
0：無料\\
1：安価\\
2：普通\\
3：高価\\
4：とても高価""")

zmax=st.number_input("価格の上限を0から4で指定してください.ex)3を選んだ場合は,価格が0から3の施設が表示されます.",min_value=0, max_value=4, value=4, step=1)

df_info3=pd.DataFrame()
df_info4=pd.DataFrame()
df_info5=pd.DataFrame()
df_info3=df_info[df_info["価格"]==None]
df_info4=df_info[df_info["価格"]!=None]
df_info5=df_info4[df_info4["価格"]<=zmax]
df_info=pd.concat([df_info3,df_info5])

##idからurlを取得する
df_info["url"]=""
lis1=[]
for item in df_info["id"]:
    id=item
    url = f"""https://maps.googleapis.com/maps/api/place/details/json?place_id={id}&fields=url&key=AIzaSyAM1yTGD0EKlXX5QGtKll_e9F8-JrJlyZE"""
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    url=response.json()["result"]["url"]
    lis1.append(url)
df_info["url"]=lis1

st.write("検索を開始しますか？")
if st.button("開始"):
    st.markdown("""### 検索結果""")
    #画面に表示する用のデータフレームを作る
    st.markdown("""##### データ""")
    df_display=df_info.copy()
    df_display["営業中"]=df_display["営業中"].replace(True,"Open").replace(False,"Close")
    df_display["価格"]=df.display["価格"].replace(0,"無料").replace(1,"安価").replace(2,"普通").replace(3,"高価").replace(4,"とても高価")
    df_display=df_display[["名前","営業中","価格","評価","口コミ数"]].sort_values("評価",ascending=False).reset_index(drop=True)
    st.write("上から評価順になっています．また，<NA>は不明なことを示しています．")
    st.dataframe(df_display)


    #url
    st.markdown("""##### GoogleMapに移動する""")
    for item,name in zip(df_info["url"],df_info["名前"]):
        link = f"""[{name}]({item})"""
        st.markdown(link, unsafe_allow_html=True)

    st.markdown("""##### 地図""")
    ##条件に合う店をマッピングする
    m = folium.Map(location=[lat,lng], zoom_start=13)
    folium.Marker(location=[lat, lng],popup="中心地").add_to(m)#ピン
    try:
        folium.Circle(radius=rmax,location=[lat, lng],popup="検索範囲",color="blue",fill=True,fill_opacity=0.07).add_to(m)
    except:
        pass  
    for name,lat,lng in zip(df_info["名前"],df_info["緯度"],df_info["経度"]):
        folium.Marker(location=[lat, lng],popup=name,icon=folium.Icon(color="red",icon="eye-open")).add_to(m)
    folium_static(m)  
