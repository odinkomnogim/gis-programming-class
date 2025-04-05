from osgeo import gdal, osr

raster_path = 'C:/Users/yermakoovaa/Downloads/4.tif'
footprint_path = 'C:/Users/yermakoovaa/Downloads/footprint_4.geojson'
output_path = 'C:/Users/yermakoovaa/Downloads/4_wfootprint.tif'

dataset = gdal.Open(raster_path, gdal.GA_ReadOnly)

bands_list = []
for i in range(1, dataset.RasterCount + 1):
    band = dataset.GetRasterBand(i)
    band_array = band.ReadAsArray().astype(float)
    bands_list.append(band_array)

driver = gdal.GetDriverByName('GTiff')
output_dataset = driver.CreateCopy(output_path, dataset, 0)

footprint_layer = QgsVectorLayer(footprint_path, 'footprint', 'ogr')
QgsProject.instance().addMapLayer(footprint_layer)

feature = footprint_layer.getFeature(0)
geometry = feature.geometry().asPolygon()[0]
corners = [(point.x(), point.y()) for point in geometry]

gcps = [
    gdal.GCP(corners[0][0], corners[0][1], 0, 0, 0),
    gdal.GCP(corners[1][0], corners[1][1], 0, output_dataset.RasterXSize - 1, 0),
    gdal.GCP(corners[2][0], corners[2][1], 0, output_dataset.RasterXSize - 1, output_dataset.RasterYSize - 1),
    gdal.GCP(corners[3][0], corners[3][1], 0, 0, output_dataset.RasterYSize - 1)
]
spatial_ref = osr.SpatialReference()
spatial_ref.ImportFromWkt(ft_layer.crs().toWkt())
output_dataset.SetGCPs(gcps, spatial_ref.ExportToWkt())
output_dataset.FlushCache()

out_raster_layer = QgsRasterLayer(output_path, '4_wfootprint.tif')
QgsProject.instance().addMapLayer(out_raster_layer)