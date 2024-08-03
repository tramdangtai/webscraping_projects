# 1. About get_data.py
File này là file chính, lưu trữ các class chứa code web scraping.

## Class Get_Data_From_Bocaodientu()
Mục tiêu:
Mỗi lần chạy sẽ là lấy dữ liệu các công ty thành lập mới nhất từ web bocaodientu về máy local.
Sau đó phân chia dữ liệu cho các file tỉnh thành nhằm cụ thể hóa mục tiêu tìm dữ liệu theo tỉnh thành.

## Class Support_Analytics_Get_Data_From_Web()
Mục tiêu:
Hỗ trợ class Get_Data_From_Bocaodientu trong việc làm sạch dữ liệu và phân chia dữ liệu ra các file csv, excel liên quan.

## Class Get_Data_From_Masothue_Version_One() & Get_Data_From_Masothue_Version_Two()
Mục tiêu:
Sử dụng dữ liệu sẵn có từ bocaodientu từ class Get_Data_From_Bocaodientu, tìm kiếm thêm các thông tin chi tiết, quan trọng nhất là số điện thoại từ web masothue để lấy số điện thoại về hỗ trợ telesales tư vấn.

Notes:
2 phiên bản vì tùy chỉnh của web, có lúc Version_One trả về kết quả tốt, có lúc Version_Two trả về kết quả tốt. Sử dụng cả 2 nhằm lấy được dữ liệu một cách nhiều nhất.


## Class Get_Data_From_Thuvienphapluat()
Mục tiêu:
Sử dụng dữ liệu từ class Get_Data_From_Masothue_Version_One và Get_Data_From_Masothue_Version_Two, và làm đầy đủ dữ liệu hơn bằng cách tìm kiếm thêm các thông tin liên quan khác của công ty từ web Thuvienphapluat.


# 2. About get_data_bctc_py.
Thực hiện import các class web scraping và chạy code.

Mục tiêu: Lấy các báo cáo tài chính mình cần từ Ủy ban chứng khoán nhà nước về bằng cách chỉ cần nhập vào các đối số: Mã cổ phiếu, thời gian muốn tìm báo cáo, loại báo cáo


# 3. About get_data_bocaodientu.py
Thực hiện lấy dữ liệu các công ty mới thành lập từ bocaodientu, masothue và thuvienphapluat.

Mục tiêu:
Tìm kiếm số điện thoại để hỗ trợ telesales trong việc tiếp cận khách hàng tiềm năng.


