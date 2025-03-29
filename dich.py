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

# Đọc file CSV và lấy cột thứ 1
df = pd.read_csv('banagpt.csv', usecols=[0])  # Đọc cột thứ 1 (cột A), chú ý cột đầu tiên là cột số 0

# Giả sử các câu cần dịch nằm trong cột đầu tiên
texts = df.iloc[:, 0]  # Lấy dữ liệu từ cột đầu tiên

# Dịch các câu và lưu vào cột mới 'bana'
df['bana'] = texts.apply(translate_text)  # Thêm cột mới 'bana' chứa câu đã dịch

# Lưu DataFrame vào file CSV mới
df.to_csv('file_output.csv', index=False)  # Thay 'file_output.csv' bằng tên file bạn muốn xuất ra
