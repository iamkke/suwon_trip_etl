import datetime
import calendar
import sys

from config import settings
from logger import logger

import maria
import iris

def from_month(year, month):
     year, month = (year-1, 12) if month - 1 < 1 else (year, month-1) 
     day = calendar.monthrange(year, month)[1]
     return {"start": datetime.date(year, month, 1), "end": datetime.date(year, month, day)}

def to_month(year, month):
     day = calendar.monthrange(year, month)[1]
     return  {"start": datetime.date(year, month, 1), "end": datetime.date(year, month, day)}

def get_dates(): #기간 설정
     if len(sys.argv) == 2:
          year, month = int(sys.argv[1][:4]), int(sys.argv[1][4:])
          before_month = from_month(year, month)
          this_month=to_month(year,month)
     else:
          today = datetime.date.today() 
          temp = from_month(today.year, today.month)["start"]
          
          before_month = from_month(temp.year, temp.month)
          this_month=to_month(temp.year,temp.month)         

     return {
          "before_month_start" : before_month["start"].strftime('%Y-%m-%d'),
          "before_month_end" : before_month["end"].strftime('%Y-%m-%d'),
          "this_month_start" : this_month["start"].strftime('%Y-%m-%d'),
          "this_month_end" : this_month["end"].strftime('%Y-%m-%d'),
     }

infos = [ 
    {
        "table": "VISITOR_EVENT",
        "query": """
                 select
                    {this_month_start} as REG_DATE,
                    a.EVT_ID as EVT_ID,
                    a.TTLE as TTLE, 
                    DATE_FORMAT(a.BGNG_DT, '%Y-%m-%d') as BGNG_DATE, 
                    DATE_FORMAT(a.END_DT, '%Y-%m-%d') as END_DATE,  
                    IF(a.FEE = '' , '-', a.FEE) as PAY, 
                    IF(a.EXTRL_URL = '', '-', a.EXTRL_URL) as EVT_URL, 
                    CONCAT('http://27.101.101.67', b.FILE_PATH, b.FILE_ORGL_NM) as IMG_PATH,
                    b.FILE_NO as IMG_NO_IN_SUWON_DB
               FROM evt AS a
               LEFT JOIN evt_img AS b ON a.EVT_ID = b.EVT_ID and b.LANG_ID = 1 and b.MAIN_IMG_YN = 'Y' and b.DISP_YN ='Y' and b.USE_YN = 'Y'
               WHERE a.LANG_ID = 1 and a.USE_YN = 'Y' and (a.END_DT >= '{this_month_start}' and a.END_DT <= '{this_month_end}')  
        """
    }
]

def main():
    try:
        dates = get_dates() #파일 실행시 매개변수 인자 처리 부분
        
        conditions = {
            "reg_date": dates["base_time"]
        }
        
        for i in infos:
          cols, rows = maria.fetch(i["query"].format(**dates))
          iris.update(i["table"], cols, rows, conditions)
          
        logger.info("^^")
        
    except:
        logger.exception("oo")

if __name__ == "__main__":
     main()


