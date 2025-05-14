# 圖片旋轉專案

這個專案使用 Python 程式碼 (rotate.py) 來旋轉圖片。

## 專案結構

-   [`rotate.py`](rotate.py): 主要的 Python 程式碼檔案。
-   `assets/`: 包含旋轉前的圖片。
-   `rotated_images/`: 包含旋轉後的圖片。

## 建構 Python 執行環境

1.  **安裝 Python：**
    -   前往 Python 官網 ([https://www.python.org/downloads/](https://www.python.org/downloads/)) 下載並安裝適合您作業系統的 Python 版本。
    -   在安裝過程中，請務必勾選 "Add Python to PATH" 選項，以便在命令列中直接使用 `python` 指令。
2.  **建立虛擬環境 (venv)：**
    -   開啟命令列，並導航至專案目錄。
    -   執行以下指令來建立虛擬環境：

    ```bash
    python -m venv venv
    ```

    -   啟動虛擬環境：

        -   **Windows：**

        ```bash
        venv\Scripts\activate
        ```

        -   **macOS/Linux：**

        ```bash
        source venv/bin/activate
        ```
3.  **安裝必要的函式庫：**
    -   使用 `pip` 指令來安裝專案所需的函式庫。
    -   確認虛擬環境已啟動，並執行以下指令：

    ```bash
    pip install -r requirements.txt
    ```

## 使用方法

1.  確認已安裝 Python 及必要的函式庫。
2.  執行 [`rotate.py`](rotate.py) 程式碼。
3.  旋轉後的圖片將儲存在 `rotated_images/` 目錄中。

## 範例

```python
python rotate.py
```

## 注意事項

-   請確保已安裝所有必要的 Python 函式庫。
-   建議使用虛擬環境來管理專案的相依性。