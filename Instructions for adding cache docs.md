# Instructions for Adding Remote Cache Documents

This document outlines the steps required to enable the `Document Scanner` module to load documents from a remote cache (e.g., a web server).

---

## **1. Identify Remote Documents**
- Update the document configuration to include a flag or URL field indicating that the document is stored remotely.
- Example configuration:
  ```json
  {
      "file_path": "https://example.com/documents/file.csv",
      "is_remote": true,
      "file_name": "file.csv",
      "header_row": 0,
      "search_columns": ["Column1"],
      "return_columns": ["Column2"]
  }
  ```

---

## **2. Modify the `_load` Method in `SearchableDocument`**

### **Step 1: Detect Remote Documents**
- Check if the `is_remote` flag is set in the document configuration.
- If `is_remote` is `True`, treat the `file_path` as a URL.

### **Step 2: Download the Remote File**
- Use the `requests` library to download the file to a temporary location.
- Example code:
  ```python
  import requests
  from tempfile import NamedTemporaryFile

  if self.config.get("is_remote", False):
      response = requests.get(self.file_path, stream=True)
      if response.status_code == 200:
          with NamedTemporaryFile(delete=False, suffix=self.file_path.suffix) as temp_file:
              for chunk in response.iter_content(chunk_size=8192):
                  temp_file.write(chunk)
              self.file_path = Path(temp_file.name)
      else:
          self.load_error = f"Failed to download file: {response.status_code}"
          return
  ```

### **Step 3: Load the File**
- After downloading, load the file into memory using the existing logic for `.csv` or `.xlsx` files.
- Example:
  ```python
  if self.file_path.suffix.lower() in ['.xlsx', '.xls']:
      self.df = pd.read_excel(self.file_path, header=self.header_row)
  else:
      self.df = pd.read_csv(self.file_path, header=self.header_row)
  ```

### **Step 4: Handle Errors**
- Add error handling for network issues, invalid URLs, and failed downloads.
- Example:
  ```python
  if not self.file_path.exists():
      self.load_error = "File not found"
      return
  ```

---

## **3. Update Configuration Management**
- Ensure the `DocumentScannerConfig` class supports saving and loading remote document configurations.
- Example:
  ```python
  {
      "file_path": "https://example.com/documents/file.csv",
      "is_remote": true
  }
  ```

---

## **4. Workflow for Remote Documents**
1. **Configuration**:
   - The document configuration includes a `file_path` (URL) and `is_remote: True`.

2. **Loading**:
   - The `_load` method detects remote documents and downloads them to a temporary file.
   - The temporary file is then loaded into memory.

3. **Error Handling**:
   - If the download fails, an error message is logged, and the `load_error` attribute is set.

4. **Cleanup**:
   - Temporary files are deleted after use.

---

## **5. Considerations**

### **Caching**
- To avoid repeated downloads, consider caching remote files locally and checking for updates using HTTP headers (e.g., `ETag` or `Last-Modified`).

### **Security**
- Validate URLs to prevent malicious downloads.
- Use HTTPS to ensure secure communication.

### **Timeouts**
- Set timeouts for network requests to avoid hanging.
- Example:
  ```python
  response = requests.get(self.file_path, stream=True, timeout=10)
  ```

---

## **6. Testing**
- Test the implementation with various scenarios:
  - Valid and invalid URLs.
  - Large files.
  - Slow network connections.
  - Files with different formats (e.g., `.csv`, `.xlsx`).

---

By following these steps, the `Document Scanner` module can be extended to support loading documents from a remote cache efficiently and securely.