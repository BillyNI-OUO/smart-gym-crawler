# README

[TOC]

## Installation

請確定你是在 Python3 的環境上運行。若是在預設為 Python2 的環境，可以使用 `pip3`以及`python3`。

```bash
pip install requests
pip install mysql-connector-python
pip install numpy
pip install pandas
```

## Usage

### Grid Search

對一系列的座標範圍進行網格狀搜尋，使用方法如下。先指定搜尋品質，再指定座標範圍檔案。

```bash
python ./parse.py <quality> <filepath>

e.g.
python ./parse.py high ./coordinates/台中.txt
python ./parse.py low ./coordinates/台中.txt
```

- `<quality>`
  - `high`: 用 `grid_search` 方法，會用到 Google Maps API (會花錢，且需要指定 crawler 使用的 APIKEYS)
  - `low`: 用 `grid_search2` 方法，不會用到 Google Maps API (不用花錢)，但搜尋品質較低
- `<filepath>`: 座標範圍檔案位置，檔案內容約略如下。

```
24.43163, 120.63205	24.40154, 120.62046
24.43257, 120.62493	24.41209, 120.61205
24.41756, 120.63892	24.38278, 120.65677
24.40326, 120.62905	24.37082, 120.656
24.38114, 120.65224	24.37887, 120.68382
24.37074, 120.6676	24.36097, 120.70442
24.39764, 120.59318	24.38763, 120.58794
...
```

### 再次搜索

以低品質的 API(不用花錢)的方式，在已知的(存在於 DB `place_info` 中)地點進行 `query_nearby2` 搜尋附近餐廳。

```bash
python ./parse.py again <start_from_id>

e.g.
python ./parse.py again 10000
```

- `<start_from_id>`: 從`place_info`資料表的某個 ID 繼續進行搜索。如指定`100`，則會搜尋 100, 101, 102...。

## Structure

- `crawler.py`: 負責抓取 Google Map 上的資料，可以透過高、低品質的方式抓取。使用高品質的方法時，會需要指定 APIKEYS，也就是要透過 Google Maps API，但要收費!所以盡量使用低品質。
- `data.py`: 負責與 MySQL DB 連線，以及透過`crawler.py`的函式取得 Google Map 資料。
- `parse.py`: 當作 command line 工具使用。

