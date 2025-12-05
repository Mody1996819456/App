import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import numpy as np

# 1. إعدادات الصفحة (WIDE Layout)
st.set_page_config(layout="wide", page_title="أداة التحليل الاحترافي للبيانات")

st.title("🔬 أداة التحليل الاحترافي العام للبيانات")
st.markdown("---")

# ===== الشريط الجانبي (للتنظيم) =====
st.sidebar.header("تحميل وتصفية البيانات")

# 2. تحميل الملف
uploaded_file = st.sidebar.file_uploader(
    "يرجى تحميل ملف بيانات (CSV أو Excel):",
    type=['csv', 'xlsx']
)

if uploaded_file is None:
    st.info("يرجى تحميل ملف للبدء بالتحليل. استخدم الشريط الجانبي.")
    st.stop()

# قراءة ومعالجة الملف
try:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(BytesIO(uploaded_file.getvalue()))
    
    st.sidebar.success("✅ تم تحميل الملف بنجاح!")

except Exception as e:
    st.error(f"❌ حدث خطأ أثناء قراءة الملف. يرجى التأكد من التنسيق: {e}")
    st.stop()

# 3. تحديد أنواع الأعمدة
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
object_cols = df.select_dtypes(include='object').columns.tolist()

# 4. واجهة استعراض البيانات وجودتها (في الواجهة الرئيسية)
st.header("1. استعراض وجودة البيانات")

tab1, tab2, tab3 = st.tabs(["البيانات الخام (نظرة أولية)", "نظرة عامة على الأعمدة", "القيم المفقودة"])

with tab1:
    st.dataframe(df.head(), use_container_width=True)
    st.caption(f"عدد الصفوف: {len(df)} | عدد الأعمدة: {len(df.columns)}")

with tab2:
    buffer = BytesIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue().decode('utf-8'))

with tab3:
    # تحليل نسبة القيم المفقودة
    missing_data = df.isnull().sum().reset_index(name='Missing Count')
    missing_data['Missing Percentage'] = (missing_data['Missing Count'] / len(df)) * 100
    missing_data = missing_data[missing_data['Missing Count'] > 0].sort_values(by='Missing Percentage', ascending=False)
    
    if missing_data.empty:
        st.success("🎉 لا توجد قيم مفقودة في البيانات.")
    else:
        st.warning("⚠️ يوجد قيم مفقودة. يرجى الانتباه عند التحليل.")
        st.dataframe(missing_data, use_container_width=True)

st.markdown("---")

# 5. أدوات التحليل الاحترافي (في الشريط الجانبي)
st.sidebar.header("🛠️ خيارات التحليل")

# أداة اختيار نوع التحليل
analysis_type = st.sidebar.selectbox(
    "اختر نوع الرسم البياني (Visualization):",
    ['تحليل متغيرين (Scatter Plot)', 'توزيع متغير واحد (Histogram)', 'مصفوفة الارتباط (Heatmap)']
)

# 6. قسم عرض الرسوم البيانية (الواجهة الرئيسية)
st.header(f"2. عرض التحليل: {analysis_type}")

# --- التحليل الأول: تحليل متغيرين (Scatter Plot) ---
if analysis_type == 'تحليل متغيرين (Scatter Plot)':
    if len(numeric_cols) < 2:
        st.warning("🚫 يتطلب هذا التحليل عمودين رقميين على الأقل. يرجى مراجعة البيانات.")
    else:
        # اختيار الأعمدة
        col_x = st.sidebar.selectbox("المحور X (المتغير المستقل):", options=numeric_cols)
        col_y = st.sidebar.selectbox("المحور Y (المتغير التابع):", options=numeric_cols)
        col_color = st.sidebar.selectbox("التلوين حسب (متغير نوعي اختياري):", options=['لا يوجد'] + object_cols)

        if col_x and col_y:
            color_param = col_color if col_color != 'لا يوجد' else None
            
            # إنشاء الرسم البياني
            fig_scatter = px.scatter(
                df,
                x=col_x,
                y=col_y,
                color=color_param,
                title=f'**العلاقة بين {col_x} و {col_y}**',
                template='plotly_white' # تحسين المظهر
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("يُظهر هذا الرسم البياني العلاقة (Correlation) بين متغيرين.")

# --- التحليل الثاني: توزيع متغير واحد (Histogram) ---
elif analysis_type == 'توزيع متغير واحد (Histogram)':
    col_for_hist = st.sidebar.selectbox(
        "اختر العمود لتحليل توزيعه:",
        options=df.columns.tolist()
    )
    
    if col_for_hist:
        # إضافة Box Plot للمقارنة وتحليل الاحترافية
        marginal_type = 'box' if col_for_hist in numeric_cols else None
        
        fig_hist = px.histogram(
            df,
            x=col_for_hist,
            marginal=marginal_type,
            color=col_for_hist if col_for_hist in object_cols else None,
            title=f'**توزيع القيم للعمود: {col_for_hist}**',
            template='plotly_white'
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption("يُظهر هذا الرسم البياني تكرار القيم. إذا كان العمود رقميًا، فسيظهر معه مخطط الصندوق والشارب (Box Plot) لتحليل الانحرافات.")

# --- التحليل الثالث: مصفوفة الارتباط (Heatmap) ---
elif analysis_type == 'مصفوفة الارتباط (Heatmap)':
    if not numeric_cols:
        st.warning("🚫 لا توجد أعمدة رقمية لإجراء تحليل الارتباط.")
    else:
        st.subheader("مصفوفة الارتباط (Heatmap) بين المتغيرات الرقمية")
        
        # استخدام دالة corr() مع إسقاط القيم المفقودة مؤقتًا
        corr_matrix = df[numeric_cols].dropna().corr().round(2)
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r', # مقياس احترافي للألوان (أحمر/أزرق)
            title='**مصفوفة الارتباط بين المتغيرات**',
            labels=dict(color="قيمة الارتباط")
        )
        st.plotly_chart(fig_corr, use_container_width=True)

