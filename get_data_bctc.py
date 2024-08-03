from get_data import Get_Data_From_SSC
import pandas as pd

ssc = Get_Data_From_SSC()

input_ma_cp = ssc.user_enter_ma_cp()
start_date, end_date = ssc.user_need_period_date(input_ma_cp)
id_report = ssc.user_report()

done = ssc.get_data(ma_cp=input_ma_cp, from_date=start_date, to_date=end_date, report_id=id_report, type_report=10)
print(done)
