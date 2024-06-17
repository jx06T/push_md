import os
from datetime import datetime
import re
import shutil
import subprocess
import MYcurses2
import signal
import api as imgurAPI

class push_md():
    def __init__(self,input_folder_paths0,input_folder_paths,output_folder_path,url):
        self.url = url
        self.input_folders0 = input_folder_paths0
        self.input_folders = input_folder_paths
        self.output_folder0 = output_folder_path
        self.output_folder1 = output_folder_path+"\src\content\posts"

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
                        Mtime = self.check_file_already_exists(file.replace(" ","_"))
                        tags,content = self.getTag(f)
                        categories = file.split("\\")[:-1]
                        if len(categories) == 0:
                            categories.append("")
                        content = self.addtitle(content,title,Mtime,tags,categories)              
                        content = self.image_urls(content,file.replace(" ","_")[:-3],categories)
                        content = self.quote_urls(content)
                        content = self.callout(content)

                        # print(content)
                        output = self.output_folder1+"\\"+self.get_okName_F(file.replace(" ","_"))
                        self.save_content_to_file(content,output)

    def getTag(self,file):
        line = file.readline()
        if line == "---\n":
            return (None,line+file.read())
        tags = line.split("#")
        content = line+"\n"
        if "#" not in line:
            tags = []
        else:
            content = ""
            tags[-1] = tags[-1][0:-1]
            tags = tags[1:]
        content += file.read()
        return (tags,content)

    def getTime(self,file):
        file_path = os.path.join(self.output_folder1, file)
        print(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                pattern = r"published: (\d{4}-\d{2}-\d{2})"
                matches = re.findall(pattern, content)

                print(matches[0])
                return matches[0]
        except:
            return self.get_now_time() 
            
    def check_file_already_exists(self,file):
        files = MYcurses2.getAll_file(self.output_folder1)
        filtered_arr = [i for i in files if i == self.get_okName_F(file)]
        # print(files,file,filtered_arr)
        if len(filtered_arr)>0:
            Mtime = self.getTime(filtered_arr[0])
        else:
            Mtime = self.get_now_time()

        return Mtime

    def addtitle(self,content,title,time,tags,categories):
        print("標記資訊...")
        category = categories[-1]
        if tags is None:
            separator_index = content[4:].find('---')+4
            tags = ""
            metadata = ""
            YAML = content[:separator_index]
            if "title" not in YAML:
                metadata += f"\ntitle: {title}"
            if "published" not in YAML:
                metadata += f"\npublished: {time}"
            if "category" not in YAML:
                metadata += f"\ncategory: {category}"
            metadata += "\n"
        else:
            separator_index = 0
            tags ="[" + ",".join([f"'{tag.strip()}'" for tag in tags]) + "]"
            metadata = f"---\ntitle: {title}\npublished: {time}\ntags: {tags}\ncategory: {category}\n---\n"
        
        # print(f"標題:{title},\n時間:{time},\n標籤:\n{tags},\n分類:\n{category}")
        print(metadata)
        content_with_metadata = content[:separator_index] + metadata + content[separator_index:]
        print("successfully!")
        return content_with_metadata
         
    def get_okName(self,name):
        special_chars = "()[]#!@$%^&*|{}?<>:\"\'\\/"
        pattern = "[" + re.escape("".join(special_chars)) + "]"
        name = re.sub(pattern, "", name)
        return name

    def get_okName_F(self,file_path):
        folder_path, file_name = os.path.split(file_path)
        new_file_name = self.get_okName(file_name)
        new_file_path = os.path.join(folder_path, new_file_name)
        return new_file_path

    def image_urls(self,content,main_name,file_path):
        print("檢查本地資源引用...")
        pattern = r"!\[(.*)\]\((.*(?:C:|D:).*\\(.+\..+))\)"
        
        # eplaced_text = re.sub(pattern, lambda match: f"![{match.group(1)}]({re.escape(os.path.basename(main_name))}__{self.get_okName(match.group(3))})", content)
        eplaced_text = re.sub(pattern, lambda match: f"![{match.group(1)}]({imgurAPI.post_image(match.group(2),match.group(1))})", content)

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
        filtered_arr = [i for i in files if os.path.splitext(os.path.basename(i))[0] == self.get_okName(file1)]
        
        url = self.url
        if len(filtered_arr)>0:
            file1 = filtered_arr[0] 
            # time = self.getTime(file1)
            # url+="/".join(time.split("-"))+"/"
            url += (file1[:-3]).replace("\\","/")

        url = url.lower()
        if url == self.url:
            print("未找到文章!!!!!",file)
        else:
            print("替換",file,"->",url)
        return url

    def callout(self,content):
        print("callout語法統一...")
        pattern = r"\> \[\!(.+)\] (.*)"
        matches = re.finditer(pattern, content)
        ok = ["note","tip","important","warning","caution"]
        new_text = content
        # 打印匹配的文字和它們的索引位置
        for match in matches:
            start_index = match.start()
            # end_index = match.end()
            matched_text = match.group(1).lower()
            title = match.group(2)
            if matched_text not in ok:
                continue
            # print(f"Matched text: {matched_text}, Start index: {start_index}, End index: {end_index}")
            print(f"There is a \"{matched_text}\" ,Start at {start_index}")
            temp_text0 = content[start_index:]
            end_index = temp_text0.find("\n\n")
            temp_text0 = temp_text0[:end_index]

            temp_text = temp_text0.replace("\n> ","<br>\n")
            temp_text = temp_text.replace("\n>","<br>\n")
            temp_text = temp_text[temp_text0.find("\n")+4:]
            temp_text = ":::"+matched_text+"["+title+"]"+temp_text+"\n:::"
            # print(temp_text0)
            # print("--------------------------------------")
            # print(temp_text)
            # print("-------------------------------------------------------")
            new_text = new_text.replace(temp_text0,temp_text)
        # print(new_text)
        return new_text
    def preview(self):
        try:
            # 使用 Popen 启动子进程
            self.process = subprocess.Popen(
                ["npm", "start"], 
                cwd=self.output_folder0, 
                shell=True
            )
            print("Preview started. Press Ctrl+C to stop.")
            self.process.wait()  # 等待子进程完成
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during pull: {e}")
            print(f"Output: {e.output}")
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            print("Stopping preview...")
            self.stop_preview()

    def stop_preview(self):
            if self.process and self.process.poll() is None:  # 检查子进程是否仍在运行
                self.process.send_signal(signal.SIGINT)  # 发送中断信号
                self.process.wait()  # 等待子进程退出
                print("Preview stopped.")

    def updata(self):
        try:
            # 拉取遠程倉庫的最新更改
            subprocess.run(["git", "pull", "origin", "deploy"], cwd=self.output_folder0, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during pull: {e}")
            print(f"Output: {e.output}")
            input("Press Enter to continue...")
            # return  
        try:
            # 添加所有變更，包括未跟踪的文件
            subprocess.run(["git", "add", "."], cwd=self.output_folder0, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during add: {e}")
            print(f"Output: {e.output}")
            input("Press Enter to continue...")
            # return
        try:
            # 提交變更
            subprocess.run(["git", "commit", "-a", "-m", "ddd"], cwd=self.output_folder0, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during commit: {e}")
            print(f"Output: {e.output}")
            input("Press Enter to continue...")
            # return
        try:
            # 推送到遠程倉庫
            subprocess.run(["git", "push", "origin", "deploy"], cwd=self.output_folder0, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during push: {e}")
            print(f"Output: {e.output}")
            input("Press Enter to continue...")
            # return
        print("done!!!!!!!!!!")

    def delete_file(self):
        files = self.input_folders
        for file in files:
            file_path = os.path.join(self.output_folder1, file)
            if os.path.exists(file_path):
                if file.endswith(".md"):
                    a = input(f"刪除{file_path}?(Y/[N])")
                    if not a == "Y":
                        continue
                    os.remove(file_path)
        # self.updata()

# 指定要遍歷的資料夾路徑
input_folder_path = "D:\Document_J\iCloudDrive\iCloud~md~obsidian\jx\GithubPages"
output_folder_path = "D:\Document_J\jx06_blog"
url = "https://jx06blog-jx06ts-projects.vercel.app/posts/"
# output_folder_path = "D:\Document_J\hexo\source\_posts"
if __name__ == "__main__":
    input_folder_paths = MYcurses2.get(input_folder_path)
    T = 0
    if len(input_folder_paths) > 0:
        mdPusher = push_md(input_folder_path,input_folder_paths,output_folder_path,url)
        mdPusher.read_md_files()
        T+=1
        
    a = input("要刪啥嗎?(Y/[N])")
    if a == "Y":
        delete_folder_paths = MYcurses2.get(output_folder_path+"\src\content\posts",1)
        if  len(delete_folder_paths) > 0:
            mdPusher = push_md(input_folder_path,delete_folder_paths,output_folder_path,url)
            mdPusher.delete_file()
            T+=1
    if T>0:
        a = input("要預覽嗎?(Y/[N])")
        if a == "Y":
            mdPusher.preview()

        a = input("要取消提交到github嗎?(Y/[N])")
        if not a == "Y":
            mdPusher.updata()