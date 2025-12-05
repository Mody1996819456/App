import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import numpy as np

# ===== 1. إعدادات الصفحة والتصميم الاحترافي =====
# استخدام التخطيط الواسع (wide layout) لزيادة مساحة العرض
st.set_page_config(layout="wide", page_title="أداة التحليل الاحترافي العامة للبيانات")

st.title("📊 لوحة القيادة الاحترافية: محلل البيانات العام")
st.markdown("---")

# ===== 2. الشريط الجانبي (الفلاتر الرئيسية) =====
st.sidebar.header("تحميل وفلاتر التحليل")

uploaded_file = st.sidebar.file_uploader(
    "يرجى تحميل ملف بيانات (CSV أو Excel):",
    type=['csv', 'xlsx']
)

if uploaded_file is None:
    st.info("يرجى تحميل ملف للبدء. ستظهر فلاتر التحليل في الشريط الجانبي بعد التحميل.")
    st.stop()

# قراءة ومعالجة الملف
try:
    if uploaded_file.name.endswith('.csv'):
        # قراءة CSV مع افتراض الترميز UTF-8
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    elif uploaded_file.name.endswith('.xlsx'):
        # استخدام BytesIO للتعامل مع ملفات Excel بشكل أفضل
        df = pd.read_excel(BytesIO(uploaded_file.getvalue()))
    
    st.sidebar.success("✅ تم تحميل الملف بنجاح!")

except Exception as e:
    st.error(f"❌ حدث خطأ أثناء قراءة الملف. يرجى التأكد من التنسيق والترميز: {e}")
    st.stop()

# تحديد أنواع الأعمدة بعد التحميل
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
object_cols = df.select_dtypes(include='object').columns.tolist()

# ===== 3. فلاتر التحليل الديناميكية (في الشريط الجانبي) =====

st.sidebar.markdown("---")
st.sidebar.header("🛠️ خيارات ومحاور الرسوم البيانية")

# الفلتر الرئيسي لاختيار نوع الرسم البياني
analysis_type = st.sidebar.selectbox(
    "1. اختر نوع الرسم البياني:",
    ['تحليل متغيرين (Scatter Plot)', 'توزيع متغير واحد (Histogram)', 'مصفوفة الارتباط (Heatmap)']
)

# ===== 4. عرض ملخص البيانات (الواجهة الرئيسية) =====
st.header("1. ملخص و جودة البيانات")

tab1, tab2, tab3 = st.tabs(["البيانات الخام", "ملخص الأعمدة", "القيم المفقودة"])

with tab1:
    st.dataframe(df.head(), use_container_width=True)
    st.caption(f"عدد الصفوف الكلي: {len(df)} | عدد الأعمدة: {len(df.columns)}")

with tab2:
    # الحل الآمن لـ df.info() لمنع TypeError
    non_null_count = df.count()
    missing_percentage = (df.isnull().sum() / len(df)) * 100
    summary_df = pd.DataFrame({
        'نوع البيانات (dtype)': df.dtypes,
        'القيم غير المفقودة': non_null_count,
        'نسبة المفقود (%)': missing_percentage.round(2)
    })
    st.dataframe(summary_df, use_container_width=True)
    st.caption("ملخص يوضح نوع البيانات وعدد القيم المتوفرة في كل عمود.")

with tab3:
    missing_data = df.isnull().sum().reset_index(name='Missing Count')
    missing_data['Missing Percentage'] = (missing_data['Missing Count'] / len(df)) * 100
    missing_data = missing_data[missing_data['Missing Count'] > 0].sort_values(by='Missing Percentage', ascending=False)
    if missing_data.empty:
        st.success("🎉 لا توجد قيم مفق
