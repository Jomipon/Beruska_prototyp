import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import xml.etree.ElementTree as ET
from support import download_get_url
from io import BytesIO

class forecast():
    def __init__(self,p_lat, p_lon):
        self.url_base_api = "https://api.met.no/weatherapi/locationforecast/2.0/classic"
        self.lat = p_lat
        self.lon = p_lon
    
    def get_url(self):
        return f'{self.url_base_api}?lat={str(self.lat).replace(",",".")}&lon={str(self.lon).replace(",",".")}'
    
    def download_data(self):
        url = self.get_url()
        xml_yr_no = download_get_url(url).decode('UTF-8')
        return xml_yr_no
    
    def parse_download_data(self, xml_data):
        try:
            tree = ET.ElementTree(ET.fromstring(xml_data))
        except:
            return []
        root = tree.getroot()
        products = root.findall("product")
        forecast_rows = []
        limit_from = datetime.datetime(year=datetime.date.today().year,month=datetime.date.today().month, day=datetime.date.today().day)
        limit_to = limit_from + datetime.timedelta(days = 3)
        for product in products:
            times = product.findall("time")
            for time in times:
                #<time datatype="forecast" from="2025-11-07T08:00:00Z" to="2025-11-07T08:00:00Z">
                datatype = time.attrib.get("datatype", "")
                time_from = time.attrib.get("from", "")
                time_to = time.attrib.get("to", "")
                if time_from:
                    time_from = datetime.datetime.strptime(time_from[0:-1],"%Y-%m-%dT%H:%M:%S")
                if time_to:
                    time_to = datetime.datetime.strptime(time_to[0:-1],"%Y-%m-%dT%H:%M:%S")
                locations = time.findall("location")
                if datatype == "forecast" and time_from and time_to and time_from >= limit_from and time_to < limit_to:
                    forecast_row = {}
                    forecast_row["time_from"] = time_from
                    forecast_row["time_to"] = time_to
                    for location in locations:
                        #<location altitude="379" latitude="49.78" longitude="14.17">
                        altitude = int(location.attrib.get("altitude", "0"))
                        latitude = float(location.attrib.get("latitude", "0"))
                        longitude = float(location.attrib.get("longitude", "0"))
                        forecast_row["altitude"] = altitude
                        forecast_row["latitude"] = latitude
                        forecast_row["longitude"] = longitude
                        temperature = location.find("temperature")
                        if temperature is not None:
                            #<temperature id="TTT" unit="celsius" value="5.6"></temperature>
                            temperature_id = temperature.attrib.get("id", "")
                            temperature_unit = temperature.attrib.get("unit", "")
                            temperature_value = float(temperature.attrib.get("value", "0"))
                            forecast_row["temperature_id"] = temperature_id
                            forecast_row["temperature_unit"] = temperature_unit
                            forecast_row["temperature_value"] = temperature_value
                        windDirection = location.find("windDirection")
                        if windDirection is not None:
                            #<windDirection id="dd" deg="126.7" name="SE"></windDirection>
                            windDirection_id = windDirection.attrib.get("id", "")
                            windDirection_deg = float(windDirection.attrib.get("deg", "0"))
                            windDirection_name = windDirection.attrib.get("name", "")
                            forecast_row["windDirection_id"] = windDirection_id
                            forecast_row["windDirection_deg"] = windDirection_deg
                            forecast_row["windDirection_name"] = windDirection_name
                        windSpeed = location.find("windSpeed")
                        if windSpeed is not None:
                            #<windSpeed id="ff" mps="3.4" beaufort="3" name="Lett bris"></windSpeed>
                            windSpeed_id = windSpeed.attrib.get("id", "")
                            windSpeed_mps = float(windSpeed.attrib.get("mps", "0"))
                            windSpeed_beaufort = windSpeed.attrib.get("beaufort", "")
                            windSpeed_name = windSpeed.attrib.get("name", "")
                            forecast_row["windSpeed_id"] = windSpeed_id
                            forecast_row["windSpeed_mps"] = windSpeed_mps
                            forecast_row["windSpeed_beaufort"] = windSpeed_beaufort
                            forecast_row["windSpeed_name"] = windSpeed_name
                        humidity = location.find("humidity")
                        if humidity is not None:
                            #<humidity unit="percent" value="90.5"></humidity>
                            humidity_unit = humidity.attrib.get("unit")
                            humidity_value = float(humidity.attrib.get("value"))
                            forecast_row["humidity_unit"] = humidity_unit
                            forecast_row["humidity_value"] = humidity_value
                        pressure = location.find("pressure")
                        if pressure is not None:
                            #<pressure id="pr" unit="hPa" value="1015.2"></pressure>
                            pressure_id = pressure.attrib.get("id")
                            pressure_unit = pressure.attrib.get("unit")
                            pressure_value = float(pressure.attrib.get("value"))
                            forecast_row["pressure_id"] = pressure_id
                            forecast_row["pressure_unit"] = pressure_unit
                            forecast_row["pressure_value"] = pressure_value
                        cloudiness = location.find("cloudiness")
                        if cloudiness is not None:
                            #<cloudiness id="NN" percent="30.5"></cloudiness>
                            cloudiness_id = cloudiness.attrib.get("id")
                            cloudiness_percent = float(cloudiness.attrib.get("percent"))
                            forecast_row["cloudiness_id"] = cloudiness_id
                            forecast_row["cloudiness_percent"] = cloudiness_percent
                        fog = location.find("fog")
                        if fog is not None:
                            #<fog id="FOG" percent="0.0"></fog>
                            fog_id = fog.attrib.get("id")
                            fog_percent = float(fog.attrib.get("percent"))
                            forecast_row["fog_id"] = fog_id
                            forecast_row["fog_percent"] = fog_percent
                        lowClouds = location.find("lowClouds")
                        if lowClouds is not None:
                            #<lowClouds id="LOW" percent="30.5"></lowClouds>
                            lowClouds_id = lowClouds.attrib.get("id")
                            lowClouds_percent = float(lowClouds.attrib.get("percent"))
                            forecast_row["lowClouds_id"] = lowClouds_id
                            forecast_row["lowClouds_percent"] = lowClouds_percent
                        mediumClouds = location.find("mediumClouds")
                        if mediumClouds is not None:
                            #<mediumClouds id="MEDIUM" percent="0.0"></mediumClouds>
                            mediumClouds_id = mediumClouds.attrib.get("id")
                            mediumClouds_percent = float(mediumClouds.attrib.get("percent"))
                            forecast_row["mediumClouds_id"] = mediumClouds_id
                            forecast_row["mediumClouds_percent"] = mediumClouds_percent
                        highClouds = location.find("highClouds")
                        if highClouds is not None:
                            #<highClouds id="HIGH" percent="0.0"></highClouds>
                            highClouds_id = highClouds.attrib.get("id")
                            highClouds_percent = float(highClouds.attrib.get("percent"))
                            forecast_row["highClouds_id"] = highClouds_id
                            forecast_row["highClouds_percent"] = highClouds_percent
                        dewpointTemperature = location.find("dewpointTemperature")
                        if dewpointTemperature is not None:
                            #<dewpointTemperature id="TD" unit="celsius" value="4.1"></dewpointTemperature>
                            dewpointTemperature_id = dewpointTemperature.attrib.get("id")
                            dewpointTemperature_unit = dewpointTemperature.attrib.get("unit")
                            dewpointTemperature_value = float(dewpointTemperature.attrib.get("value"))
                            forecast_row["dewpointTemperature_id"] = dewpointTemperature_id
                            forecast_row["dewpointTemperature_unit"] = dewpointTemperature_unit
                            forecast_row["dewpointTemperature_value"] = dewpointTemperature_value
                        precipitation = location.find("precipitation")
                        if precipitation is not None:
                            #<precipitation unit="mm" value="0.0"></precipitation>
                            precipitation_id = precipitation.attrib.get("id")
                            precipitation_unit = precipitation.attrib.get("unit")
                            precipitation_value = float(precipitation.attrib.get("value"))
                            forecast_row["precipitation_id"] = precipitation_id
                            forecast_row["precipitation_unit"] = precipitation_unit
                            forecast_row["precipitation_value"] = precipitation_value
                    forecast_rows.append(forecast_row)
        forecast_rows_new = []
        for forecast_row in forecast_rows:
            if forecast_row["time_from"] == forecast_row["time_to"]:
                forecast_rows_new.append(forecast_row)
        for forecast_row in forecast_rows:
            if forecast_row["time_from"] < forecast_row["time_to"] and "precipitation_id" in forecast_row:
                for forecast_row_new in forecast_rows_new:
                    if forecast_row_new["time_from"] == forecast_row_new["time_from"]:
                        forecast_row_new["precipitation_id"] = forecast_row["precipitation_id"]
                        forecast_row_new["precipitation_unit"] = forecast_row["precipitation_unit"]
                        forecast_row_new["precipitation_value"] = forecast_row["precipitation_value"]
        forecast_rows = forecast_rows_new
        return forecast_rows
    def create_graf(self,forecast_rows):
        rows = pd.DataFrame(forecast_rows)
        rows = rows[["time_from","temperature_value"]]
        rows["temp__20"] = -20
        rows["temp_0"] = 0
        rows["temp_20"] = 20
        rows_positive = rows.where(rows["temperature_value"] >= 0).dropna(how="all")
        rows_negative = rows.where(rows["temperature_value"] < 0).dropna(how="all")
        fig, ax = plt.subplots()
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m."))
        ax.xaxis.set_minor_locator(mdates.HourLocator(interval=6))
        ax.grid(axis="x", which="major", linestyle=":", linewidth=1)
        ax.plot(rows_positive["time_from"], rows_positive["temperature_value"], color="black", label="C")
        ax.plot(rows_negative["time_from"], rows_negative["temperature_value"], color="blue", label="C")
        ax.plot(rows["time_from"], rows["temp__20"], color="blue", label="- 20", linestyle='dotted')
        ax.plot(rows["time_from"], rows["temp_0"], color="green", label="- 20", linestyle='dotted')
        ax.plot(rows["time_from"], rows["temp_20"], color="yellow", label="- 20", linestyle='dotted')
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        buf.seek(0)
        return buf
            