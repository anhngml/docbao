# docbao
Ứng dụng web giúp phát hiện trends trên các trang báo mạng Việt Nam

demo: http://docbao.tudonghoamaytinh.com/

# nguyên lý hoạt động

## 1. Backend
Backend sử dụng thư viện BeautifulSoup của python để lọc ra toàn bộ link có trong homepage của các trang báo. Với mỗi link thu được, quét trang mà nó dẫn đến, cố gắng tìm html tag / class chứa thông tin về ngày tháng xuất bản bài viết (mỗi báo sẽ có cấu hình riêng, lưu trong file config tên là docbao.txt). Nếu tìm thấy ngày tháng xuất bản, và ngày đó nằm trong phạm vi ngày thiết lập để quét, thì bổ sung bài đó vào csdl để xử lý tiếp. Những link không phải bài báo thì đưa vào blacklist để tránh quét lại

Với mỗi link tới bài báo đã có trong csdl, sử dụng Vntokenizer để trách thành mảng các từ khóa. Trước khi tách sử dụng thêm file stopwords-nlp-vi.txt và collocation.txt (là 2 file được nhập bằng tay qua giao diện web - mục "Bổ sung từ ghép" trong demo), để hệ thống tách chính xác và chỉ giữ những từ khóa có nội dung. Sau khi đã tách tít thành các từ khóa, thì đếm và sắp xếp các từ khóa theo thứ tự tần suất xuất hiện giảm dần.

Tiếp đó, toàn bộ csdl các tít báo được xuất ra file article_data.json, top từ khóa xuất ra hot_keyword.json, toàn bộ từ khóa xuất ra keyword_dict.json, các từ khóa chưa được gán category thì xuất ra uncategorized_keyword.txt (những từ khóa đã được phân category qua giao diện web được lưu trong folder category), một số thông tin khác như tổng số bài báo, số nguồn quét được xuất ra log_data.json.

Sau đó toàn bộ các file trên được đẩy lên host chứa frontend thông qua giao thức ftp.

Toàn bộ quy trình trên được lặp lại với tần suất 5p/lần thông qua crontab (gọi file run_docbao.sh, để sử dụng file này cần config rclone để kết nối với host qua ftp)

Backend của demo (docbao.tudonghoamaytinh.com) hiện chạy trên Raspberry Pi 3 và đạt hiệu quả tốt với số lượng quét mỗi lần trên 30 đầu báo. Lần chạy đầu tiên sẽ tương đối chậm vì phải check toàn bộ các link, các lần chạy sau chỉ mất từ 2-3 phút do có blacklist và thông thường trong 5 phút chỉ có thêm vài bài viết mới.

## 2. Frontend

Frontend được cải biến dựa trên https://html5boilerplate.com/, sử dụng một chút AngularJS để đọc các file json và nạp dữ liệu cho các thư viện javascript vẽ biểu đồ và bảng thông tin cho người dùng. Sử dụng thêm một chút javascript ở client để cung cấp các tính năng như click vào keywork thì lọc báo và cuộn xuống phần danh sách báo. (toàn bộ phần này nằm trong file index.html và readdata.js)

Riêng phần bổ sung stopword, từ ghép và phân nhóm cho từ khóa sử dụng một chút php (thực ra vì host giá rẻ, chỉ hỗ trợ php nên không dùng được python) để lưu dữ liệu ra các file collocation.txt, stopwords-nlp-vi.txt, uncategorized_keyword.txt và các file trong folder category. Toàn bộ các file này sẽ được đồng bộ về Backend bằng rclone trước khi chạy app python quét dữ liệu (xem thêm file run_docbao.sh)


# Cài đặt:
1. Copy folder client lên một máy chủ chạy linux (khuyến khích đặt đường dẫn tại ~/docbao/client   - sorry vì cách đặt tên dễ gây hiểu lầm này) và cài đặt python3 trở lên, cùng các package cần thiết để có thể run được file docbao.py. Lưu ý: nếu chạy trên Windows thì cài Anaconda và fix lại các đường dẫn trong file docbao.txt (đổi / thành \).

2. Copy folder server lên một host hỗ trợ php. Tạo tài khoản ftp để có thể đẩy file lên host

3. Cài rclone trên server, config rclone để kết nối với host qua ftp. Khuyến khích đặt kết nối tên là "docbao"

4. Sửa lại file run_docbao.sh cho phù hợp với đường dẫn đã cài đặt

5. Lần chạy thứ nhất, chạy trực tiếp docbao.py để quét các bài báo mới (nên xóa file article.dat, blacklist.dat để hệ thống khởi tạo lại csdl). Quá trình chạy có thể kéo dài tầm 10-20p

6. Ngay Sau lần chạy thứ nhất, cài đặt crontab để chạy file run_docbao.sh với chu kì 5 phút (quãng thời gian quá ngắn có thể khiến docbao.py chưa kịp quét xong nhưng tự động nhân bản làm chậm server --> không thể chạy hết)

# Cấu hình:
File cấu hình quan trọng nhất là client\docbao.txt. File ở dạng yaml để dễ chỉnh sửa. Phần quan trọng nhất của file này là khai báo cấu hình để quét báo. 

Vói mỗi một nguồn báo để quét được cần khai báo cấu hình quét như sau:
~~~
- Người Lao động:  
    url: https://nld.com.vn  
    date_tag:  
    date_class:  
        - ngayxuatban  
    date_re: (\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})  
~~~
date_tag là list các tag_name có thể có của phần html chứa published_date trong web (cái này mở page source của bài viết để tìm, ví dụ: <time>...</time>)
date_class tương tự, là list các class_name có thể có của phần html chứa pushlised_date trong web. Ví dụ: <div class="ngayxuatban">...</>
date_re là expression để kiểm tra nội dung date tag / class đó có phải là ngày tháng không, và dùng để trích ngày tháng đó ra, đưa về một dạng chuẩn vì mỗi báo lại để một kiểu hiển thị thời gian khác nhau.

Một số thông số quan trọng khác:
- so_tu_toi_thieu_cua_tieu_de: mặc định là 3. Thông số này dùng để loại nhanh link mà không cần kiểm tra vì tiêu đề bài báo đa số không ít hơn 4 từ. 
- so_ngay_toi_da_lay_so_voi_hien_tai: mặc định là 0, nghĩa là chỉ lưu trong cơ sở dữ liệu những bài báo đã quét được trong ngày hôm nay. Nếu đặt là 1 sẽ lưu cả những bài báo đã quét trong ngày hôm qua. Mặc dù đặt con số càng lớn, thì csdl càng phong phú, tuy nhiên việc thống kê và xác định từ khóa hot sẽ bị ảnh hưởng do những đề tài cũ hơn sẽ có nhiều bài viết hơn. Ở demo (http://docbao.tudonghoamaytinh.com) hiện đặt là 1, dựa trên nhận xét một vấn đề trên báo mạng thường không hot quá 2 ngày, nên chỉ csdl chỉ cần phân tích 2 ngày gần nhất là đủ.





