from osgeo import gdal, osr

fn_raster = 'C:/Users/Соня/Downloads/1.tif'
fn_footprint = 'C:/Users/Соня/Downloads/footprint_1.geojson'
fn_output = 'C:/Users/Соня/Downloads/image_1_copy2.tif'

dataset = gdal.Open(fn_raster)
driver = gdal.GetDriverByName('GTiff')
output_dataset = driver.CreateCopy(fn_output, dataset, 0)

bands_list = []
for i in range(1, dataset.RasterCount + 1):
    band = dataset.GetRasterBand(i)
    band_array = band.ReadAsArray().astype(float)
    bands_list.append(band_array)

ft_layer = QgsVectorLayer(fn_footprint, 'footprint', 'ogr')
QgsProject.instance().addMapLayer(ft_layer)

feature = ft_layer.getFeature(0)
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

outr_layer = QgsRasterLayer(fn_output, 'image_1_copy.tif')
QgsProject.instance().addMapLayer(outr_layer)