
from tasks import stop_services
from tasks import extract_data_from_apis
from tasks import transform_data_to_lod
from tasks import restart_fuseki
from tasks import restart_lodview

stop_services()
# extract_data_from_apis()
transform_data_to_lod()
restart_fuseki()
restart_lodview()
