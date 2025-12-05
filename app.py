import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import numpy as np

# ===== 1. إعدادات الصفحة والتصميم الاحترافي (WIDE) =====
# استخدام التخطيط الواسع (wide layout) لزيادة مساحة العرض
st.set_page_config(layout="wide", page_title="أداة التحليل الاحترافي العامة للبيانات")

st.title("📊 لوحة القيادة الاحترافية: محلل البيانات العام")
st.markdown("---")

# ===== 2. الشريط الجانبي (تحميل الملف) =====
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
        st.success("🎉 لا توجد قيم مفقودة.")
    else:
        st.warning("⚠️ يوجد قيم مفقودة.")
        # تغيير اسم العمود من 'index' إلى 'Column Name' ليكون احترافياً
        missing_data = missing_data.rename(columns={'index': 'اسم العمود'})
        st.dataframe(missing_data[['اسم العمود', 'Missing Count', 'Missing Percentage']], use_container_width=True)

st.markdown("---")

# ===== 5. عرض الرسوم البيانية (Charts) حسب اختيار المستخدم =====
st.header(f"2. الرسوم البيانية الاحترافية: {analysis_type}")

# --- (A) تحليل متغيرين (Scatter Plot) ---
if analysis_type == 'تحليل متغيرين (Scatter Plot)':
    if len(numeric_cols) < 2:
        st.warning("🚫 يتطلب هذا التحليل عمودين رقميين على الأقل. يرجى مراجعة البيانات.")
    else:
        # فلاتر المحاور في الشريط الجانبي
        st.sidebar.markdown("---")
        st.sidebar.subheader("إعدادات Scatter Plot")
        col_x = st.sidebar.selectbox("2. المحور X:", options=numeric_cols)
        col_y = st.sidebar.selectbox("3. المحور Y:", options=numeric_cols)
        col_color = st.sidebar.selectbox("4. التلوين حسب (متغير نوعي):", options=['لا يوجد'] + object_cols)

        if col_x and col_y:
            color_param = col_color if col_color != 'لا يوجد' else None
            
            fig_scatter = px.scatter(
                df,
                x=col_x,
                y=col_y,
                color=color_param,
                title=f'**العلاقة بين {col_x} و {col_y}**',
                template='plotly_white',
                hover_data=df.columns.tolist() 
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("مخطط مبعثر تفاعلي يوضح العلاقة بين متغيرين رقميين.")
        else:
            pass # للحفاظ على الصياغة الصحيحة ومنع IndentationError

# --- (B) توزيع متغير واحد (Histogram) ---
elif analysis_type == 'توزيع متغير واحد (Histogram)':
    # فلتر اختيار العمود في الشريط الجانبي
    st.sidebar.markdown("---")
    st.sidebar.subheader("إعدادات Histogram")
    col_for_hist = st.sidebar.selectbox(
        "2. اختر العمود لتحليل توزيعه:",
        options=df.columns.tolist()
    )
    
    if col_for_hist:
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
        st.caption("مخطط التوزيع يوضح تكرار القيم والانحرافات (Outliers) إذا كان العمود رقميًا.")
    else:
        pass # للحفاظ على الصياغة الصحيحة ومنع IndentationError


# --- (C) مصفوفة الارتباط (Heatmap) ---
elif analysis_type == 'مصفوفة الارتباط (Heatmap)':
    if not numeric_cols:
        st.warning("🚫 لا توجد أعمدة رقمية لإجراء تحليل الارتباط.")
    else:
        st.subheader("مصفوفة الارتباط (Heatmap)")
        
        # استخدام دالة corr() مع إسقاط الصفوف التي تحتوي على قيم مفقودة مؤقتًا لضمان عمل الارتباط
        corr_matrix = df[numeric_cols].dropna().corr().round(2)
        
        if corr_matrix.empty:
            st.warning("تعذر حساب مصفوفة الارتباط. قد تكون البيانات المتبقية غير كافية.")
        else:
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='RdBu_r', 
                title='**مصفوفة الارتباط بين المتغيرات**',
                labels=dict(color="قيمة الارتباط"),
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            st.caption("خريطة حرارية احترافية توضح قوة العلاقة بين كل زوج من المتغيرات الرقمية.")
