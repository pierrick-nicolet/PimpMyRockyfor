# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ConvertToAscii.py
# Created on: 05.05.2021
# by: Pierrick.Nicolet@ngu.no
#  ---------------------------------------------------------------------------
#
# This tool creates the ascii files that are needed by RockyFor3D. The input
# feature class should have been created using the tool "1. Create an empty
# feature class"
#
# Reference:
#
# https://www.ecorisq.org/ecorisq-tools
#
# ---------------------------------------------------------------------------

# Import arcpy modules
import arcpy
import os
import locale

# Retrive the parameters from the GUI
fc = arcpy.GetParameterAsText(0)
DEM = arcpy.GetParameterAsText(1)
workspace = arcpy.GetParameterAsText(2)
cellSize = float(arcpy.GetParameterAsText(3).split(' ')[0])

locale_info = locale.localeconv()
decimal_separator = locale_info['decimal_point']
thousands_separator = locale_info['thousands_sep']
#arcpy.AddMessage('The local decimal separator is: "{}", and the thousand separator is: "{}"'.format(decimal_separator,thousands_separator))

#-----------------------------------------------------------------------------
# -- Parameter list
par_list = ['rockdensity','d1','d2','d3','blshape','rg70','rg20','rg10',
			'soiltype']

fields = arcpy.ListFields(fc)

fields = [field.name for field in fields]

if 'nrtrees' in fields:
	par_list.append('nrtrees')
	par_list.append('dbhmean')
	par_list.append('dbhstd')

if 'conif_percent' in fields:
	par_list.append('conif_percent')

#-----------------------------------------------------------------------------
# --Definition of the study area

DEM = arcpy.Raster(DEM)
DEM_path = DEM.catalogPath
DEM_ext = arcpy.Describe(DEM_path).extent
arcpy.env.outputCoordinateSystem = DEM_ext.spatialReference
dem_xmin = DEM_ext.XMin
dem_xmax = DEM_ext.XMax
dem_ymin = DEM_ext.YMin
dem_ymax = DEM_ext.YMax

if arcpy.GetInstallInfo()['ProductName'] == 'Desktop':
	fc = arcpy.mapping.Layer(fc)
else:
	fc = arcpy.MakeFeatureLayer_management(fc)
arcpy.RecalculateFeatureClassExtent_management(fc) # not available with a basic license (only standard and advanced)
fc_ext = arcpy.Describe(fc).extent
# The extent of the feature class is returned in the SRC of the dataframe
if DEM_ext.spatialReference.name == fc_ext.spatialReference.name:
	# arcpy.AddMessage('The extent of the feature class is returned in the SRC of the dataframe')
	fc_xmin = fc_ext.XMin
	fc_xmax = fc_ext.XMax
	fc_ymin = fc_ext.YMin
	fc_ymax = fc_ext.YMax
else:
	# Use the original SRC of the feature class
	# arcpy.AddMessage('Use the original SRC of the feature class')
	fc_ext = arcpy.Describe(arcpy.Describe(fc).dataElement.catalogPath).extent
	pt_ll = arcpy.PointGeometry(arcpy.Point(fc_ext.XMin,fc_ext.YMin),fc_ext.spatialReference).projectAs(DEM_ext.spatialReference).centroid
	pt_ur = arcpy.PointGeometry(arcpy.Point(fc_ext.XMax,fc_ext.YMax),fc_ext.spatialReference).projectAs(DEM_ext.spatialReference).centroid
	pt_ul = arcpy.PointGeometry(arcpy.Point(fc_ext.XMin,fc_ext.YMax),fc_ext.spatialReference).projectAs(DEM_ext.spatialReference).centroid
	pt_lr = arcpy.PointGeometry(arcpy.Point(fc_ext.XMax,fc_ext.YMin),fc_ext.spatialReference).projectAs(DEM_ext.spatialReference).centroid
	
	fc_xmin = min(pt_ll.X,pt_ul.X)
	fc_xmax = max(pt_lr.X,pt_ur.X)
	fc_ymin = min(pt_ll.Y,pt_lr.Y)
	fc_ymax = max(pt_ur.Y,pt_ul.Y)


if (fc_xmin < (dem_xmin-cellSize)) or (fc_xmax > (dem_xmax+cellSize)) or (fc_ymin < (dem_ymin-cellSize)) or (fc_ymax > (dem_ymax+cellSize)):
	# A tolerance of (1 * cellSize) is added to avoid getting the error for small misalignments
	arcpy.AddError('The polygon layer should be completely contained by the DEM')
	arcpy.AddMessage('fc_xmin={}, dem_xmin={}'.format(fc_xmin,dem_xmin))
	arcpy.AddMessage('fc_xmax={}, dem_max={}'.format(fc_xmax,dem_xmax))
	arcpy.AddMessage('fc_ymin={}, dem_ymin={}'.format(fc_ymin,dem_ymin))
	arcpy.AddMessage('fc_ymax={}, dem_ymax={}'.format(fc_ymax,dem_ymax))

xmin = dem_xmin
while xmin < fc_xmin:
	xmin += cellSize
	
xmax = dem_xmax
while xmax > fc_xmax:
	xmax = xmax - cellSize
	
ymin = dem_ymin
while ymin < fc_ymin:
	ymin += cellSize
	
ymax = dem_ymax
while ymax > fc_ymax:
	ymax = ymax - cellSize

arcpy.env.extent = arcpy.Extent(xmin, ymin, xmax, ymax)
arcpy.env.cellSize = cellSize

for param in par_list:
	out_tiff = os.path.join(workspace,'{}.tif'.format(param))
	if os.path.isfile(out_tiff):
		arcpy.AddWarning('{} already exists and cannot be overwritten'.format(out_tiff))
	else:
		out_ascii = os.path.join(workspace,'{}.asc'.format(param))
		if os.path.isfile(out_ascii):
			arcpy.AddWarning('{} already exists and cannot be overwritten'.format(out_ascii))
		else:
			arcpy.FeatureToRaster_conversion(fc, param, out_tiff, cellSize)
			arcpy.RasterToASCII_conversion(out_tiff, out_ascii)
			if (decimal_separator != ".") or (thousands_separator != ""):
				# Open the ASCII file 
				with open(out_ascii, 'r') as file:
					filedata = file.read()
				
				# Replace the separators
				if (thousands_separator != "") and (thousands_separator != " "):
					filedata = filedata.replace(thousands_separator, '')
				if (decimal_separator != "."):
					filedata = filedata.replace(decimal_separator, '.')
				
				# Write the file out again
				with open(out_ascii, 'w') as file:
					file.write(filedata)
			try:
				if arcpy.GetInstallInfo()['ProductName'] == 'Desktop':
					arcpy.Delete_management(out_tiff)
				else:
					arcpy.management.Delete(out_tiff)
				os.remove(out_ascii + '.xml')
			except:
				arcpy.AddWarning('{} could not be deleted'.format(out_tiff))

out_tiff = os.path.join(workspace,'dem.tif')
if os.path.isfile(out_tiff):
	arcpy.AddWarning('{} already exists and cannot be overwritten'.format(out_tiff))
else:
	out_ascii = os.path.join(workspace,'dem.asc')
	if os.path.isfile(out_ascii):
		arcpy.AddWarning('{} already exists and cannot be overwritten'.format(out_ascii))
	else:
		arcpy.CopyRaster_management(DEM, out_tiff)
		arcpy.RasterToASCII_conversion(out_tiff, out_ascii)
		if (decimal_separator != ".") or (thousands_separator != ""):
			# Open the ASCII file 
			with open(out_ascii, 'r') as file:
				filedata = file.read()
			
			# Replace the separators
			if (thousands_separator != "") and (thousands_separator != " "):
				filedata = filedata.replace(thousands_separator, '')
			if (decimal_separator != "."):
				filedata = filedata.replace(decimal_separator, '.')
			
			# Write the file out again
			with open(out_ascii, 'w') as file:
				file.write(filedata)
		
		try:
			if arcpy.GetInstallInfo()['ProductName'] == 'Desktop':
				arcpy.Delete_management(out_tiff)
			else:
				arcpy.management.Delete(out_tiff)
			os.remove(out_ascii + '.xml')
		except:
			arcpy.AddWarning('{} could not be deleted'.format(out_tiff))
