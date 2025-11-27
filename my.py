import base64
with open("/mnt/STORAGE/HRMS/hrms_backend/users/surajit -pic.jpeg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    print(encoded_string)