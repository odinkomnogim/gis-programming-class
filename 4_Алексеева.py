from osgeo import gdal
from qgis.core import QgsVectorLayer, QgsProject

import numpy as np
import os

input_raster_path = 'C:/QGIS_Project/no_crs/1.tif'
output_raster_path = 'C:/QGIS_Project/no_crs/1_copy.tif'
footprint_path = 'C:/QGIS_Project/footprints/footprint_1.geojson'

raster = gdal.Open(input_raster_path)

bands_data = []
for i in range(1, raster.RasterCount + 1):
    band = raster.GetRasterBand(i)
    array = band.ReadAsArray().astype(float)
    bands_data.append(array)

driver = gdal.GetDriverByName('GTiff')
out_raster = driver.Create(output_raster_path, raster.RasterXSize, raster.RasterYSize, raster.RasterCount, gdal.GDT_Float32)

for i, array in enumerate(bands_data):
    out_band = out_raster.GetRasterBand(i + 1)
    out_band.WriteArray(array)

footprint_layer = QgsVectorLayer(footprint_path, 'footprint', 'ogr')
if not footprint_layer.isValid():
    raise Exception("Ошибка")

feature = next(footprint_layer.getFeatures())
geometry = feature.geometry()
polygon = geometry.asPolygon()[0]

corner_points = [(point.x(), point.y()) for point in polygon[:4]]

crs = footprint_layer.crs()
out_raster.SetProjection(crs.authid())

gcps = [
    gdal.GCP(corner_points[0][0], corner_points[0][1], 0, 0, 0),
    gdal.GCP(corner_points[1][0], corner_points[1][1], 0, raster.RasterXSize - 1, 0),
    gdal.GCP(corner_points[2][0], corner_points[2][1], 0, raster.RasterXSize - 1, raster.RasterYSize - 1),
    gdal.GCP(corner_points[3][0], corner_points[3][1], 0, 0, raster.RasterYSize - 1),
]

out_raster.SetGCPs(gcps, out_raster.GetProjection())
out_raster.FlushCache()
