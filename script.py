import wx
import os
import ctypes
import shutil
import threading
from pathlib import Path

try:
    dll_path = os.path.abspath("libtitle_cleaner.dll")
    lib = ctypes.CDLL(dll_path)
    lib.clean_title.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    DLL_LOADED = True
except:
    DLL_LOADED = False


def fast_clean_title(text):
    if not DLL_LOADED:
        cleaned = text.replace('_', ' ').replace('-', ' ').replace('.', ' ')
        return ' '.join(word.capitalize() for word in cleaned.split() if word)

    input_bytes = text.encode("utf-8")
    output = ctypes.create_string_buffer(512)
    lib.clean_title(input_bytes, output)
    cleaned = output.value.decode("utf-8").strip()
    return ' '.join(word.capitalize() for word in cleaned.split())


class VideoSorterFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Video Sorter Pro", size=(500, 400))
        self.SetMinSize((480, 380))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(40, 40, 40))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(20)

        title = wx.StaticText(panel, label="Video Sorter Pro")
        title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        main_sizer.Add(title, flag=wx.CENTER | wx.ALL, border=10)

        folder_box = wx.StaticBox(panel, label="Selected Folder")
        folder_box.SetForegroundColour(wx.Colour(255, 255, 255))
        folder_sizer = wx.StaticBoxSizer(folder_box, wx.VERTICAL)

        self.folder_label = wx.StaticText(panel, label="No folder selected")
        self.folder_label.SetForegroundColour(wx.Colour(255, 255, 255))
        folder_sizer.Add(self.folder_label, flag=wx.ALL | wx.EXPAND, border=10)

        self.select_btn = wx.Button(panel, label="Select Folder", size=(120, 35))
        self.select_btn.SetBackgroundColour(wx.Colour(60, 120, 200))
        self.select_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.select_btn.Bind(wx.EVT_BUTTON, self.on_select_folder)
        folder_sizer.Add(self.select_btn, flag=wx.ALL | wx.CENTER, border=10)

        main_sizer.Add(folder_sizer, flag=wx.ALL | wx.EXPAND, border=15)

        status_box = wx.StaticBox(panel, label="Status")
        status_box.SetForegroundColour(wx.Colour(255, 255, 255))
        status_sizer = wx.StaticBoxSizer(status_box, wx.VERTICAL)

        self.status_label = wx.StaticText(panel, label="Ready to sort videos")
        self.status_label.SetForegroundColour(wx.Colour(255, 255, 255))
        status_sizer.Add(self.status_label, flag=wx.ALL, border=10)

        self.progress_bar = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        self.progress_bar.SetValue(0)
        status_sizer.Add(self.progress_bar, flag=wx.ALL | wx.EXPAND, border=10)

        main_sizer.Add(status_sizer, flag=wx.ALL | wx.EXPAND, border=15)

        stats_box = wx.StaticBox(panel, label="Statistics")
        stats_box.SetForegroundColour(wx.Colour(255, 255, 255))
        stats_sizer = wx.StaticBoxSizer(stats_box, wx.HORIZONTAL)

        self.videos_label = wx.StaticText(panel, label="Videos: 0")
        self.videos_label.SetForegroundColour(wx.Colour(255, 255, 255))
        stats_sizer.Add(self.videos_label, flag=wx.ALL, border=10)

        stats_sizer.AddStretchSpacer()

        self.folders_label = wx.StaticText(panel, label="Folders: 0")
        self.folders_label.SetForegroundColour(wx.Colour(255, 255, 255))
        stats_sizer.Add(self.folders_label, flag=wx.ALL, border=10)

        main_sizer.Add(stats_sizer, flag=wx.ALL | wx.EXPAND, border=15)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.preview_btn = wx.Button(panel, label="Preview", size=(100, 35))
        self.preview_btn.SetBackgroundColour(wx.Colour(150, 100, 200))
        self.preview_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.preview_btn.Enable(False)
        self.preview_btn.Bind(wx.EVT_BUTTON, self.on_preview)
        button_sizer.Add(self.preview_btn, flag=wx.ALL, border=10)

        button_sizer.AddStretchSpacer()

        self.sort_btn = wx.Button(panel, label="Sort Videos", size=(100, 35))
        self.sort_btn.SetBackgroundColour(wx.Colour(100, 180, 100))
        self.sort_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.sort_btn.Enable(False)
        self.sort_btn.Bind(wx.EVT_BUTTON, self.on_sort_videos)
        button_sizer.Add(self.sort_btn, flag=wx.ALL, border=10)

        main_sizer.Add(button_sizer, flag=wx.ALL | wx.EXPAND, border=15)

        dll_status = "DLL Loaded" if DLL_LOADED else "DLL Not Found"
        footer = wx.StaticText(panel, label=f"{dll_status} | Video Sorter Pro v2.1")
        footer.SetForegroundColour(wx.Colour(180, 180, 180))
        footer_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        footer.SetFont(footer_font)
        main_sizer.Add(footer, flag=wx.CENTER | wx.ALL, border=15)

        panel.SetSizer(main_sizer)

        self.selected_folder = None
        self.video_files = []
        self.sorting_thread = None

        self.Center()

    def on_select_folder(self, event):
        dlg = wx.DirDialog(self, "Choose a folder containing videos")
        if dlg.ShowModal() == wx.ID_OK:
            self.selected_folder = dlg.GetPath()

            display_path = self.selected_folder
            if len(display_path) > 50:
                display_path = "..." + display_path[-47:]

            self.folder_label.SetLabel(display_path)
            self.scan_folder()

            if self.video_files:
                self.auto_sort_videos()
        dlg.Destroy()

    def scan_folder(self):
        if not self.selected_folder:
            return

        self.status_label.SetLabel("Scanning folder...")
        self.progress_bar.SetValue(0)

        self.video_files = []
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}

        for entry in os.scandir(self.selected_folder):
            if entry.is_file():
                ext = Path(entry.name).suffix.lower()
                if ext in video_extensions:
                    self.video_files.append(entry)

        titles = set()
        for video in self.video_files:
            title = fast_clean_title(video.name)
            if title:
                titles.add(title)

        self.videos_label.SetLabel(f"Videos: {len(self.video_files)}")
        self.folders_label.SetLabel(f"Folders: {len(titles)}")

        if self.video_files:
            self.status_label.SetLabel(f"Found {len(self.video_files)} video files")
            self.sort_btn.Enable(True)
            self.preview_btn.Enable(True)
        else:
            self.status_label.SetLabel("No video files found")
            self.sort_btn.Enable(False)
            self.preview_btn.Enable(False)

    def auto_sort_videos(self):
        confirm_dlg = wx.MessageDialog(
            self,
            f"Sort {len(self.video_files)} videos into folders?",
            "Confirm",
            wx.YES_NO | wx.ICON_QUESTION
        )

        if confirm_dlg.ShowModal() == wx.ID_YES:
            self.start_sorting()
        confirm_dlg.Destroy()

    def on_preview(self, event):
        if not self.video_files:
            return

        preview_dlg = wx.Dialog(self, title="Preview", size=(600, 400))
        preview_dlg.SetBackgroundColour(wx.Colour(40, 40, 40))

        sizer = wx.BoxSizer(wx.VERTICAL)

        preview_text = ""
        for i, video in enumerate(self.video_files[:15]):
            title_name = fast_clean_title(video.name)
            if not title_name:
                title_name = "Unknown"
            preview_text += f"'{video.name}' -> '{title_name}'\n"

        if len(self.video_files) > 15:
            preview_text += f"\n... and {len(self.video_files) - 15} more files"

        text_ctrl = wx.TextCtrl(preview_dlg, value=preview_text,
                                style=wx.TE_MULTILINE | wx.TE_READONLY)
        text_ctrl.SetBackgroundColour(wx.Colour(50, 50, 50))
        text_ctrl.SetForegroundColour(wx.Colour(255, 255, 255))
        sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, border=15)

        close_btn = wx.Button(preview_dlg, wx.ID_OK, "Close")
        close_btn.SetBackgroundColour(wx.Colour(100, 100, 100))
        close_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        sizer.Add(close_btn, flag=wx.ALL | wx.CENTER, border=15)

        preview_dlg.SetSizer(sizer)
        preview_dlg.ShowModal()
        preview_dlg.Destroy()

    def on_sort_videos(self, event):
        if not self.video_files:
            return

        confirm_dlg = wx.MessageDialog(
            self,
            f"Sort {len(self.video_files)} videos into folders?",
            "Confirm",
            wx.YES_NO | wx.ICON_QUESTION
        )

        if confirm_dlg.ShowModal() == wx.ID_YES:
            self.start_sorting()
        confirm_dlg.Destroy()

    def start_sorting(self):
        self.select_btn.Enable(False)
        self.sort_btn.Enable(False)
        self.preview_btn.Enable(False)

        self.sorting_thread = threading.Thread(target=self.sort_videos_thread)
        self.sorting_thread.start()

    def sort_videos_thread(self):
        total_files = len(self.video_files)
        moved_count = 0

        for i, video in enumerate(self.video_files):
            progress = int((i / total_files) * 100)
            wx.CallAfter(self.update_progress, progress, f"Processing: {video.name}")

            title = fast_clean_title(video.name)
            if not title:
                title = "Unknown"

            dest_folder = os.path.join(self.selected_folder, title)

            try:
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)

                source_path = video.path
                dest_path = os.path.join(dest_folder, video.name)

                if os.path.dirname(source_path) != dest_folder:
                    shutil.move(source_path, dest_path)
                    moved_count += 1

            except Exception as e:
                wx.CallAfter(self.show_error, f"Error moving {video.name}: {str(e)}")

        wx.CallAfter(self.sorting_complete, moved_count)

    def update_progress(self, value, status):
        self.progress_bar.SetValue(value)
        self.status_label.SetLabel(status)

    def sorting_complete(self, moved_count):
        self.progress_bar.SetValue(100)
        self.status_label.SetLabel(f"Complete! Moved {moved_count} videos")

        self.select_btn.Enable(True)
        self.sort_btn.Enable(True)
        self.preview_btn.Enable(True)

        success_dlg = wx.MessageDialog(
            self,
            f"Successfully sorted {moved_count} videos!",
            "Complete",
            wx.OK | wx.ICON_INFORMATION
        )
        success_dlg.ShowModal()
        success_dlg.Destroy()

        self.scan_folder()

    def show_error(self, message):
        dlg = wx.MessageDialog(self, message, "Error", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()


class VideoSorterApp(wx.App):
    def OnInit(self):
        frame = VideoSorterFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = VideoSorterApp()
    app.MainLoop()