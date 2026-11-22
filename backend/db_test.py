from app.database import engine

print("ENGINE CREATED:", engine is not None)

try:
    with engine.connect() as connection:
        result = connection.exec_driver_sql("SELECT current_database()")
        print("DATABASE CONNECTED:", result.scalar())

except Exception as error:
    print("ERROR TYPE:", type(error).__name__)
    print("ERROR MESSAGE:", str(error))
