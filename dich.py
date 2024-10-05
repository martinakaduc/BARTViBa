import pandas as pd
import requests

# Hàm gọi API
def translate_text(text):
    url = 'http://localhost:7000/translate/vi_ba'  # Thay đổi URL API của bạn
    payload = {
  "region": "BinhDinh",
  "text": text
}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get('tgt')  # Thay đổi tùy theo phản hồi của API
    else:
        return text  # Trả về văn bản gốc nếu có lỗi

# Đọc file Excel từ sheet 2 và lấy cột thứ 2
df = pd.read_excel('Model dịch.xlsx', sheet_name='Mức câu', usecols=[1])  # Đọc cột thứ 2 (cột B), chú ý cột đầu tiên là cột số 0

# Giả sử các câu cần dịch nằm trong cột B
texts = df.iloc[:, 0]  # Lấy dữ liệu từ cột thứ 2 (chỉ số cột bắt đầu từ 0)

# Dịch các câu
df['Translated'] = texts.apply(translate_text)  # Thêm cột mới 'Translated' chứa câu đã dịch

# Lưu DataFrame vào file Excel mới
df.to_excel('file_output.xlsx', index=False)  # Thay 'file_output.xlsx' bằng tên file bạn muốn xuất ra
