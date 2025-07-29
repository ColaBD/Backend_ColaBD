class Response_Controller:
  data: any
  status_code: int
  success: bool
   
  def __init__(self, data, status_code, success):
    self.data = data
    self.status_code = status_code
    self.success = success  
    
class Response_Generic:
  data: any
  success: bool
  
  def __init__(self, data, success):
    self.data = data
    self.success = success  