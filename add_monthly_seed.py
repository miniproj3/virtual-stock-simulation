import os
import pymysql
from datetime import datetime

# RDS 연결 정보 환경변수에서 가져오기
RDS_HOST = os.environ.get('RDS_HOST')
RDS_USER = os.environ.get('RDS_USER')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD')
RDS_DB = os.environ.get('RDS_DB')

def lambda_handler(event, context):
    connection = None
    try:
        # RDS 연결 설정
        connection = pymysql.connect(
            host=RDS_HOST,
            user=RDS_USER,
            password=RDS_PASSWORD,
            database=RDS_DB,
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            today = datetime.now()
            current_month_start = today.replace(day=1)

            # 사용자 seed_krw 업데이트
            update_query = """
            UPDATE users
            SET seed_krw = seed_krw + 1000000, last_login = NOW()
            WHERE last_login < %s OR last_login IS NULL
            """
            cursor.execute(update_query, (current_month_start,))
            print(f"Monthly update applied to {cursor.rowcount} users.")

            # 신규 사용자에게 즉시 seed_krw 지급
            initialize_query = """
            UPDATE users
            SET seed_krw = GREATEST(seed_krw, 1000000)
            WHERE created_at >= %s
            """
            cursor.execute(initialize_query, (current_month_start,))
            print(f"Initial seed set for {cursor.rowcount} new users.")

            # 변경 사항 커밋
            connection.commit()

        return {
            'statusCode': 200,
            'body': f"Monthly update and initial seed set successfully executed."
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"Error occurred: {str(e)}"
        }
    finally:
        if connection:
            connection.close()
