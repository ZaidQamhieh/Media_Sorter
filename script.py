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


class MediaSorterFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Media Sorter Pro", size=(550, 600))
        self.SetMinSize((530, 550))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(40, 40, 40))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(20)

        title = wx.StaticText(panel, label="Media Sorter Pro")
        title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        main_sizer.Add(title, flag=wx.CENTER | wx.ALL, border=10)

        # File type selection
        type_box = wx.StaticBox(panel, label="File Types to Sort")
        type_box.SetForegroundColour(wx.Colour(255, 255, 255))
        type_sizer = wx.StaticBoxSizer(type_box, wx.HORIZONTAL)

        self.video_cb = wx.CheckBox(panel, label="Videos")
        self.video_cb.SetValue(True)
        self.video_cb.SetForegroundColour(wx.Colour(255, 255, 255))
        type_sizer.Add(self.video_cb, flag=wx.ALL, border=10)

        self.image_cb = wx.CheckBox(panel, label="Images")
        self.image_cb.SetValue(True)
        self.image_cb.SetForegroundColour(wx.Colour(255, 255, 255))
        type_sizer.Add(self.image_cb, flag=wx.ALL, border=10)

        self.pdf_cb = wx.CheckBox(panel, label="PDFs")
        self.pdf_cb.SetValue(True)
        self.pdf_cb.SetForegroundColour(wx.Colour(255, 255, 255))
        type_sizer.Add(self.pdf_cb, flag=wx.ALL, border=10)

        main_sizer.Add(type_sizer, flag=wx.ALL | wx.EXPAND, border=15)

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

        self.status_label = wx.StaticText(panel, label="Ready to sort media files")
        self.status_label.SetForegroundColour(wx.Colour(255, 255, 255))
        status_sizer.Add(self.status_label, flag=wx.ALL, border=10)

        self.progress_bar = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        self.progress_bar.SetValue(0)
        status_sizer.Add(self.progress_bar, flag=wx.ALL | wx.EXPAND, border=10)

        main_sizer.Add(status_sizer, flag=wx.ALL | wx.EXPAND, border=15)

        stats_box = wx.StaticBox(panel, label="Statistics")
        stats_box.SetForegroundColour(wx.Colour(255, 255, 255))
        stats_sizer = wx.StaticBoxSizer(stats_box, wx.VERTICAL)
        # First row of stats
        stats_row1 = wx.BoxSizer(wx.HORIZONTAL)

        self.videos_label = wx.StaticText(panel, label="Videos: 0")
        self.videos_label.SetForegroundColour(wx.Colour(255, 255, 255))
        stats_row1.Add(self.videos_label, flag=wx.ALL, border=10)

        stats_row1.AddStretchSpacer()

        self.images_label = wx.StaticText(panel, label="Images: 0")
        self.images_label.SetForegroundColour(wx.Colour(255, 255, 255))
        stats_row1.Add(self.images_label, flag=wx.ALL, border=10)

        stats_row1.AddStretchSpacer()

        self.pdfs_label = wx.StaticText(panel, label="PDFs: 0")
        self.pdfs_label.SetForegroundColour(wx.Colour(255, 255, 255))
        stats_row1.Add(self.pdfs_label, flag=wx.ALL, border=10)

        stats_sizer.Add(stats_row1, flag=wx.EXPAND)

        # Second row of stats
        stats_row2 = wx.BoxSizer(wx.HORIZONTAL)

        self.total_label = wx.StaticText(panel, label="Total Files: 0")
        self.total_label.SetForegroundColour(wx.Colour(255, 255, 255))
        stats_row2.Add(self.total_label, flag=wx.ALL, border=10)

        stats_row2.AddStretchSpacer()

        self.folders_label = wx.StaticText(panel, label="Folders: 0")
        self.folders_label.SetForegroundColour(wx.Colour(255, 255, 255))
        stats_row2.Add(self.folders_label, flag=wx.ALL, border=10)

        stats_sizer.Add(stats_row2, flag=wx.EXPAND)

        main_sizer.Add(stats_sizer, flag=wx.ALL | wx.EXPAND, border=15)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.preview_btn = wx.Button(panel, label="Preview", size=(100, 35))
        self.preview_btn.SetBackgroundColour(wx.Colour(150, 100, 200))
        self.preview_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.preview_btn.Enable(False)
        self.preview_btn.Bind(wx.EVT_BUTTON, self.on_preview)
        button_sizer.Add(self.preview_btn, flag=wx.ALL, border=10)

        button_sizer.AddStretchSpacer()

        self.sort_btn = wx.Button(panel, label="Sort Files", size=(100, 35))
        self.sort_btn.SetBackgroundColour(wx.Colour(100, 180, 100))
        self.sort_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.sort_btn.Enable(False)
        self.sort_btn.Bind(wx.EVT_BUTTON, self.on_sort_files)
        button_sizer.Add(self.sort_btn, flag=wx.ALL, border=10)

        main_sizer.Add(button_sizer, flag=wx.ALL | wx.EXPAND, border=15)

        dll_status = "DLL Loaded" if DLL_LOADED else "DLL Not Found"
        footer = wx.StaticText(panel, label=f"{dll_status} | Media Sorter Pro v3.0")
        footer.SetForegroundColour(wx.Colour(180, 180, 180))
        footer_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        footer.SetFont(footer_font)
        main_sizer.Add(footer, flag=wx.CENTER | wx.ALL, border=15)

        panel.SetSizer(main_sizer)

        self.selected_folder = None
        self.media_files = []
        self.sorting_thread = None

        # File extensions
        self.video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.f4v',
                                 '.m2ts', '.ts'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico',
                                 '.raw', '.heic', '.heif'}
        self.pdf_extensions = {'.pdf'}

        self.Center()

    def get_file_type(self, filename):
        """Determine the file type based on extension"""
        ext = Path(filename).suffix.lower()
        if ext in self.video_extensions:
            return 'video'
        elif ext in self.image_extensions:
            return 'image'
        elif ext in self.pdf_extensions:
            return 'pdf'
        return None

    def on_select_folder(self, event):
        dlg = wx.DirDialog(self, "Choose a folder containing media files")
        if dlg.ShowModal() == wx.ID_OK:
            self.selected_folder = dlg.GetPath()

            display_path = self.selected_folder
            if len(display_path) > 50:
                display_path = "..." + display_path[-47:]

            self.folder_label.SetLabel(display_path)
            self.scan_folder()

            if self.media_files:
                self.auto_sort_files()
        dlg.Destroy()

    def scan_folder(self):
        if not self.selected_folder:
            return

        self.status_label.SetLabel("Scanning folder...")
        self.progress_bar.SetValue(0)

        self.media_files = []
        video_count = 0
        image_count = 0
        pdf_count = 0

        # Get selected file types
        include_videos = self.video_cb.GetValue()
        include_images = self.image_cb.GetValue()
        include_pdfs = self.pdf_cb.GetValue()

        for entry in os.scandir(self.selected_folder):
            if entry.is_file():
                file_type = self.get_file_type(entry.name)

                if file_type == 'video' and include_videos:
                    self.media_files.append(entry)
                    video_count += 1
                elif file_type == 'image' and include_images:
                    self.media_files.append(entry)
                    image_count += 1
                elif file_type == 'pdf' and include_pdfs:
                    self.media_files.append(entry)
                    pdf_count += 1

        # Count unique titles for folder estimation
        titles = set()
        for media_file in self.media_files:
            title = fast_clean_title(media_file.name)
            if title:
                titles.add(title)

        # Update statistics
        self.videos_label.SetLabel(f"Videos: {video_count}")
        self.images_label.SetLabel(f"Images: {image_count}")
        self.pdfs_label.SetLabel(f"PDFs: {pdf_count}")
        self.total_label.SetLabel(f"Total Files: {len(self.media_files)}")
        self.folders_label.SetLabel(f"Folders: {len(titles)}")

        if self.media_files:
            self.status_label.SetLabel(f"Found {len(self.media_files)} media files")
            self.sort_btn.Enable(True)
            self.preview_btn.Enable(True)
        else:
            self.status_label.SetLabel("No media files found")
            self.sort_btn.Enable(False)
            self.preview_btn.Enable(False)

    def auto_sort_files(self):
        confirm_dlg = wx.MessageDialog(
            self,
            f"Sort {len(self.media_files)} media files into folders?",
            "Confirm",
            wx.YES_NO | wx.ICON_QUESTION
        )

        if confirm_dlg.ShowModal() == wx.ID_YES:
            self.start_sorting()
        confirm_dlg.Destroy()

    def on_preview(self, event):
        if not self.media_files:
            return

        preview_dlg = wx.Dialog(self, title="Preview", size=(700, 450))
        preview_dlg.SetBackgroundColour(wx.Colour(40, 40, 40))

        sizer = wx.BoxSizer(wx.VERTICAL)

        preview_text = ""
        for i, media_file in enumerate(self.media_files[:20]):
            title_name = fast_clean_title(media_file.name)
            if not title_name:
                title_name = "Unknown"

            file_type = self.get_file_type(media_file.name)
            type_indicator = f"[{file_type.upper()}]" if file_type else "[UNKNOWN]"

            preview_text += f"{type_indicator} '{media_file.name}' -> '{title_name}'\n"

        if len(self.media_files) > 20:
            preview_text += f"\n... and {len(self.media_files) - 20} more files"

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

    def on_sort_files(self, event):
        if not self.media_files:
            return

        confirm_dlg = wx.MessageDialog(
            self,
            f"Sort {len(self.media_files)} media files into folders?",
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

        self.sorting_thread = threading.Thread(target=self.sort_files_thread)
        self.sorting_thread.start()

    def sort_files_thread(self):
        total_files = len(self.media_files)
        moved_count = 0

        for i, media_file in enumerate(self.media_files):
            progress = int((i / total_files) * 100)
            file_type = self.get_file_type(media_file.name)
            type_indicator = f"[{file_type.upper()}]" if file_type else ""

            wx.CallAfter(self.update_progress, progress, f"Processing {type_indicator}: {media_file.name}")

            title = fast_clean_title(media_file.name)
            if not title:
                title = "Unknown"

            dest_folder = os.path.join(self.selected_folder, title)

            try:
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)

                source_path = media_file.path
                dest_path = os.path.join(dest_folder, media_file.name)

                if os.path.dirname(source_path) != dest_folder:
                    shutil.move(source_path, dest_path)
                    moved_count += 1

            except Exception as e:
                wx.CallAfter(self.show_error, f"Error moving {media_file.name}: {str(e)}")

        wx.CallAfter(self.sorting_complete, moved_count)

    def update_progress(self, value, status):
        self.progress_bar.SetValue(value)
        self.status_label.SetLabel(status)

    def sorting_complete(self, moved_count):
        self.progress_bar.SetValue(100)
        self.status_label.SetLabel(f"Complete! Moved {moved_count} files")

        self.select_btn.Enable(True)
        self.sort_btn.Enable(True)
        self.preview_btn.Enable(True)

        success_dlg = wx.MessageDialog(
            self,
            f"Successfully sorted {moved_count} media files!",
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


class MediaSorterApp(wx.App):
    def OnInit(self):
        frame = MediaSorterFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = MediaSorterApp()
    app.MainLoop()