from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # wait web driver load
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import os
from os import listdir
from os.path import isfile, join, getctime
from unicodedata import normalize, is_normalized
import pandas as pd
from datetime import datetime
from time import sleep



DICT_COLUMNS = {
    "Ngày đăng trên Bố cáo": "Date",
    "Mã số doanh nghiệp": "Tax code",
    "Tên đầy đủ của công ty": "Name Company",
    "Tỉnh thành trụ sở chính": "Place",
    "Loại thông báo": "Type Notification",
    "Số điện thoại giám đốc": "Phone",
    "Ngày lấy số điện thoại từ web": "Date_Phone_Updates",
    "Năm sinh của giám đốc": "Year of birth",
    "Nơi sinh của giám đốc (tỉnh)": "City of birth",
    "Tên tiếng anh của Công ty": "Name in English",
    "Tên giao dịch viết tắt": "Abbreviated transaction name",
    "Họ và tên của giám đốc": "Legal representative Full name",
    "Địa chỉ trụ sở chính": "Head office address",
    "Giới tính giám đốc": "Gender",
    "Loại hình pháp lý": "Type of organization",
    "Ngày thành lập": "Issued date",
    "Chi cục Thuế quản lý": "Tax Department Manages",
    "ID lĩnh vực hoạt động kinh doanh chính": "Main Business Lines ID",
    "Lĩnh vực hoạt động kinh doanh chính": "Main Business Lines Content",
    "Tình trạng hoạt động": "Operating",
    "Chức vụ": "Position",
    "Vốn điều lệ": "Charter_Capital",
    "Email": "Mail"
}
NEW_COLUMN_ORDER = ["Type Notification",
                    "Place",
                    "Operating",
                    "Main Business Lines ID",
                    "Main Business Lines Content",
                    "Tax Department Manages",
                    "Type of organization",
                    "Head office address",
                    "Issued date",
                    "Charter_Capital",
                    "Abbreviated transaction name",
                    "Name in English",
                    "Name Company",
                    "Tax code",
                    "Date",
                    "Phone",
                    "Date_Phone_Updates",
                    "Legal representative Full name",
                    "Gender",
                    "Year of birth",
                    "City of birth",
                    "Position",
                    "Mail"
                    ]

PATH_FOLDER_GET_DATA_NEW_REGISTRATION = "E:/Admin/TramDangTai/PycharmProjects/pythonProject1/Data_Bocao/New_Registration"
PATH_FOLDER_SAVE_DATA_NEW_REGISTRATION = "J:/My Drive/data/New_Registration"
PATH_FOLDER_SAVE_DATA_NEW_REGISTRATION_XLSX = "J:/My Drive/data/New_Registration_xlsx"
PATH_FILE_TPHCM_CSV_NEW_REGISTRATION = f"{PATH_FOLDER_SAVE_DATA_NEW_REGISTRATION}/City_Thành phố Hồ Chí Minh.csv"
PATH_FILE_TPHCM_XLSX_NEW_REGISTRATION = f"{PATH_FOLDER_SAVE_DATA_NEW_REGISTRATION_XLSX}/City_Thành phố Hồ Chí Minh.xlsx"


class Get_Data_From_Bocaodientu():
    def __init__(seft):
        seft.url_bocao = "https://bocaodientu.dkkd.gov.vn/egazette/Forms/Egazette/DefaultAnnouncements.aspx"
        seft.options = Options()
        seft.options.add_argument("--headless=new")  # Hidden webdriver

    def Get_bocao_page_source(seft, Page, Notification):
        """ web scraping here
        :param Page: Số trang trên web lấy dữ liệu.
        :param Notification: loại dữ liệu nào cần lấy.
        :return: page_source
        """
        Int_Page = int(Page)  # Chuyển đổi type page thành int để đảm bảo code run.

        # Thao tác với Edge - mở Edge - truy cập url
        driver = webdriver.Edge(options=seft.options)
        driver.get(seft.url_bocao)

        # Click vào trường chứa loại dữ liệu nào cần lấy.
        Click_Type_Notificaion = driver.find_element(By.ID, f"ctl00_C_RptProdGroups_ctl0{Notification}_EGZDivItem")
        Click_Type_Notificaion.click()

        # Tìm element page cuối trang, gần với button chuyển page nhất để chuẩn bị sử dụng tab
        anchor_tag = driver.find_element(By.XPATH, '//*[@id="ctl00_C_CtlList"]/tbody/tr[22]/td')
        actions = ActionChains(driver)
        actions.move_to_element(anchor_tag)

        # Nếu page khác 1 thì chạy code ben dưới. Này là gửi phím tab để chuyển qua số page mong muốn rồi enter.
        if Int_Page != 1:
            actions.send_keys(Keys.TAB * (Int_Page - 1))
            actions.send_keys(Keys.RETURN)
            actions.perform()
            sleep(2)

        # dùng BeautifulSoup lấy page_source để chuẩn bị lấy data.
        page_source = BeautifulSoup(driver.page_source, "html.parser")
        return page_source

    def Get_Data_From_Source(seft, NumberofPage, Notification):
        """
        :param NumberofPage: số trang của page cần lấy dữ liệu
        :param Notification: loại dữ liệu nào cần lấy.
        :return: list data chứa dữ liệu thô.
        """
        Page_Source = seft.Get_bocao_page_source(NumberofPage, Notification)
        Data_Raw = Page_Source.find_all("td")
        # Chuyển đổi dữ liệu từ scraping thành list.
        List_Data_Raw_From_Source = [value.get_text().strip() for value in Data_Raw]
        return List_Data_Raw_From_Source

    def Modify_Data_Name_Company(seft, List_Data_Infor_Company):
        """ Function hỗ trợ xử lý lấy name company
        :param List_Data_Infor_Company:
        :return: list data name company modify
        """
        List_Split_Data_Infor_Com = [item.split() for item in List_Data_Infor_Company]
        List_Split_Data_Infor_Com = [item[:-4] for item in List_Split_Data_Infor_Com]
        Data_Name_Company = [" ".join(item) for item in List_Split_Data_Infor_Com]
        return Data_Name_Company

    def Get_List_Data_NameCompany(seft, List_Data_Raw):
        """
        :param List_Data_Raw: là list data chứa dữ liệu thô được lấy từ function: Get_Data_From_Source
        :return: list data name company final
        """
        List_Data_Infor_Company = [List_Data_Raw[i] for i in range(1, len(List_Data_Raw) - 6, 5)]
        List_Split_Data_Infor_Com = [item.split() for item in List_Data_Infor_Company]
        List_Split_Data_Infor_Com = [item[:-4] for item in List_Split_Data_Infor_Com]
        Data_Name_Company = [" ".join(item) for item in List_Split_Data_Infor_Com]
        return Data_Name_Company

    def Craw_Data_Bocao_OneFile(seft, Type_Notification):
        """ code run final
        :param Type_Notification: loại dữ liệu nào cần lấy.
        :return: thông báo đã chạy code xong.
        """
        List_Notification = {1: 'New_Registration',
                             2: 'Notice_Changes',
                             3: 'Register_Changes',
                             4: "Violation_Revocation",
                             5: "Dissolution",
                             6: "Others"
                             }

        List_Data_Date = []
        List_Data_Place = []
        List_Data_Type_Notification = []
        List_Data_MST = []
        List_Data_Name_Company = []

        for num_page in range(1, 6):
            Data = seft.Get_Data_From_Source(num_page, Type_Notification)

            List_Data_Date.extend([Data[i] for i in range(0, len(Data) - 6, 5)])  # List Comprehension: Data Date & Time
            List_Data_Place.extend([Data[i] for i in range(2, len(Data) - 6, 5)])  # List Comprehension: Data Place
            # Data Type of Notification
            List_Data_Type_Notification.extend([Data[i] for i in range(3, len(Data) - 6, 5)])
            # List Data Infor Company
            List_Data_Infor_Company = [Data[i] for i in range(1, len(Data) - 6, 5)]
            List_Data_MST.extend([str(item.split()[-1]) for item in List_Data_Infor_Company])  # List Data MST
            List_Data_Name_Company.extend(seft.Get_List_Data_NameCompany(Data))

        # Combine & convert from List to Dict - in order to convert from dict to dataframe
        Dict_Data_Raw = {"Date": List_Data_Date,
                         "Tax code": List_Data_MST,
                         "Name Company": List_Data_Name_Company,
                         "Place": List_Data_Place,
                         "Type Notification": List_Data_Type_Notification,
                         }
        DF_Data_Raw = pd.DataFrame(Dict_Data_Raw)
        Date = f"{datetime.now().hour}h{datetime.now().minute}__{datetime.now().day}.{datetime.now().month}.{datetime.now().year}"
        DF_Data_Raw.to_csv(f'Data_Bocao/{List_Notification[Type_Notification]}/{Date}_ListCompany.csv')
        print(
            f"Complete Crawl Data from web: bocaodientu.dkkd.gov.vn. Type Data: {List_Notification[Type_Notification]}")


class Support_Analytics_Get_Data_From_Web():
    def __init__(seft):
        seft.path_folder_save_data = "J:/My Drive/data"
        seft.path_folder_txt = "E:/Admin/TramDangTai/PycharmProjects/pythonProject1/Data_Bocao"

    def Get_All_Namefile_in_Folder(seft, path):
        """ Get name file have type .csv
        :param path: Path folder get name file
        :return: list name file.
        """
        name_all_file = [f for f in listdir(path) if isfile(join(path, f))]
        name_all_file.sort(key=lambda x: getctime(join(path, x)))
        # Xử lý lỗi hiện 'desktop.ini' khi chạy code lấy tên file.
        if 'desktop.ini' in name_all_file:
            name_all_file.remove('desktop.ini')
        return name_all_file

    def Get_List_Data_Place(seft, path):
        """
        Này là sẽ trả về 1 list tên của các Place bên trong path folder để lấy data.
        :param path:
        :return:
        """
        name_all_file = seft.Get_All_Namefile_in_Folder(path)
        List_Data_Place = []
        for name_file in name_all_file:
            Data = pd.read_csv(f"{path}/{name_file}")
            for i in Data["Place"]:
                if i not in List_Data_Place:
                    List_Data_Place.append(i)
        return List_Data_Place

    def insert_data_to_csv(seft, province, data):
        """
        Hàm này chèn dữ liệu mới vào đầu file CSV tương ứng với tỉnh thành.
        :param province: Tên tỉnh thành.
        :param data: DataFrame chứa dữ liệu mới.
        :return: save file csv, excel have new data.
        """
        try:
            # Đọc file CSV tỉnh thành hiện có (nếu có)
            existing_data = pd.read_csv(f"{PATH_FOLDER_SAVE_DATA_NEW_REGISTRATION}/City_{province}.csv")
        except FileNotFoundError:
            # File CSV 0 tồn tại, tạo file mới
            existing_data = pd.DataFrame()

            # Xử lý DataFrame rỗng
        if existing_data.empty:
            # Nếu existing_data rỗng, ghi dữ liệu mới trực tiếp
            data.to_csv(f"{PATH_FOLDER_SAVE_DATA_NEW_REGISTRATION}/City_{province}.csv", index=False)
        else:
            # Nếu existing_data không rỗng, chèn dữ liệu mới vào đầu
            new_data = data.copy()  # Tạo bản sao dữ liệu mới
            # Chèn dữ liệu mới vào đầu
            new_data = pd.concat([new_data, existing_data], ignore_index=True)
            # Ghi dữ liệu vào file
            new_data.to_csv(f"{PATH_FOLDER_SAVE_DATA_NEW_REGISTRATION}/City_{province}.csv", index=False)

    def is_csv_file_exists(seft, csv_filename):
        """
        check tên file CSV đã tồn tại trong file txt hay chưa.
        :param csv_filename: Tên file CSV.
        :return: bool: True nếu tên file CSV đã tồn tại, False nếu chưa
        """
        with open(f"{seft.path_folder_txt}/namefile_New_Registration.txt", "r") as f:
            for line in f:
                if csv_filename in line.strip():
                    return True
        return False

    def write_namefile_in_file_txt(seft, csv_filename):
        """
        write name files csv into file txt - in order to save name file, purpose: check name file in txt exits or not
        :param csv_filename: ten file csv
        :return: file txt insert to name files csv.
        """
        with open(f"{seft.path_folder_txt}/namefile_New_Registration.txt", "a") as f:
            f.write(f"{csv_filename}\n")

    def Data_Distribution(seft):
        """
        Code run final
        :return: Phân phối dữ liệu từ result class Get_Data_From_Bocaodientu đến các file nhỏ hơn theo tỉnh.
        """
        List_Data_City = seft.Get_List_Data_Place(PATH_FOLDER_GET_DATA_NEW_REGISTRATION)
        All_FileName_in_Folder_GetData = seft.Get_All_Namefile_in_Folder(PATH_FOLDER_GET_DATA_NEW_REGISTRATION)

        for namefile in All_FileName_in_Folder_GetData:
            if not seft.is_csv_file_exists(namefile):
                # đọc file csv + giữ type chỗ Tax code (không mất số 0 ban đầu).
                df = pd.read_csv(f"{PATH_FOLDER_GET_DATA_NEW_REGISTRATION}/{namefile}",
                                 dtype={"Tax code": object})
                # Lặp qua từng tỉnh thành
                for province in List_Data_City:
                    # Lọc dữ liệu theo tỉnh thành
                    province_df = df[df["Place"] == province]
                    seft.insert_data_to_csv(province, province_df)

                seft.write_namefile_in_file_txt(namefile)
        sleep(0.1)
        seft.Remove_Data_Duplicate_TPHCM()
        print("Data has been distributed successfully!")

    def Remove_Data_Duplicate_TPHCM(self):
        """ Removed duplicate "Tax code" records for file TP.HCM
        :return: Notification "Removed duplicate records. Completed!"
        """
        df = pd.read_csv(f"{PATH_FILE_TPHCM_CSV_NEW_REGISTRATION}", dtype={"Tax code": object})
        df.drop_duplicates(subset=['Tax code'], inplace=True)  # Xóa các bản ghi trùng lặp dựa trên 'TAX Code'
        df.to_csv(f"{PATH_FILE_TPHCM_CSV_NEW_REGISTRATION}", index=False)  # Cập nhật file hiện tại)
        self.Modify_0("Tax code")  # Code: Xu ly cho tax code, phone lost 0 của TPHCM.

        # Save data to excel for work.
        df = df[NEW_COLUMN_ORDER]
        df.to_excel(f'{PATH_FOLDER_SAVE_DATA_NEW_REGISTRATION_XLSX}/City_Thành phố Hồ Chí Minh.xlsx', index=False)
        print("Removed duplicate records. Completed!")

    def Modify_0(self, column):
        """
        Fix bug: dữ liệu mã số thuế và phone không bắt đầu bằng số 0 (mã số thuế ở TP.HCM đặc biệt có số 0 ban đầu)
        :param column: tên cột.
        :return: save file với columns phone và tax code đều có số 0 trước mỗi dữ liệu.
        """
        if column == "Phone":
            df = pd.read_csv(PATH_FILE_TPHCM_CSV_NEW_REGISTRATION,
                             dtype={"Tax code": object, "Phone": object})
            for index, row in df.iterrows():
                row_phone = row["Phone"]
                df.at[index, "Phone"] = self.update_number_hasnot_0(row_phone)
        elif column == "Tax code":
            df = pd.read_csv(PATH_FILE_TPHCM_CSV_NEW_REGISTRATION,
                             dtype={"Tax code": object})
            for index, row in df.iterrows():
                row_tax_code = row["Tax code"]
                df.at[index, "Tax code"] = self.update_number_hasnot_0(row_tax_code)
        df.to_csv(PATH_FILE_TPHCM_CSV_NEW_REGISTRATION, index=False)

    def update_number_hasnot_0(self, number):
        """
        Code support function Modify_0
        :param number: number need fix 0.
        :return: số đã có số 0 ban đầu.
        """
        if str(number) == "" or str(number) == "nan":
            return number
        elif not str(number).startswith('0'):
            return str('0' + str(number))  # Thêm 0 vào trước nếu không bắt đầu bằng 0
        elif str(number).endswith(".0"):
            return str(number).replace(".0", "")  # xóa số 0 phía sau vì type float
        else:
            return number


class Get_Data_From_Masothue_Version_One():
    def __init__(seft):
        seft.DICT_ELEMENT_WEB = {"Tên quốc tế": "Name in English",
                                 "Tên viết tắt": "Abbreviated transaction name",
                                 "Địa chỉ": "Head office address",
                                 "Người đại diện": "Legal representative Full name",
                                 "Điện thoại": "Phone",
                                 "Ngày hoạt động": "Issued date",
                                 "Quản lý bởi": "Tax Department Manages",
                                 "Loại hình DN": "Type of organization",
                                 "Tình trạng": "Operating",
                                 "Giới tính": "Gender",
                                 "Mã ngành nghề kinh doanh chính": "Main Business Lines ID",
                                 "Ngành ngành nghề kinh doanh chính": "Main Business Lines Content"}
        seft.URL_TPHCM_city = "https://masothue.com/tra-cuu-ma-so-thue-theo-tinh/ho-chi-minh-23"

    def Modify_soup(seft, list_infor_tbody):
        """Support Analytics, Cleaning data.
        :param list_infor_tbody: list data raw.
        :return: dict is a value of dict final (key: value)
        """
        dict_save_infor_raw_1 = {seft.DICT_ELEMENT_WEB[element]: item
                                 for item in list_infor_tbody
                                 for element in seft.DICT_ELEMENT_WEB
                                 if element in item}

        dict_save_infor_raw_2 = {}
        for item in dict_save_infor_raw_1:  # item = value (name columns)
            for element in seft.DICT_ELEMENT_WEB:
                if element in dict_save_infor_raw_1[item]:
                    if element == "Người đại diện":
                        if "sinh năm" in dict_save_infor_raw_1[item]:
                            # Name Director
                            list_string_infor_director = dict_save_infor_raw_1[item].replace(f"{element} ", "")
                            list_string_infor_director = list_string_infor_director.split(" ( ")
                            name_director = list_string_infor_director[0]
                            dict_save_infor_raw_2["Legal representative Full name"] = name_director
                            # Year of birth Director
                            list_year_city_of_director = list_string_infor_director[1].split(" - ")
                            list_infor_year_of_director = list_year_city_of_director[0].split(" ")
                            year_of_director = list_infor_year_of_director[-1]
                            dict_save_infor_raw_2["Year of birth"] = year_of_director
                            # City of birth Director
                            list_infor_city_of_director = list_year_city_of_director[1].split(") ")
                            city_of_director = list_infor_city_of_director[0]
                            dict_save_infor_raw_2["City of birth"] = city_of_director

                    else:
                        dict_save_infor_raw_2[item] = dict_save_infor_raw_1[item].replace(f"{element} ", "")
        return dict_save_infor_raw_2

    def interaction_web_masothue(seft, df):
        """ web scraping here
        :param df: dataframe taken from file csv local.
        :return: dict infor company: key = index of dataframe, value = dict infor company.
        """
        dict_infor_index_content = {}

        driver = webdriver.Edge()
        driver.get(seft.URL_TPHCM_city)
        sleep(0.5)
        driver.maximize_window()

        for index, row in df.iterrows():
            phone_number = row["Phone"]
            name_director = row["Legal representative Full name"]
            if str(phone_number) == "nan" or len(str(name_director)) < 5:
                name_company = row["Name Company"]
                # Tìm danh sách xổ xuống rồi chọn Tên Công Ty.
                sleep(1.5)
                # 29.06.2024 - fix bug: Message: element click intercepted
                try:
                    select_categories_element = driver.find_element(By.ID, "product_cat")
                    select_categories_element.click()
                    categories_enterpriseName_element = select_categories_element.find_element(By.CSS_SELECTOR,
                                                                                               'option[value="enterpriseName"]')
                    categories_enterpriseName_element.click()
                except:
                    continue

                sleep(0.3)
                # Tìm ô điền thông tin + điền tên Công ty.
                search_element = driver.find_element(By.CLASS_NAME, "input-group")
                search_input = search_element.find_element(By.ID, "search")
                sleep(1.1)
                # Check search element have data.
                if search_input.get_attribute("value") != "":
                    search_input.clear()
                    sleep(1.1)
                search_input.send_keys(name_company)
                sleep(1.5)
                # Bấm enter trên bàn phim.
                search_input.send_keys(Keys.ENTER)
                sleep(1.4)
                # Di chuyển màn hình xuống 1 chút.
                driver.execute_script("window.scrollTo(0, 1459)")
                sleep(1.2)
                try:
                    tbody_element = driver.find_element(By.XPATH, '//*[@id="main"]/section[1]/div/table[1]/tbody')
                    tbody_content = tbody_element.text
                    list_tbody_content = tbody_content.split("\n")
                except:
                    list_tbody_content = []
                if len(list_tbody_content) != 0:
                    sleep(0.3)
                    # gender
                    try:
                        gender_element_xpath = driver.find_element(By.XPATH,
                                                                   f'//*[@id="main"]/section[1]/div/table[@class="table-taxinfo"]/'
                                                                   f'tbody/tr[@itemprop="alumni"]/td[2]/i')
                        gender_element_xpath = gender_element_xpath.get_attribute("class")
                        gender_element = gender_element_xpath.split("-")
                        gender = gender_element[1]
                        list_tbody_content.append("Giới tính " + gender)
                    except:
                        gender = ""
                        list_tbody_content.append(gender)
                    sleep(0.6)
                    # Ngành nghề kinh doanh chính
                    try:
                        main_business_lines_element = driver.find_element(By.XPATH,
                                                                          f'//*[@id="main"]/section[1]/div/table[@class="table"]/'
                                                                          f'tbody/tr/td/strong')
                        main_business_lines_id = main_business_lines_element.text

                        main_business_lines_content_element = main_business_lines_element.find_element(By.XPATH,
                                                                                                       ".//ancestor::tr")
                        main_business_lines_content = main_business_lines_content_element.find_element(By.XPATH,
                                                                                                       ".//td[2]")
                        main_business_lines_content = main_business_lines_content.text
                        list_tbody_content.extend(["Mã ngành nghề kinh doanh chính " + main_business_lines_id,
                                                   "Ngành ngành nghề kinh doanh chính " + main_business_lines_content])
                    except:
                        main_business_lines_content = ""
                        main_business_lines_id = ""
                        list_tbody_content.extend([main_business_lines_content, main_business_lines_id])
                dict_infor_index_content[index] = seft.Modify_soup(list_tbody_content)
                if len(dict_infor_index_content) > 199:
                    return dict_infor_index_content
        return dict_infor_index_content

    def fill_infor_from_web_to_file_local(seft, data, dict_infor_from_web):
        """
        Fill data take from web into dataframe.
        :param data: dataframe taken from file csv.
        :param dict_infor_from_web: dict is return of function interaction_web_masothue
        :return:
        """
        for index, row in data.iterrows():
            if index in dict_infor_from_web:
                data.at[index, "Date_Phone_Updates"] = datetime.now()
                for name_column in dict_infor_from_web[index]:
                    data[name_column] = data[name_column].astype(object)
                    data.at[index, name_column] = dict_infor_from_web[index][name_column]
        return data

    def Get_Data_TPHCM(seft):
        """Run code final
        """
        data = pd.read_csv(PATH_FILE_TPHCM_CSV_NEW_REGISTRATION, dtype={"Tax code": object, "Phone": object})
        dict_infor_company_in_web = seft.interaction_web_masothue(data)
        df = seft.fill_infor_from_web_to_file_local(data, dict_infor_company_in_web)
        df.to_csv(PATH_FILE_TPHCM_CSV_NEW_REGISTRATION, index=False)  # save data into csv file
        # save data from csv to excel để mọi người dễ sài.
        df = df[NEW_COLUMN_ORDER]
        df.to_excel(PATH_FILE_TPHCM_XLSX_NEW_REGISTRATION, index=False)
        print(f"Completed. Added Phone Number from web masothue.com to Data TP.HCM. Version_One")


class Get_Data_From_Masothue_Version_Two():
    def __init__(seft):
        seft.url_getdata = "https://masothue.com/"
        seft.options = Options()
        seft.options.add_argument("--headless=new")  # Hidden webdriver
        seft.Analytics_Data = Support_Analytics_Get_Data_From_Web()  # Class support each other

    def xoa_dau(self, txt: str) -> str:
        """
        :param txt: 1 word để mình xóa dấu nó
        :return: word đã xóa dấu.
        """
        BANG_XOA_DAU = str.maketrans(
            "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
            "A" * 17 + "D" + "E" * 11 + "I" * 5 + "O" * 17 + "U" * 11 + "Y" * 5 + "a" * 17 + "d" + "e" * 11 + "i" * 5 + "o" * 17 + "u" * 11 + "y" * 5
        )
        if not is_normalized("NFC", txt):
            txt = normalize("NFC", txt)
        return txt.translate(BANG_XOA_DAU)

    def Get_All_Namefile_in_Folder(seft):
        """
        Get name file have type .csv
        :return: List name file have type .csv
        """
        path_folder = PATH_FOLDER_SAVE_DATA_NEW_REGISTRATION
        name_all_file = [f for f in listdir(path_folder) if isfile(join(path_folder, f))]
        name_all_file.sort(key=lambda x: getctime(join(path_folder, x)))
        if 'desktop.ini' in name_all_file:  # Xử lý lỗi hiện 'desktop.ini' khi chạy code lấy tên file.
            name_all_file.remove('desktop.ini')
        return name_all_file

    def Get_URL_Company_Get_Data(self, dataframe):
        """
        :param dataframe: dataframe from file csv.
        :return: Dict các url để run webdriver.
        """
        Dict_URL = {}
        # Lặp qua mỗi hàng trong DataFrame
        for index, row in dataframe.iterrows():
            # Lấy giá trị từ cột "Tax code" và "Place"
            tax_code = row["Tax code"]
            name_company = row["Name Company"]
            phone_number = row["Phone"]
            name_director = row["Legal representative Full name"]

            # Nếu trường số phone trống hoặc k có tên giám đốc, run code below.
            if str(phone_number) == "nan" or len(str(name_director)) < 5:
                name_company_modify = name_company.lower()
                name_company_modify = self.check_char_special(name_company_modify)
                name_company_modify = name_company_modify.replace(" ", "-")
                name_company_xoa_dau = self.xoa_dau(name_company_modify)
                # Kết hợp giá trị thành chuỗi mới
                chuoi_moi = f"{tax_code}-{name_company_xoa_dau}"

                # Gộp với url để thành url hoàn chỉnh.
                url_get_data = self.url_getdata + chuoi_moi
                # đưa vào list để dễ quản lý.
                Dict_URL[index] = url_get_data
                if len(Dict_URL) > 15:
                    return Dict_URL
        return Dict_URL

    def Get_Infor_Company_onWeb(self, dict_url_company: dict):
        """
        Web Scraping Here.
        :param dict_url_company: dict các url của từng công ty để run.
        :return: dict infor company from web
        """
        driver = webdriver.Edge()
        dict_infor_company_index = {}
        for index in dict_url_company:
            driver.get(dict_url_company[index])
            sleep(2)
            driver.execute_script("window.scrollTo(0, 1369)")
            sleep(1)
            # Address
            try:
                address_element = driver.find_element(By.CSS_SELECTOR, 'td[itemprop="address"]')
                address = address_element.text
            except:
                address = ""
            sleep(1)
            # Name Director
            try:
                name_element_xpath = driver.find_element(By.XPATH,
                                                         '//*[@id="main"]/section[1]/div/table[@class="table-taxinfo"]'
                                                         '/tbody/tr[@itemprop="alumni"]/td[2]/span')
                name_director = name_element_xpath.text
            except:
                name_director = ""
            sleep(1.1)
            # Phone
            try:
                phone_element = driver.find_element(By.CSS_SELECTOR, 'td[itemprop="telephone"]')
                phone_text = phone_element.text
            except:
                phone_text = "0"
            sleep(1.009)
            # Name Company Global
            try:
                name_globe_element = driver.find_element(By.CSS_SELECTOR, 'td[itemprop="alternateName"]')
                name_globe_element = name_globe_element.text
            except:
                name_globe_element = "0"
            sleep(1.008)
            # Abbreviated transaction name: Tên giao dịch viết tắt
            try:
                abbreviated_transaction_name_icon = driver.find_element(By.XPATH,
                                                                        f'//*[@id="main"]/section[1]/div/table[@class="table-taxinfo"]/'
                                                                        f'tbody/tr/td/i[@class="fa fa-reorder"]')
                abbreviated_transaction_name_element = abbreviated_transaction_name_icon.find_element(By.XPATH,
                                                                                                      ".//ancestor::tr")
                abbreviated_transaction_name_element = abbreviated_transaction_name_element.find_element(By.XPATH,
                                                                                                         ".//td[2]")
                abbreviated_transaction_name = abbreviated_transaction_name_element.text
            except:
                abbreviated_transaction_name = ""
            sleep(1.1)
            # Gender Director
            try:
                gender_element_xpath = driver.find_element(By.XPATH,
                                                           f'//*[@id="main"]/section[1]/div/table[@class="table-taxinfo"]/'
                                                           f'tbody/tr[@itemprop="alumni"]/td[2]/i')
                gender_element_xpath = gender_element_xpath.get_attribute("class")
                gender_element = gender_element_xpath.split("-")
                gender = gender_element[1]
            except:
                gender = ""
            sleep(0.9)
            # năm sinh + nơi sinh giám đốc
            if not gender == "":
                year_and_city_of_birth_element_xpath = driver.find_element(By.XPATH,
                                                                           f'//*[@id="main"]/section[1]/div/table[@class="table-taxinfo"]/'
                                                                           f'tbody/tr[@itemprop="alumni"]/td[2]')
                year_and_city_of_birth_element_xpath = year_and_city_of_birth_element_xpath.text
                year_and_city_of_birth_element_xpath = year_and_city_of_birth_element_xpath.split("(")
                year_and_city_of_birth_element_xpath = year_and_city_of_birth_element_xpath[1].split(")")
                year_and_city_of_birth = year_and_city_of_birth_element_xpath[0].strip()

                list_year_and_city_of_birth = year_and_city_of_birth.split("-")
                year_of_birth = list_year_and_city_of_birth[0].strip()
                year_of_birth = year_of_birth.split(" ")
                year_of_birth = year_of_birth[2]

                city_of_birth = list_year_and_city_of_birth[1].strip()
            else:
                year_of_birth = ""
                city_of_birth = ""
            sleep(0.5)
            # Ngày hoạt động
            try:
                issued_date_element = driver.find_element(By.XPATH,
                                                          f'//*[@id="main"]/section[1]/div/table[@class="table-taxinfo"]/'
                                                          f'tbody/tr/td/i[@class="fa fa-calendar"]')
                issued_date_element_content = issued_date_element.find_element(By.XPATH, ".//ancestor::tr")
                issued_date = issued_date_element_content.find_element(By.XPATH, ".//td[2]")
                issued_date = issued_date.text
            except:
                issued_date = ""
            sleep(1.1)
            # Chi cục thuế quản lý
            try:
                tex_department_manages_element = driver.find_element(By.XPATH,
                                                                     f'//*[@id="main"]/section[1]/div/table[@class="table-taxinfo"]/'
                                                                     f'tbody/tr/td/i[@class="fa fa-users"]')
                tex_department_manages = tex_department_manages_element.find_element(By.XPATH, ".//ancestor::tr")
                tex_department_manages = tex_department_manages.find_element(By.XPATH, ".//td[2]")
                tax_department_manages = tex_department_manages.text
            except:
                tax_department_manages = ""
            sleep(0.4)
            # Loại hình DN
            try:
                type_of_organization_element = driver.find_element(By.XPATH,
                                                                   f'//*[@id="main"]/section[1]/div/table[@class="table-taxinfo"]/'
                                                                   f'tbody/tr/td/i[@class="fa fa-building"]')
                type_of_organization = type_of_organization_element.find_element(By.XPATH, ".//ancestor::tr")
                type_of_organization = type_of_organization.find_element(By.XPATH, ".//td[2]")
                type_of_organization = type_of_organization.text
            except:
                type_of_organization = ""
            sleep(0.1)
            # Tình trạng
            try:
                operating_element = driver.find_element(By.XPATH,
                                                        f'//*[@id="main"]/section[1]/div/table[@class="table-taxinfo"]/'
                                                        f'tbody/tr/td/i[@class="fa fa-info"]')
                operating = operating_element.find_element(By.XPATH, ".//ancestor::tr")
                operating = operating.find_element(By.XPATH, ".//td[2]")
                operating = operating.text
            except:
                operating = ""
            sleep(1.5)
            # Ngành nghề kinh doanh chính
            try:
                main_business_lines_element = driver.find_element(By.XPATH,
                                                                  f'//*[@id="main"]/section[1]/div/table[@class="table"]/'
                                                                  f'tbody/tr/td/strong')
                main_business_lines_id = main_business_lines_element.text

                main_business_lines_content_element = main_business_lines_element.find_element(By.XPATH,
                                                                                               ".//ancestor::tr")
                main_business_lines_content = main_business_lines_content_element.find_element(By.XPATH, ".//td[2]")
                main_business_lines_content = main_business_lines_content.text
            except:
                main_business_lines_content = ""
                main_business_lines_id = ""
            sleep(0.2)
            dict_infor_company = {
                "Year of birth": year_of_birth,
                "City of birth": city_of_birth,
                "Phone": phone_text,
                "Name in English": name_globe_element,
                "Legal representative Full name": name_director,
                "Head office address": address,
                "Gender": gender,
                "Type of organization": type_of_organization,
                "Issued date": issued_date,
                "Tax Department Manages": tax_department_manages,
                "Operating": operating,
                "Main Business Lines ID": main_business_lines_id,
                "Main Business Lines Content": main_business_lines_content,
                "Abbreviated transaction name": abbreviated_transaction_name
            }

            dict_infor_company_index[index] = dict_infor_company
            # if int(index) > 1000:
            #     return dict_infor_company_index
        return dict_infor_company_index

    def Add_Data(self, data, dict_infor: dict):
        """data: dataframe của file csv.
        dict_infor: dict số phone đã get from web
        Return: dataframe.
        """
        dict_infor_company = dict_infor
        for index, row in data.iterrows():
            if index in dict_infor_company:
                data.at[index, "Date_Phone_Updates"] = datetime.now()
                for name_column in dict_infor_company[index]:
                    data[name_column] = data[name_column].astype(object)
                    data.at[index, name_column] = dict_infor_company[index][name_column]
        return data

    def Get_Data_TPHCM(self):
        """
        Final Code of Class.
        :return:
        """
        start_time = datetime.now()
        #
        df = pd.read_csv(PATH_FILE_TPHCM_CSV_NEW_REGISTRATION,
                         dtype={"Tax code": object, "Phone": object})
        dict_url = self.Get_URL_Company_Get_Data(df)
        dict_infor_company = self.Get_Infor_Company_onWeb(dict_url)
        dataframe_after_add_infor = self.Add_Data(df, dict_infor_company)
        dataframe_after_add_infor.to_csv(PATH_FILE_TPHCM_CSV_NEW_REGISTRATION, index=False)

        end_time = datetime.now()
        print('Duration: {}'.format(end_time - start_time))

        # Modify Phone has not 0.
        self.Analytics_Data.Modify_0("Phone")
        # save data from csv to excel để mọi người dễ sài.
        dataframe_after_add_infor = dataframe_after_add_infor[NEW_COLUMN_ORDER]
        dataframe_after_add_infor.to_excel(PATH_FILE_TPHCM_XLSX_NEW_REGISTRATION, index=False)
        print(f"Completed. Added Phone Number from web masothue.com to Data TP.HCM. Version_Two")

    def delete_char_trash(self, text: str, char: str) -> str:
        """
        Code hỗ trợ function check_char_special
        :param text: tên công ty.
        :param char: ký tự special
        :return: tên công ty đã xử lý các ký tự đặc biệt.
        """
        index_character = text.index(char)
        text_final = text[:index_character - 1] + text[index_character + 1:]
        return text_final

    def check_char_special(self, text: str):
        """
        Code check và fix ký tự đặc biệt có gây ra lỗi trong khi tạo url để web scraping.
        :param text: tên công ty.
        :return: tên công ty đã xử lý các ký tự đặc biệt.
        """
        List_char_replace_blank = [".", ","]
        for char in List_char_replace_blank:
            if char in text:
                count_char = text.count(char)
                if count_char == 1:
                    return text.replace(char, " ")
                elif count_char == 2:
                    text_final = text.replace(char, " ")
                    return text_final.replace(char, " ")
        List_char_delete = ["&", "-"]
        for char in List_char_delete:
            if char in text:
                count_char = text.count(char)
                if count_char == 1:
                    return self.delete_char_trash(text, char)
                elif count_char == 2:
                    text_final = self.delete_char_trash(text, char)
                    return self.delete_char_trash(text_final, char)
            else:
                return text


class Get_Data_From_Thuvienphapluat():
    def __init__(seft):
        seft.URL_WEB_THUVIENPHAPLUAT = "https://thuvienphapluat.vn/ma-so-thue"
        seft.options = Options()
        seft.options.add_argument("--headless=new")  # Here

    def get_mst_fill_web(self, data):
        """
        :param data: dataframe for file csv.
        :return: dict - key: index of dataframe, value: mst have condition
        """
        dict_link = {}
        for index, row in data.iterrows():
            # các công ty gần nhất sẽ chưa update mail. Nên lấy các công ty trước đó 1 chút khả năng sẽ cao hơn.
            row_phone = row["Phone"]
            name_director = row["Legal representative Full name"]
            gender = row["Gender"]
            tax_department = row["Tax Department Manages"]
            mail = row["Mail"]
            Charter_Capital = row["Charter_Capital"]
            Position = row["Position"]
            date = row["Date"]
            date_check = int(str(date[0]) + str(date[1]))
            day_now = datetime.now()
            day_check = day_now.day
            if (
                    len(str(row_phone)) > 5
                    and len(str(name_director)) > 5
                    and len(str(tax_department)) > 5
                    and len(str(gender)) > 3
                    and len(str(mail)) < 5
                    and len(str(Charter_Capital)) < 5
                    and len(str(Position)) < 5
                    and date_check < day_check):
                row_tax_code = row["Tax code"]
                dict_link[index] = row_tax_code
        return dict_link

    def get_data_from_web(self, dict_mst_fill_web):
        """
        :param dict_mst_fill_web:  dict of function get_dict_mst_fill_web
        :return: dict, key = name column, value = dict [name column]: value in oder to fill dataframe
        """
        driver = webdriver.Edge(options=self.options)
        driver.get(self.URL_WEB_THUVIENPHAPLUAT)
        sleep(0.2)
        dict_infor_company = {}
        dict_index_name_column = {}
        for index in dict_mst_fill_web:
            input_mst_element = driver.find_element(By.CSS_SELECTOR, 'input[name="tukhoa"]')
            if input_mst_element.get_attribute("value") != "":
                input_mst_element.clear()
                sleep(0.1)
            input_mst_element.send_keys(dict_mst_fill_web[index])

            sleep(0.1)
            input_mst_element.send_keys(Keys.ENTER)
            sleep(0.1)
            try:
                click_mst_element = driver.find_element(By.CSS_SELECTOR, 'tr[class="item_mst"]')
                click_mst_element_detail = click_mst_element.find_element(By.XPATH, ".//child::a")
                click_mst_element_detail.click()
                sleep(0.5)
                run_code = True
            except:
                run_code = False
            if run_code:
                content_all_page_element = driver.find_element(By.ID, "ThongTinDoanhNghiep")
                sleep(0.5)
                content_all_page = content_all_page_element.text
                List_content_all = content_all_page.split("\n")
                # check Position
                for item in List_content_all:
                    for infor in DICT_COLUMNS:
                        if infor == "Chức vụ" and infor in item:
                            dict_infor_company[DICT_COLUMNS[infor]] = item.replace("Chức vụ: ", "").strip()
                        elif infor in item:
                            index_type = List_content_all.index(item)
                            dict_infor_company[DICT_COLUMNS[infor]] = List_content_all[index_type + 1]
                if len(dict_infor_company) != 0:
                    dict_index_name_column[index] = dict_infor_company
        return dict_index_name_column

    def fill_data_from_web_to_file(self, data_web, dataframe_csv):
        """
        :param data_web: dict from function get_data_from_web
        :param dataframe_csv: dataframe of file csv.
        :return: dataframe filled information of company
        """
        for index, row in dataframe_csv.iterrows():
            if index in data_web:
                for item in data_web:
                    for name_column in data_web[item]:
                        dataframe_csv.at[index, name_column] = data_web[item][name_column]
        return dataframe_csv

    def Get_Data_TPHCM(self):
        """
        Code Final of Class Get_Data_From_Thuvienphapluat
        :return:
        """
        data_tphcm = pd.read_csv(PATH_FILE_TPHCM_CSV_NEW_REGISTRATION, dtype={"Tax code": object})
        dict_mst = self.get_mst_fill_web(data_tphcm)
        data_from_web = self.get_data_from_web(dict_mst)
        if len(data_from_web) != 0:
            data_filled = self.fill_data_from_web_to_file(data_from_web, data_tphcm)
            data_filled.to_csv(PATH_FILE_TPHCM_CSV_NEW_REGISTRATION, index=False)  # save data to csv
            data_filled.to_excel(PATH_FILE_TPHCM_XLSX_NEW_REGISTRATION, index=False)  # save data to excel
            print("Run code: Complete. Get Data from Web: Thuvienphapluat.")
        else:
            print("Run code: Complete. But, not value changed.")


class Get_Data_From_Topi():
    def __init__(seft):
        seft.url = "https://topi.vn/danh-sach-ma-chung-khoan-theo-nganh-tai-viet-nam.html"


    def GetDataStock_in_webTopi(seft):
        """
        access link web topi & scraping data from web to dataframe & list.
        :return: 2 value:
        value 1: df data name company & stocks
        value 2: list group stocks.
        """
        driver = webdriver.Edge()
        driver.get(seft.url)
        # get page source
        page_source = BeautifulSoup(driver.page_source, "html.parser")
        driver.close()
        # get all information data about name company and stocks
        infor_tbody = page_source.find_all('td')
        # convert from page source infor text --> import list.
        list_save_infor = [word.get_text().strip() for word in infor_tbody]
        # get list name company from list above (list_save_infor)
        list_save_ten_congty = [word for word in list_save_infor if list_save_infor.index(word) % 2 == 0]
        # get list stocks from list above (list_save_infor)
        list_save_macp = [word for word in list_save_infor if list_save_infor.index(word) % 2 != 0]
        # concat from 2 list name company & stocks into 1 dict.
        result = {'Name': list_save_ten_congty, 'Ma Co Phieu': list_save_macp}
        dataframe_raw = pd.DataFrame(result)

        # get all name group stocks (nhóm ngành)
        infor_group_stocks = page_source.find_all('h3')
        # convert from page_source above to text --> import list.
        list_save_infor_h3 = [word.get_text().strip() for word in infor_group_stocks]
        # split data usefully and save list.
        List_Data_Group_Stocks = list_save_infor_h3[1:][:-6]
        # insert 1 group not have in list above.
        List_Data_Group_Stocks.insert(3, "3.1. Cổ phiếu ngành Thiết bị điện, điện tử")
        return dataframe_raw, List_Data_Group_Stocks


    def save_data_stock(seft, df, list_group_stocks):
        # get all index of column have value is 'Mã cổ phiếu', and then, save it to list.
        List_Index_MCP = df.index[df['Ma Co Phieu']== 'Mã cổ phiếu'].tolist()
        # save every group stock into file csv.
        for chimuc in range(len(List_Index_MCP)):
            if List_Index_MCP[chimuc] != max(List_Index_MCP):
                new_df = df.iloc[List_Index_MCP[chimuc] + 1: List_Index_MCP[chimuc + 1]]
            elif List_Index_MCP[chimuc] == max(List_Index_MCP):
                new_df = df.iloc[List_Index_MCP[chimuc] + 1: df.shape[0] - 1]
            namefile = list_group_stocks[chimuc].split(".")[-1]
            new_df.to_csv(f'data_stocks\Ma_cp_theo_nganh\{namefile.strip()}.csv')
        print(f"Completed web scraping data stock in web. Link folder: {os.getcwd()}\data_stocks\Ma_cp_theo_nganh")


class Get_Data_From_SSC():
    def __init__(seft):
        seft.url_ssc_gov = 'https://congbothongtin.ssc.gov.vn/faces/NewsSearch'
        seft.edge_options = Options()
        # seft.edge_options.add_experimental_option("detach", True)  # keep browser open
        seft.edge_options.add_argument("--headless=new")  # Hidden webdriver
        seft.dict_report_id = {'BCDKT': {'id_report': 'pt2:BCDKT::ti', 'id_body': 'pt2:BCDKT'},
                  'KQKD': {'id_report': 'pt2:KQKD::ti', 'id_body': 'pt2:KQKD'},
                  'LCTT-GT': {'id_report': 'pt2:LCTT-GT::ti', 'id_body': 'pt2:LCTT-GT'}}


    def user_enter_ma_cp(seft):
        user_need_ma_cp = input('What stock do you want get data? Please enter the correct stock code. '
                                '\nI want to get data about stock: ').upper()
        if len(user_need_ma_cp) != 3:
            print('You did not type stock code correctly. The stock code has three words.')
            type_again = input('Do you want to type again? Please enter: "Yes" or "No"\n').lower()
            if type_again == 'yes':
                seft.user_enter_ma_cp()
            elif type_again != 'yes':
                print('Exit')
                return 0
        elif len(user_need_ma_cp) == 3:
            print('------------')
            return user_need_ma_cp


    def user_need_period_date(seft, ma_cp='Stocks'):
        print(f'What time period do you want to get data on {ma_cp} stock? Please enter follow format: "DD/MM/YYYY"')
        start_date = input('From Date: ')
        end_date = input('To Date: ')
        if end_date > start_date:
            print('------------')
            return start_date, end_date
        else:
            print('Date Error: To_Date must be bigger From_Data. Please enter again! ')
            seft.user_need_period_date(ma_cp)
            return 0, 0


    def user_report(seft):
        user_need_report = input(
            'What report do you want? Please input 1 of 3 word (reports): "BCDKT", "KQKD" or "LCTT-GT". '
            '\nOr if you want to get all reports, please enter "ALL"'
            '\nI want report: ').upper()
        if user_need_report not in seft.dict_report_id and user_need_report != 'ALL':
            print('You did not type the word correctly. Please type again.')
            seft.user_report()
        print('------------')
        return user_need_report


    def get_name_quantity_report(seft, macp, list_element_by_row):
        list_data_raw = [element.getText() for element in list_element_by_row]

        list_name_report = [list_data_raw[i] for i in range(1, len(list_data_raw), 6)]
        list_name_company = [list_data_raw[i] for i in range(2, len(list_data_raw), 6)]
        list_detail_name_report = [list_data_raw[i] for i in range(3, len(list_data_raw), 6)]
        list_time_send_report = [list_data_raw[i] for i in range(4, len(list_data_raw), 6)]

        if len(list_name_report) == 0:
            print("Not found reports about stock and date you enter. Please Exit & Enter again. "
                  "\nYou can change: date (longer time). Thanks!")
            return 0
        else:
            print('------------')
            print(
                f"Number of reports found for stock code: {macp} - {list_name_company[0]} là: {len(list_name_report)}.")
            dict_infor_company = {'Name Report': list_name_report,
                                  'Time send Report': list_time_send_report,
                                  'Detail Report': list_detail_name_report}
            data = pd.DataFrame(dict_infor_company)
            print('Data is shown below:')
            print(data)
            print('------------')
            dict_name_report = {key: list_detail_name_report[key] for key in range(len(list_detail_name_report))}
            is_number_correct, number_name_report = seft.is_number_in_dict_name_report(dict_name_report)
            if is_number_correct:
                return number_name_report, data['Detail Report'][number_name_report]


    def is_number_in_dict_name_report(self, dict_check: dict):
        print('What is Name Report do you want? Please enter 1 number corresponding to Name Report.')
        number = int(input('What is number you want? \nI want: '))
        if number in dict_check:
            print(f'Ok, You want to get data about "{dict_check[number]}". Wait for few minutes....')
            print('------------')
            return True, number
        else:
            print('The number you entered is incorrect. '
                  '\nPlease enter a number that corresponds to the Report Name above.')
            self.is_number_in_dict_name_report(dict_check)
            return False, number


    def is_number_in_dict_type_report(self, dict_check: dict):
        name_report_user_want = input('Which type of name report do you want? \n'
                                      'Please enter number corresponding report. Number you want is: ')
        if name_report_user_want in dict_check:
            print(f'Ok. You choose: {dict_check[name_report_user_want]}.')
            return True, name_report_user_want
        else:
            print('The number you entered is incorrect. '
                  '\nPlease enter a number that corresponds to the type of Report above.')
            self.is_number_in_dict_type_report(dict_check)
            return False, name_report_user_want


    def get_data(self, ma_cp, from_date, to_date, report_id, type_report=None):
        print('Please wait for 1, 2 minutes...')
        # Open Webdriver.
        driver = webdriver.Edge(options=self.edge_options)
        WebDriverWait(driver, 10)
        # try: because error "selenium.common.exceptions.WebDriverException:"
        try:
            driver.get(self.url_ssc_gov)
            driver.implicitly_wait(0.1)
            # find element & enter Ma Co Phieu
            driver.find_element(By.CLASS_NAME, 'x25').send_keys(ma_cp)
            driver.implicitly_wait(0.1)
            # find element & enter date start
            driver.find_element(By.CSS_SELECTOR, 'input[id="pt9:id1::content"]').send_keys(from_date)
            driver.implicitly_wait(1)
            # find element & enter date end
            driver.find_element(By.CSS_SELECTOR, 'input[id="pt9:id2::content"]').send_keys(to_date)
            driver.implicitly_wait(1)
            # find element sort list type of report.
            driver.find_element(By.CLASS_NAME, 'x18g').click()
            driver.implicitly_wait(1)
            # get table return: name report found.
            table_report = driver.find_element(By.CLASS_NAME, 'x18w')
            check_boxs_element = table_report.find_elements(By.TAG_NAME, 'label')
            # save name report & number correction in dict
            dict_check_box_elements = {}
            if type_report in range(12):
                number = type_report
                is_number_user_want_correct = True
            else:
                for element in check_boxs_element:
                    number_check_box = element.find_element(By.CSS_SELECTOR,
                                                            'input[type="checkbox"]').get_attribute('value')
                    dict_check_box_elements[number_check_box] = element.text
                    print(number_check_box, " :", element.text)

                is_number_user_want_correct, number = self.is_number_in_dict_type_report(dict_check_box_elements)
            driver.implicitly_wait(1)
            # find element type of report & click choose
            table_report.find_element(By.CSS_SELECTOR, f'input[value="{number}"]').click()
            driver.implicitly_wait(1)
            # click button search
            driver.find_element(By.LINK_TEXT, 'Tìm kiếm').click()
            sleep(5)
            # find href element behind name report.
            try:
                rows_element = driver.find_element(By.XPATH, '//*[@id="pt9:t1::db"]/table/tbody')
                href_click_elements = rows_element.find_elements(By.PARTIAL_LINK_TEXT, 'Báo cáo ')
                id_href_elements = [hr.get_attribute('id') for hr in href_click_elements]
            except:
                print(f'No reports found for this period from {from_date} to {to_date} of stocks code: {ma_cp}.\n'
                      f'Please enter again with longer period or other stock code')
                return 'Error'
            # get new page source
            page_source = BeautifulSoup(driver.page_source, "html.parser")
            # find table return
            table_return_element = page_source.find(id='pt9:t1::db')
            # find rows in table return
            row_value_element = table_return_element.find_all(class_='x221')
            # get name report user want to get data.
            number_name_report, name_report_link_text = self.get_name_quantity_report(ma_cp, row_value_element)
            sleep(1)
            # find & click choose name report.
            driver.find_element(By.ID, id_href_elements[number_name_report]).click()
            sleep(2)
            driver.maximize_window()
            # check report is get 3 report or 1 report.
            if report_id != 'ALL':
                # find element report
                driver.find_element(By.CSS_SELECTOR, f'div[_afrptkey="pt2:{report_id}"]').click()
                driver.implicitly_wait(5)
                sleep(1)
                # get table financial report
                page_source_table = BeautifulSoup(driver.page_source, "html.parser")
                table_all_report_element = page_source_table.find(attrs={'id': f'pt2:{report_id}', 'class': 'x2af'})
                table_report_element = table_all_report_element.find_all('td', attrs={'class': 'xia'})
                # get header of report.
                headers_element = page_source_table.find_all('th', attrs={'role': "columnheader", 'class': 'x150'})
                # get financial report final
                data = self.get_report(table_report_element, headers_element)

                data.to_excel(f'data_stocks\stocks\{ma_cp}_{name_report_link_text}.xlsx', sheet_name=report_id, index=False)
                sleep(1)
            elif report_id == 'ALL':
                dict_df = {}
                for id_report in self.dict_report_id:
                    # find element report
                    driver.find_element(By.CSS_SELECTOR, f'div[_afrptkey="pt2:{id_report}"]').click()
                    driver.implicitly_wait(5)
                    sleep(1)

                    # get table financial report
                    page_source_table = BeautifulSoup(driver.page_source, "html.parser")
                    table_all_report_element = page_source_table.find(attrs={'id': f'pt2:{id_report}', 'class': 'x2af'})
                    table_report_element = table_all_report_element.find_all('td', attrs={'class': 'xia'})
                    # get header of report.
                    headers_element = page_source_table.find_all('th', attrs={'role': "columnheader", 'class': 'x150'})
                    # get financial report final
                    data = self.get_report(table_report_element, headers_element)
                    # add financial report to dict.
                    dict_df[id_report] = data
                    sleep(1)
                sleep(1)
                self.save_file(file_path=f'data_stocks\stocks\{ma_cp}_{name_report_link_text}.xlsx', dict_dataframe=dict_df)

            driver.quit()
            print(f'Completed get data: \n'
                  f'Stock {ma_cp}, \n'
                  f'Report: {report_id}, \n'
                  f'Name Report: {name_report_link_text}.')
            return 'Completed'
        except Exception as e:
            # if error relation connection, exit drive & print error.
            driver.quit()
            return 'Error: ', 'ERR_CONNECTION_TIMED_OUT'


    def get_report(seft, table_element, header_element):
        """
        :param table_element: table all content report. just need element.
        :param header_element: header content report. just need element
        :return: dataframe financial report.
        """
        # get text in element of table element
        list_data_report_value = [element.getText() for element in table_element]
        list_header = [header.getText() for header in header_element]  # get text in element of header_element
        number_header = len(list_header)  # get len list header in order to next step for loop below.
        dict_data = {}
        i = 0
        for header in list_header:
            i += 1
            list_of_header = []
            for value in range(i-1, len(list_data_report_value), number_header):
                list_of_header.append(list_data_report_value[value])
            dict_data[header] = list_of_header
        df = pd.DataFrame(dict_data)
        data = seft.check_col_empty(df)
        return data


    def save_file(self, file_path, dict_dataframe):
        """
        using ExcelWriter & xlsxwriter to save excel file.
        :param file_path: path of file excel.
        :param dict_dataframe: dict contains: values: dataframe & keys: name sheet
        :return: file excel can have multiple sheets.
        """
        writer = pd.ExcelWriter(path=file_path, engine='xlsxwriter')
        for report_id in dict_dataframe:
            dict_dataframe[report_id].to_excel(writer, sheet_name=report_id, index=False)
        writer.close()


    def check_col_empty(self, dataframe):
        data = dataframe.copy()
        for col in data.columns:
            if data[col].nunique() < 5:  # quantity unique value
                data.drop(col, axis=1, inplace=True)
        return data

