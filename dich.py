import pandas as pd
import requests

# Đọc dữ liệu từ file Excel, sheet thứ hai
file_path = 'D:\\Code\\Python\\Bahnar\\BARTViBa\\data.xlsx'  # Thay đổi thành đường dẫn tới file Excel của bạn
data = pd.read_excel(file_path, sheet_name=1)  # Sử dụng chỉ số 1 để lấy sheet thứ hai

# Hàm gọi API dịch của bạn
def translate_text(text):
    url = 'http://localhost:7000/translate/vi_ba'  # Thay đổi URL API của bạn
    payload = {'region': 'BinhDinh', 'text': text}
    print(payload)
    response = requests.post(url, json=payload)
    print(response.json())
    if response.status_code == 200:
        return response.json().get('tgt')  # Thay đổi theo phản hồi của API
    else:
        return "Loi"

# Giả sử dữ liệu bạn muốn dịch nằm ở cột đầu tiên
texts = data.iloc[:, 1].tolist()  # Lấy dữ liệu từ cột đầu tiên

# Dịch các câu
translated_texts = [translate_text(text) for text in texts]

# Tạo DataFrame từ dữ liệu gốc và đã dịch
df = pd.DataFrame({
    'Original': texts,
    'Translated': translated_texts
})

# Lưu DataFrame vào file Excel mới
df.to_excel('translated_sentences.xlsx', index=False)

print("Dịch thành công và lưu vào 'translated_sentences.xlsx'")
