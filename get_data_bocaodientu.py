from get_data import (Get_Data_From_Bocaodientu,
                               Get_Data_From_Masothue_Version_One,
                               Get_Data_From_Masothue_Version_Two,
                               Get_Data_From_Thuvienphapluat,
                               Support_Analytics_Get_Data_From_Web)
from time import sleep
from datetime import datetime
start_time = datetime.now()

# Task 1: Get Data Bocao
def run_task_1():
    List_Notification = {1: 'New_Registration',
                         2: 'Notice_Changes',
                         3: 'Register_Changes',
                         }
    Get_Data = Get_Data_From_Bocaodientu()
    Get_Data.Craw_Data_Bocao_OneFile(1) #Get Data New_Registration
    sleep(2)


# Task 2:  Distribution Data
def run_task_2():
    Data_Distribution = Support_Analytics_Get_Data_From_Web()
    Data_Distribution.Data_Distribution()


# Task 3: Get Data from web: masothue
def run_task_3():
    Get_Data_Web_Masothue_V1 = Get_Data_From_Masothue_Version_One()
    Get_Data_Web_Masothue_V1.Get_Data_TPHCM()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

    Get_Data_Web_Masothue_V2 = Get_Data_From_Masothue_Version_Two()
    Get_Data_Web_Masothue_V2.Get_Data_TPHCM()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))


# Task 4L Get Data From Web: thuvienphapluat
def run_task_4():
    get_data = Get_Data_From_Thuvienphapluat()
    get_data.Get_Data_TPHCM()


run_task_1()
run_task_2()
run_task_3()
run_task_4()

end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))

