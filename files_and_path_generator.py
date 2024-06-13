import os
from datetime import datetime


def generate_pdf_filename(folder_name):
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    filename = f"{date_str}-{time_str}.pdf"

    # Create directory if it does not exist
    directory = os.path.join(os.getcwd(), folder_name)
    if not os.path.exists(directory):
        os.makedirs(directory)

    return os.path.join(directory, filename)
