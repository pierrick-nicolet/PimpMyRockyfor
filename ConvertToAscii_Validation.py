import arcpy
class ToolValidator(object):
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup arcpy and the list of tool parameters."""
    self.params = arcpy.GetParameterInfo()

  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parameter
    has been changed."""
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    if self.params[1].value:
      self.params[3].enabled = True
      DEM = self.params[1].value
      desc = arcpy.Describe(DEM)
      res = desc.meanCellWidth
      lst = ['{} m'.format(res)]
      for i in range(2,11):
        lst.append('{} m'.format(res*i))

      self.params[3].filter.list=lst
    else:
      self.params[3].filter.list=[]
      self.params[3].value = ''
      self.params[3].enabled = False
    return







