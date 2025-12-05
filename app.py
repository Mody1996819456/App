import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# =============================================================================
# إعدادات الصفحة الأساسية
# =============================================================================

st.set_page_config(
    page_title="نظام الإدارة المتكامل والتحليل الاحترافي",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# دوال المساعدة للوحدات المختلفة
# =============================================================================

@st.cache_data
def load_employee_data():
    """تحميل بيانات الموظفين الوهمية (لأغراض العرض)."""
    data = {
        'EmployeeID': range(101, 150),
        'Department': np.random.choice(['Sales', 'Marketing', 'Tech', 'Finance', 'HR'], 49),
        'Age': np.random.randint(22, 58, 49),
        'Tenure_Years': np.random.randint(1, 18, 49),
        'Monthly_Salary': np.random.randint(6000, 25000, 49),
        'Performance_Rating': np.random.randint(1, 6, 49),
        'Is_Active': np.random.choice([True, False], 49, p=[0.85, 0.15])
    }
    df = pd.DataFrame(data)
    # إضافة مقياس مخاطر وهمي للتنبؤ الأولي
    df['Turnover_Risk_Score'] = (6 - df['Performance_Rating']) * (1 / df['Tenure_Years'])
    return df

def analyze_general_data(df):
    """منطق التحليل الاحترافي العام لأي ملف يتم تحميله."""
    
    st.header("1. استعراض وجودة البيانات 🔍")
    
    tab1, tab2 = st.tabs(["البيانات الخام والأنواع", "القيم المفقودة"])

    with tab1:
        st.dataframe(df.head())
        st.caption(f"عدد الصفوف: {len(df)} | عدد الأعمدة: {len(df.columns)}")
        st.subheader("أنواع بيانات الأعمدة:")
        buffer = BytesIO()
        df.info(buf=buffer)
        st.text(buffer.getvalue().decode('utf-8'))

    with tab2:
        missing_data = df.isnull().sum().reset_index(name='Missing Count')
        missing_data['Missing Percentage'] = (missing_data['Missing Count'] / len(df)) * 100
        missing_data = missing_data[missing_data['Missing Count'] > 0].sort_values(by='Missing Percentage', ascending=False)
        
        if missing_data.empty:
            st.success("🎉 لا توجد قيم مفقودة في هذا الملف. جودة بيانات ممتازة!")
        else:
            st.warning("⚠️ تم العثور على قيم مفقودة في الأعمدة التالية:")
            st.dataframe(missing_data, use_container_width=True)

    # --- أدوات التحليل الاحترافي ---
    st.header("2. أدوات التحليل الاحترافي التفاعلية 📈")
    
    # تحديد الأعمدة لأنواع مختلفة
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    object_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    all_cols = df.columns.tolist()

    analysis_type = st.selectbox(
        "اختر نوع التحليل المراد عرضه:",
        ['مصفوفة الارتباط (Heatmap)', 'تحليل التوزيع (Histogram/Box Plot)', 'تحليل العلاقة (Scatter Plot)']
    )

    if analysis_type == 'مصفوفة الارتباط (Heatmap)':
        if not numeric_cols:
            st.warning("لا توجد بيانات رقمية كافية في الملف لإجراء تحليل الارتباط.")
        else:
            selected_corr_cols = st.multiselect(
                "اختر الأعمدة الرقمية المراد تحليل ارتباطها:",
                options=numeric_cols,
                default=numeric_cols
            )

            if selected_corr_cols:
                corr_matrix = df[selected_corr_cols].corr().round(2)
                fig_corr = px.imshow(
                    corr_matrix, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r',
                    title='مصفوفة الارتباط بين المتغيرات'
                )
                st.plotly_chart(fig_corr, use_container_width=True)

    elif analysis_type == 'تحليل التوزيع (Histogram/Box Plot)':
        col_for_hist = st.selectbox("اختر العمود لتحليل توزيعه:", options=all_cols)
        
        if col_for_hist:
            # إذا كان العمود رقمي، أضف Box Plot احترافي
            marginal_type = "box" if col_for_hist in numeric_cols else None
            
            fig_hist = px.histogram(
                df, x=col_for_hist, marginal=marginal_type,
                title=f'توزيع القيم للعمود: {col_for_hist}'
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    elif analysis_type == 'تحليل العلاقة (Scatter Plot)':
        if len(numeric_cols) < 2:
             st.warning("تحليل Scatter Plot يتطلب عمودين رقميين على الأقل.")
        else:
            col_x = st.selectbox("المحور X (رقمي):", options=numeric_cols)
            col_y = st.selectbox("المحور Y (رقمي):", options=numeric_cols)
            col_color = st.selectbox("التلوين حسب (متغير نوعي اختياري):", options=['لا يوجد'] + object_cols)

            if col_x and col_y:
                color_param = col_color if col_color != 'لا يوجد' else None
                fig_scatter = px.scatter(
                    df, x=col_x, y=col_y, color=color_param,
                    title=f'العلاقة بين {col_x} و {col_y}'
                )
                st.plotly_chart(fig_scatter, use_container_width=True)


def analyze_hr_management(df):
    """منطق التحليل الاحترافي لوحدة إدارة الموظفين."""
    st.title("👨‍💼 نظام إدارة وتحليل الموظفين (HR Analytics)")
    
    st.sidebar.header("تصفية بيانات الموظفين")
    selected_department = st.sidebar.multiselect(
        "تصفية حسب القسم:",
        options=df['Department'].unique(),
        default=df['Department'].unique()
    )
    df_selection = df[df['Department'].isin(selected_department)]

    if df_selection.empty:
        st.warning("لا توجد بيانات موظفين مطابقة للفلاتر المختارة.")
        return

    # --- 1. المقاييس الرئيسية (KPIs) ---
    st.subheader("المقاييس الرئيسية (KPIs)")
    total_employees = len(df_selection)
    avg_salary = df_selection['Monthly_Salary'].mean()
    avg_tenure = df_selection['Tenure_Years'].mean()
    turnover_rate = (len(df) - df['Is_Active'].sum()) / len(df) * 100 # المعدل على مستوى الشركة بالكامل

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric(label="إجمالي الموظفين", value=total_employees)
    with col2: st.metric(label="متوسط الراتب الشهري", value=f"{avg_salary:,.0f} EGP")
    with col3: st.metric(label="متوسط سنوات الخدمة", value=f"{avg_tenure:.1f} سنوات")
    with col4: st.metric(label="معدل الدوران الكلي", value=f"{turnover_rate:.1f}%")

    st.markdown("---")

    # --- 2. التحليل الاحترافي المتعمق ---
    st.subheader("تحليل الأداء والدوران الاحترافي")

    tab_perf, tab_risk = st.tabs(["الأداء والتوزيع", "مخاطر الدوران"])
    
    with tab_perf:
        # الأداء مقابل الراتب (Scatter Plot)
        fig_scatter = px.scatter(
            df_selection,
            x='Monthly_Salary',
            y='Performance_Rating',
            color='Department',
            size='Tenure_Years',
            hover_data=['EmployeeID', 'Age'],
            title='توزيع تقييم الأداء حسب الراتب وسنوات الخدمة'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # توزيع الموظفين حسب القسم
        department_count = df_selection.groupby('Department').size().reset_index(name='Total_Employees')
        fig_dept = px.bar(
            department_count, x='Department', y='Total_Employees', title='توزيع الموظفين حسب القسم', color='Department'
        )
        st.plotly_chart(fig_dept, use_container_width=True)
        
    with tab_risk:
        # تحليل مخاطر الدوران
        risky_employees = df_selection.sort_values(by='Turnover_Risk_Score', ascending=False).head(10)
        
        st.info("🚨 أعلى 10 موظفين عرضة لمخاطر الدوران (بناءً على الأداء القليل/الخدمة القصيرة):")
        st.dataframe(risky_employees[['EmployeeID', 'Department', 'Performance_Rating', 'Tenure_Years', 'Turnover_Risk_Score']].set_index('EmployeeID'), use_container_width=True)

        # توزيع المخاطر حسب القسم
        fig_risk = px.histogram(
            df_selection, x='Turnover_Risk_Score', color='Department', marginal="box",
            title='توزيع درجة مخاطر الدوران حسب القسم'
        )
        st.plotly_chart(fig_risk, use_container_width=True)

# =============================================================================
# منطق التنقل الرئيسي (Main App Logic)
# =============================================================================

st.sidebar.title("🛠️ نظام الإدارة المتكامل")
st.sidebar.markdown("---")

# اختيار الوحدة من الشريط الجانبي
module_selection = st.sidebar.radio(
    "اختر وحدة النظام:",
    ('مقدمة النظام', 'تحليل البيانات العامة', 'إدارة الموظفين والتحليل')
)
st.sidebar.markdown("---")

if module_selection == 'مقدمة النظام':
    st.title("🌟 مرحبًا بك في نظام الإدارة المتكامل والتحليل الاحترافي")
    st.markdown("""
        هذا النظام موحد تم تطويره باستخدام **Streamlit** و **Pandas** للتحليل الاحترافي.
        يمكنك التنقل بين الوحدات المختلفة باستخدام الشريط الجانبي الأيسر.
        
        **الوحدات المتوفرة:**
        
        * **تحليل البيانات العامة:** قم بتحميل أي ملف (CSV/Excel) واحصل على تحليل احترافي فوري لجودة البيانات والارتباطات والتوزيع.
        * **إدارة الموظفين والتحليل:** نظام تحليلي مخصص لبيانات الموارد البشرية، يعرض مؤشرات الأداء الرئيسية (KPIs) وتحليل مخاطر الدوران.
        """)
    st.balloons()

elif module_selection == 'تحليل البيانات العامة':
    st.title("📂 وحدة تحليل البيانات العامة")
    st.info("قم بتحميل ملفك (CSV أو Excel) للحصول على تحليل احترافي فوري.")
    
    uploaded_file = st.file_uploader(
        "يرجى تحميل ملف بياناتك:",
        type=['csv', 'xlsx']
    )
    
    df_general = None
