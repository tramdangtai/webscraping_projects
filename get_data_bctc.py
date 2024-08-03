from web_scraping.get_data import Get_Data_From_SSC
import pandas as pd

ssc = Get_Data_From_SSC()

# input_ma_cp = ssc.user_enter_ma_cp()
# start_date, end_date = ssc.user_need_period_date(input_ma_cp)
# id_report = ssc.user_report()

done = ssc.get_data(ma_cp='VIC', from_date='01/01/2019', to_date='31/12/2023', report_id='ALL', type_report=10)
print(done)


# có tinh chỉnh chỗ lưu file excel.
# def analytics_report(path_file_excel,sheetname_kqkd, sheetname_bcdkt, sheetname_lctt, is_bank=False)

