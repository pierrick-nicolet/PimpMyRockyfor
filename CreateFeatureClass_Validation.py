import arcpy
import os

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
    if self.params[0].value:
      ws = os.path.dirname(self.params[0].value.value)
      fc = os.path.basename(self.params[0].value.value)
      desc = arcpy.Describe(ws)
      if desc.workspaceType == 'LocalDatabase':
        outfc = arcpy.ValidateTableName(fc, ws)
        if outfc != fc:
          self.params[0].setErrorMessage("The feature class name is invalid")
        else:
          if arcpy.Exists(os.path.join(ws,fc)):
            self.params[0].setErrorMessage("The feature class already exists")
          else:
            self.params[0].clearMessage()
      else:
        self.params[0].setErrorMessage("The output must be saved in a local database")
    return

