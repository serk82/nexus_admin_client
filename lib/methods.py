def get_format_miles(number):
    return f"{int(number):,}".replace(",", ".")

def get_date_format(date):
    from datetime import datetime
    date = datetime.strptime(date, "%Y-%m-%d")
    return date.strftime("%d/%m/%Y")

def get_kms_vehicle(license_plate):
    import requests
    import xml.etree.ElementTree as ET

    url = "http://46.183.112.193:8083/executarservgru.asp?metode=kms_grues"
    response = requests.get(url)
    if response.status_code == 200:
        vehicles = ET.fromstring(response.text)
        for vehicle in vehicles.findall("GRUA"):
            if vehicle.find("MATRICULA").text == license_plate:
                return vehicle.find("KMS").text


def get_kms_vehicles():
    import requests
    import xml.etree.ElementTree as ET

    url = "http://46.183.112.193:8083/executarservgru.asp?metode=kms_grues"
    response = requests.get(url)
    if response.status_code == 200:
        return ET.fromstring(response.text)


def is_numeric_string(value: str, field: str):
    import re

    if not bool(re.fullmatch(r"\d+", value.strip())):
        raise ValueError(f"El valor '{field}' debe tener un formato numérico!")


def question_no_yes(self, message):
    from PyQt6.QtWidgets import QMessageBox

    result = QMessageBox.question(
        self,
        " ",
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return QMessageBox.StandardButton(result)
