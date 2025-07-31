# ESPHome Template for Sonoff S31

## Configure devices.csv
```CSV file
device_name,friendly_name,ip,restore_state
dishwasher,"Dishwasher",10.0.0.208,ALWAYS_ON
```

## Configure secrets.yaml
```
authentication_key: 'AUTH_KEY'
api_password: "API_PASSWORD"
ota_password: "OTA_PASSWORD"
wifi_ssid: YOUR_WIFI_SSID
wifi_password: "WIFI_PASSWORD"
ap_fallback_password: "FALLBACK_PASSWORD"
```

## Run bulk upload
```
python3 ota_bulk_upload.py
```
