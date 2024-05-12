import os
import urwid
import pyperclip

class SettingsCheckBox(urwid.CheckBox):
    def __init__(self, label, callback,state=False):
        super().__init__(label, state=state)
        urwid.connect_signal(self, 'change', callback)

class SettingsWidget(urwid.ListBox):
    def __init__(self,dir_path,typee = 0):
        self.dir_path = dir_path
        self.selected = []
        optionsText = getAll_file(dir_path)
        options = [
            SettingsCheckBox(T,self.on_state_change) for T in optionsText
        ]
        options_pile = urwid.Pile(options)

        button_inst = urwid.Button("OK")
        # urwid.connect_signal(button_inst, "click", self.return_to_previous, "Exit")
        urwid.connect_signal(button_inst, "click", self.return_to_previous, user_args=["Exit"])

        div = urwid.Divider()

        pile = urwid.Pile([options_pile, div, button_inst])
        body = [urwid.Text("更新啥" if typee == 0 else "刪除啥"), urwid.Divider(), pile]
        super().__init__(urwid.SimpleListWalker(body))

    def keypress(self, size, key):
        if key == 'p':
            self.return_to_previous(None, "Exit")
        else:
            return super().keypress(size, key)

   

    def on_state_change(self, checkbox, state):
        if state:
            self.selected.append(checkbox.label)
        else:
            self.selected.remove(checkbox.label)

    def return_to_previous(self, button,b):
        # print("選擇了",self.selected)
        raise urwid.ExitMainLoop()
    
def getAll_file(dir_path):
        clipboard_content = pyperclip.paste()
        # print("剪貼簿內容：", clipboard_content)
        files_dict = {}
        now_file = None
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 獲取檔案的最後修改時間
                edit_time = os.path.getmtime(file_path)
                # 將檔案路徑和對應的修改時間存入字典中
                relative_path = os.path.relpath(file_path, dir_path)
                files_dict[relative_path] = edit_time
                if clipboard_content.replace(" ","_") in  os.path.basename(relative_path) or clipboard_content in  os.path.basename(relative_path):
                    now_file = relative_path
        sorted_files = sorted(files_dict, key=files_dict.get, reverse=True)
        if now_file is not None:
            sorted_files.insert(0,now_file)
        return sorted_files

def get(path,t = 0):
    settings_widget = SettingsWidget(path,t)
    urwid.MainLoop(settings_widget).run()
    return settings_widget.selected

if __name__ == "__main__":
    settings_widget = SettingsWidget("D:\Document_J\Obsidian\my\GithubPages")
    # settings_widget = SettingsWidget("D:\Document_J\code\py\dcBot")
    a = urwid.MainLoop(settings_widget).run()
    print(settings_widget.selected)
    input()
