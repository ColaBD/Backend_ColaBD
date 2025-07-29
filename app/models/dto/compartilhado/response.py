class Response:
  def __init__(self, data, status_code=000, success=False):
    self.data = data
    self.status_code = status_code
    self.success = success