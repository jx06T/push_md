# push_md
下載專案後進到目錄執行:
```
pip install urwid pyperclip
```
## FOR HEXO

安裝依賴後

配置 **push_md_HEXO.py** 中的下面兩行：
```
input_folder_path = "D:\Document_J\Obsidian\my\GithubPages"
output_folder_path = "D:\Document_J\hexo\\"
```
為
```
input_folder_path = "<path_to_your_obsidian folder>"
output_folder_path = "<path_to_your_hexo project folder"
```
並確認你的 **hexo project folder** 具有以下資料夾：

`source\\_posts`

`source\\img`
---
## FOR Astro

安裝依賴後

配置 **push_md_Astro.py** 中的下面兩行：
```
input_folder_path = "D:\Document_J\Obsidian\my\GithubPages"
output_folder_path = "D:\Document_J\hexo\\"
```
為
```
input_folder_path = "<path_to_your_obsidian folder>"
output_folder_path = "<path_to_your_hexo project folder"
```
並確認你的 **hexo project folder** 具有以下資料夾：

`source\\_posts`

`source\\img`