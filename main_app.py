import streamlit as st
from datetime import datetime
import csv
import json

# セッション状態を管理
# 最初にページ状態を初期化
if "page" not in st.session_state:
    st.session_state["page"] = "home"

# id保持
if "id" not in st.session_state:
    st.session_state["id"] = 0

# 社員リストの初期設定
if "emp_list" not in st.session_state:
    with open("employee.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        employee_list = []
        for row in reader:
            employee_list.append(row)
    st.session_state["emp_list"] = employee_list

# 社員リストの初期設定
if "e-name" not in st.session_state:
    st.session_state["e-name"] = None


ATTENDANCE_FILE = "attendance_management_data.csv"


# csv→辞書型に変換
def add_attendance_record(emp_id, emp_name, status=None):
    time_now = datetime.now().strftime("%H:%M:%S")
    day_now = datetime.now().strftime("%Y-%m-%d")
    with open(ATTENDANCE_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader_am = csv.DictReader(f)
        rows = list(reader_am)

    found = False
    for row in rows:
        if row["社員ID"] == str(emp_id) and row["日付"] == day_now:
            if status == "出勤":
                row["出勤時間"] = time_now
            elif status == "退勤":
                row["退勤時間"] = time_now
            found = True
            break

    if not found:
        rows.append(
            {
                "社員ID": str(emp_id),
                "社員名": emp_name,
                "日付": day_now,
                "出勤時間": time_now if status == "出勤" else "",
                "退勤時間": time_now if status == "退勤" else "",
                "備考": "",
            }
        )

    with open(ATTENDANCE_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["社員ID", "社員名", "日付", "出勤時間", "退勤時間", "備考"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# CSV → JSON変換
with open("employee.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    employee_list = []
    for row in reader:
        employee_list.append(row)


# ページ遷移用の関数
def go_to_page(page_name):
    st.session_state["page"] = page_name
    st.rerun()


# 社員名検索
def get_emp_name(emp_id, emp_list):
    for emp in emp_list:
        if emp["社員ID"] == str(emp_id):
            return emp["社員名"]
    return None


# ====画面構成====
# Hemeページ(ID入力)
if st.session_state.page == "home":
    st.title("【勤怠管理】")

    with st.form("my_form"):

        employee_id = st.number_input("4桁のIDを入力してください", step=1, format="%d")
        st.session_state["id"] = employee_id
        submit_btn = st.form_submit_button("次へ")

        employee_id_str = str(employee_id)

        if submit_btn:
            if len(employee_id_str) != 4:
                st.error("4桁の数字を入力してください")
            else:
                found = False
                for row in employee_list:
                    if row["社員ID"] == employee_id_str:
                        go_to_page("page2")
                        found = True
                        break

                if not found:
                    st.error("IDが存在しません")

# 勤怠選択（出勤/退勤）
elif st.session_state.page == "page2":
    st.title("勤怠選択（出勤/退勤")

    with st.form(key="attendance_form"):
        employee_op = st.radio("勤怠管理", ("出勤", "退勤"))
        value_id = st.session_state.get("id")
        value_list = st.session_state.get("emp_list")

        emp_name = get_emp_name(value_id, value_list)
        st.session_state["e-name"] = emp_name

        if st.form_submit_button("次へ"):
            if employee_op == "出勤":
                add_attendance_record(value_id, emp_name, status="出勤")
                st.session_state.page = "page3"
                go_to_page("page3")
            elif employee_op == "退勤":
                add_attendance_record(value_id, emp_name, status="退勤")
                st.session_state.page = "page4"
                go_to_page("page4")


# 勤怠記録
elif st.session_state["page"] == "page3":
    value_name = st.session_state.get("e-name")
    value_id = st.session_state.get("id")

    with st.form(key="am_form"):
        st.text(f"{value_id}:{value_name}を以下の時間で出勤を確認しました")
        now = datetime.now()
        formatted = now.strftime("%H:%M:%S")
        st.text(f"{formatted}")

        if st.form_submit_button("戻る"):
            go_to_page("home")

# 勤怠確認
elif st.session_state["page"] == "page4":
    value_name = st.session_state.get("e-name")
    value_id = st.session_state.get("id")

    with st.form(key="am_form"):
        st.text(f"{value_id}:{value_name}を以下の時間で出勤を確認しました")
        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        st.text(f"{formatted}")
        if st.form_submit_button("戻る"):
            go_to_page("home")
