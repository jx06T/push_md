import os
from datetime import datetime
import re
import shutil
import subprocess
import MYcurses2

class push_md():
    def __init__(self,input_folder_paths0,input_folder_paths,output_folder_path,url):
        self.url = url
        self.input_folders0 = input_folder_paths0
        self.input_folders = input_folder_paths
        self.output_folder0 = output_folder_path
        self.output_folder1 = output_folder_path+"source\\_posts"
        self.output_folder2 = output_folder_path+"source\\img"

    def save_content_to_file(self,content, file_path):
        try:
            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"檔案已儲存至 '{file_path}'")
        except Exception as e:
            print(f"儲存檔案時發生錯誤：{e}")

    def get_now_time(self):
        now = datetime.now()
        time_str = now.strftime('%Y-%m-%d %H:%M:%S')
        return time_str

    def read_md_files(self):
        directory = self.input_folders   
        for file in directory:
            file_path = os.path.join(self.input_folders0, file)
            if os.path.exists(file_path):
                if file.endswith(".md"):
                    print("-----------------------------")
                    print("處理...",file_path)
                    with open(file_path, "r", encoding="utf-8") as f:
                        title = file.split("\\")[-1][:-3]
                        Mtime = self.check_N_O(file.replace(" ","_"))
                        tags,content = self.getTag(f)
                        categories = file.split("\\")[:-1]

                        content = self.addtitle(content,title,Mtime,tags,categories)              
                        content = self.image_urls(content,file.replace(" ","_")[:-3])
                        content = self.quote_urls(content)

                        # print(content)
                        output = self.output_folder1+"\\"+file.replace(" ","_")
                        self.save_content_to_file(content,output)

    def getTag(self,file):
        line = file.readline()
        if line == "---\n":
            return (None,line+file.read())
        tags = line.split("#")
        content = line+"\n"
        if "#" not in line:
            tags = ["","no"]
        else:
            content = ""
        content += file.read()
        return (tags,content)

    def getTime(self,file):
        file_path = os.path.join(self.output_folder1, file)
        print(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                pattern = r"date: (\d{4}-\d{2}-\d{2})"
                matches = re.findall(pattern, content)

                print(matches[0])
                return matches[0]
        except:
            return self.get_now_time() 
            
    def check_N_O(self,file):
        files = MYcurses2.getAll_file(self.output_folder1)
        filtered_arr = [i for i in files if i == file]
        print(files,file,filtered_arr)
        if len(filtered_arr)>0:
            Mtime = self.getTime(filtered_arr[0])
        else:
            Mtime = self.get_now_time()

        return Mtime

    def addtitle(self,content,title,time,tags,categories):
        print("標記資訊...")

        categories.insert(0,"")
        categories ="\n   - ".join(categories) 
        if tags is None:
            separator_index = content[4:].find('---')+4
            tags = "no"
            metadata = ""
            YAML = content[:separator_index]
            if "title" not in YAML:
                metadata += f"\ntitle: {title}"
            if "date" not in YAML:
                metadata += f"\ndate: {time}"
            if "categories" not in YAML:
                metadata += f"\ncategories:{categories}"
            metadata += "\n"
        else:
            separator_index = 0
            tags ="\n   - ".join(tags) 
            metadata = f"---\ntitle: {title}\ndate: {time}\ntags:{tags}\ncategories:{categories}\n---\n"
        
        # print(f"標題:{title},\n時間:{time},\n標籤:\n{tags},\n分類:\n{categories}")
        print(metadata)
        content_with_metadata = content[:separator_index] + metadata + content[separator_index:]
        print("successfully!")
        return content_with_metadata
    
    def image_urls(self,content,main_name):
        print("檢查本地資源引用...")
        pattern = r"!\[(.*)\]\((.*(?:C:|D:).*\\(.+\..+))\)"
        matches = re.findall(pattern, content)
        eplaced_text = re.sub(pattern, r"![\1](../img/"+re.escape(main_name)+r"__\3)", content)

        for i in matches:
            source_file = i[1]
            destination_file = self.output_folder2+"\\"+main_name+"__"+i[2]
            print("替換",source_file,"->",destination_file)
            shutil.copyfile(source_file, destination_file)

        print("successfully!")
        return eplaced_text

    def quote_urls(self,content):
        print("檢查本地文章引用...")
        pattern = r"\[\[(.+)\]\]"
        # matches = re.findall(pattern, content)
        allfiles = MYcurses2.getAll_file(self.output_folder1)
        replaced_text = re.sub(pattern, lambda match: f"[{match.group(1)}]("+self.get_quoteURL(match.group(1), allfiles)+r")", content)
        print("successfully!")
        return replaced_text

        
        
    def get_quoteURL(self,file,files):
        file1 = file.replace(" ","_")
        filtered_arr = [i for i in files if os.path.splitext(os.path.basename(i))[0] == file1]
        
        url = self.url
        if len(filtered_arr)>0:
            file1 = filtered_arr[0] 
            time = self.getTime(file1)
            url+="/".join(time.split("-"))+"/"
            url += (file1[:-3]).replace("\\","/")

        if url == self.url:
            print("未找到文章!!!!!",file)
        else:
            print("替換",file,"->",url)
        return url

    def updata(self):
        # 执行命令 hexo cl，在指定的文件夹中执行
        subprocess.run(["hexo", "cl"], cwd= self.output_folder0, shell=True, check=True)
        # 执行命令 hexo g，在指定的文件夹中执行
        subprocess.run(["hexo", "g"], cwd= self.output_folder0, shell=True, check=True)
        # 执行命令 hexo d，在指定的文件夹中执行
        subprocess.run(["hexo", "d"], cwd= self.output_folder0, shell=True, check=True)
        print("done!!!!!!!!!!")

    def delete_file(self):
        files = self.input_folders
        for file in files:
            file_path = os.path.join(self.output_folder1, file)
            if os.path.exists(file_path):
                if file.endswith(".md"):
                    a = input(f"刪除{file_path}?(Y/N)")
                    if not a == "Y":
                        continue
                    os.remove(file_path)
                    
        # self.updata()

# 指定要遍歷的資料夾路徑
input_folder_path = "D:\Document_J\Obsidian\my\GithubPages"
output_folder_path = "D:\Document_J\hexo2\\"
url = "https://jx06t.github.io/"
# output_folder_path = "D:\Document_J\hexo\source\_posts"
if __name__ == "__main__":
    input_folder_paths = MYcurses2.get(input_folder_path)
    T = 0
    if len(input_folder_paths) > 0:
        mdPusher = push_md(input_folder_path,input_folder_paths,output_folder_path,url)
        mdPusher.read_md_files()
        T+=1
        
    a = input("要刪啥嗎?(Y/N)")
    if a == "Y":
        delete_folder_paths = MYcurses2.get(output_folder_path+"source\\_posts",1)
        if  len(delete_folder_paths) > 0:
            mdPusher = push_md(input_folder_path,delete_folder_paths,output_folder_path,url)
            mdPusher.delete_file()
            T+=1
    if T>0:
        mdPusher.updata()