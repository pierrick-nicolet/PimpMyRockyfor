# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# CreateFeatureClass.py
# Created on: 04.05.2021
# by: Pierrick.Nicolet@ngu.no
#  ---------------------------------------------------------------------------
#
# This tool creates a feature class with the parameters needed for RockyFor3D.
# It needs to be saved in a local database in order to use drop-down lists.
# It is recommanded to create a polygon covering the DEM area and to cut this 
# polygon using the "cut polygons" tool. It is recommanded, but not necessary,
# to use the same projection for the feature class than the one of the DEM. The
# projection of the DEM will be used when the grids are converted to ascii.
#
# Reference:
#
# https://www.ecorisq.org/ecorisq-tools
#
# ---------------------------------------------------------------------------

# Import arcpy modules
import arcpy
import os

# Retrive the parameters from the GUI
# Output feature class
fc_full = arcpy.GetParameterAsText(0)
#Output Coordinate System
out_sr = arcpy.GetParameterAsText(1)
#Forest type
forest = arcpy.GetParameterAsText(2)
#DEM for polygon definition (optional)
dem = arcpy.GetParameterAsText(3)

workspace = os.path.dirname(fc_full)
fc = os.path.basename(fc_full)

arcpy.env.workspace = workspace

if arcpy.GetInstallInfo()['ProductName'] == 'Desktop':
	arcpy.CreateFeatureclass_management(workspace, fc, "POLYGON", "", "", "", out_sr)
else:
	arcpy.management.CreateFeatureclass(workspace, fc, "POLYGON", "", "", "", out_sr)



# Create domains
domBlshape = "Block_Shape"
domSoiltype = "Soil_type"

domains = arcpy.da.ListDomains(workspace)

domExists = False
for domain in domains:
	if domain.name == domBlshape:
		domExists = True
if domExists:
	pass
else:
	arcpy.CreateDomain_management(workspace, domBlshape, "", "SHORT", "CODED")
	domDict = {0:"No block form", 1:"Rectangular block", 2:"Ellipsoidal block",
			 3:"Spherical block", 4:"Disc shaped block"}
	for code in domDict:
		arcpy.AddCodedValueToDomain_management(workspace, domBlshape, code, domDict[code])

domExists = False
for domain in domains:
	if domain.name == domSoiltype:
		domExists = True
if domExists:
	pass
else:
	arcpy.CreateDomain_management(workspace, domSoiltype, "", "SHORT", "CODED")
	domDict = {0:"River, swamp", 1:"Fine soil material (>1m)", 2:"Fine soil material (<1m), sand/gravel",
			3:"Scree, medium compact soil with small rock fragments, forest road",
			4:"Talus slope, compact soil with large rock fragments, forest road",
			5:"Bedrock with thin weathered material or soil cover",
			6:"Bedrock",7:"Asphalt road"}
	for code in domDict:
		arcpy.AddCodedValueToDomain_management(workspace, domSoiltype, code, domDict[code])
		
arcpy.management.AddField(fc, "rockdensity", "SHORT", "", "", "", "Rock density [kg/m3]", "", "", "")
arcpy.management.AddField(fc, "d1", "DOUBLE", "", "", "", "d1: Block height [m]", "", "", "")
arcpy.management.AddField(fc, "d2", "DOUBLE", "", "", "", "d2: Block width [m]", "", "", "")
arcpy.management.AddField(fc, "d3", "DOUBLE", "", "", "", "d3: Block length [m]", "", "", "")
arcpy.management.AddField(fc, "blshape", "SHORT", "", "", "", "Block shape", "", "", domBlshape)
arcpy.management.AssignDefaultToField(fc, "blshape", 0)
arcpy.management.AddField(fc, "rg70", "DOUBLE", "", "", "", "Rg70 [m]", "", "", "")
arcpy.management.AddField(fc, "rg20", "DOUBLE", "", "", "", "Rg20 [m]", "", "", "")
arcpy.management.AddField(fc, "rg10", "DOUBLE", "", "", "", "Rg10 [m]", "", "", "")
arcpy.management.AddField(fc, "soiltype", "SHORT", "", "", "", "Soil type", "", "", domSoiltype)
if forest == 'Raster maps':
	arcpy.management.AddField(fc, "nrtrees", "DOUBLE", "", "", "", "nr trees", "", "", "")
	arcpy.management.AddField(fc, "dbhmean", "DOUBLE", "", "", "", "DBH mean [cm]", "", "", "")
	arcpy.management.AddField(fc, "dbhstd", "DOUBLE", "", "", "", "DBH std [cm]", "", "", "")
if forest == 'Raster maps' or forest == 'Tree file':
	arcpy.management.AddField(fc, "conif_percent", "DOUBLE", "", "", "", "Conif percent", "", "", "")

if dem:
	dem = arcpy.Raster(dem)
	dem_path = dem.catalogPath
	dem_desc = arcpy.Describe(dem_path)
	dem_extent = dem_desc.extent
	
	src_dem = dem_desc.extent.spatialReference.name
	
	pt_ll = arcpy.PointGeometry(arcpy.Point(dem_extent.XMin,dem_extent.YMin),dem_extent.spatialReference).projectAs(out_sr).centroid
	pt_ul = arcpy.PointGeometry(arcpy.Point(dem_extent.XMin,dem_extent.YMax),dem_extent.spatialReference).projectAs(out_sr).centroid
	pt_ur = arcpy.PointGeometry(arcpy.Point(dem_extent.XMax,dem_extent.YMax),dem_extent.spatialReference).projectAs(out_sr).centroid
	pt_lr = arcpy.PointGeometry(arcpy.Point(dem_extent.XMax,dem_extent.YMin),dem_extent.spatialReference).projectAs(out_sr).centroid
	
	array = arcpy.Array([pt_ll, pt_ul, pt_ur, pt_lr,pt_ll])
	
	cursor = arcpy.da.InsertCursor(os.path.join(workspace, fc), ['SHAPE@'])
	cursor.insertRow([arcpy.Polygon(array)])

	del cursor

if arcpy.GetInstallInfo()['ProductName'] == 'Desktop':
	try:
		mxd = arcpy.mapping.MapDocument("CURRENT")
		dataFrame = arcpy.mapping.ListDataFrames(mxd, "*")[0]
		
		arcpy.MakeFeatureLayer_management(os.path.join(workspace,fc), fc)
		layer = arcpy.mapping.Layer(fc)
		arcpy.mapping.AddLayer(dataFrame, layer, "AUTO_ARRANGE")
		
	except:
		str_message = 'The feature class has been saved but could not be added to the current project'
		arcpy.AddMessage(str_message)
else:
	try:
		mxd = arcpy.mp.ArcGISProject("CURRENT")
		dataFrame = mxd.listMaps("*")[0]
		dataFrame.addDataFromPath(os.path.join(workspace,fc))
	except:
		str_message = 'The feature class has been saved but could not be added to the current project'
		arcpy.AddMessage(str_message)

