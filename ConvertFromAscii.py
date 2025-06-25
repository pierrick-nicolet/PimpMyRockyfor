# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ConvertFromAscii.py
# Created on: 23.06.2021
# by: Pierrick.Nicolet@ngu.no
#  ---------------------------------------------------------------------------
#
# This tool converts all the ascii files in the source folder (folder with the
# outputs of RockyFor3D) to another raster format and defines their projection.
#
# Reference:
#
# https://www.ecorisq.org/ecorisq-tools
#
# ---------------------------------------------------------------------------

# Import arcpy modules
import arcpy
import os

if __name__=="__main__":

	# Retrive the parameters from the GUI
	ASCIIFolder = arcpy.GetParameterAsText(0)
	OutputFolder = arcpy.GetParameterAsText(1)
	OutputFormat = arcpy.GetParameterAsText(2) #TIFF, CRF, ERDAS IMAGINE,Esri Grid
	src = arcpy.GetParameterAsText(3)
	
	file_list=os.listdir(ASCIIFolder)
	file_list = [x for x in file_list if x[-4:].lower()=='.asc']
	
	# Check if the output folder is a database
	desc = arcpy.Describe(OutputFolder)
	if desc.workspaceType == 'LocalDatabase':
		ext = ""
	else:
		if OutputFormat == "TIFF":
			ext= ".tif"
		elif OutputFormat == "CRF":
			ext= ".crf"
		elif OutputFormat == "ERDAS IMAGINE":
			ext= ".img"
		elif OutputFormat == "Esri Grid":
			ext= ""
	
	for file in file_list:
		in_file = os.path.join(ASCIIFolder,file)
		new_name = file[:-4] + ext
		out_file = os.path.join(OutputFolder,new_name)
		if file[:3] == "Nr_":
			rasterType = "INTEGER"
		else:
			rasterType = "FLOAT"
	
		if arcpy.GetInstallInfo()['ProductName'] == 'Desktop':
			arcpy.ASCIIToRaster_conversion (in_file, out_file, rasterType)
		else:
			arcpy.ASCIIToRaster_conversion(in_file, out_file, rasterType)
		
		if len(src) > 0:
			arcpy.DefineProjection_management(out_file, src)
