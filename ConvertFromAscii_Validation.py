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
      # Check if the output folder is a database
      desc = arcpy.Describe(self.params[1].value)
      if desc.workspaceType == 'LocalDatabase':
        self.params[2].enabled = 0
        self.params[2].value = ''
      else:
        self.params[2].enabled = 1
        self.params[2].parameterType = 'Required'
        lst=['TIFF', 'CRF', 'ERDAS IMAGINE','Esri Grid']
        self.params[2].filter.list=lst
        if self.params[2].value is None:
          self.params[2].value = 'TIFF'
    else:
      self.params[2].enabled = 0
      self.params[2].value = ''
    return


