import wx


class projector_management:
    frame = None
    parent = None
    screen = 0
    def project_pattern(self, show=True):
        if show:
            print("Showing frame")
            try:
                self.frame.Show(False)
                self.frame.Destroy()
            except:
                pass
            try:
                #wx.CallAfter(self.useless)
                self.frame = projector(self.screen, self.parent.pattern[0])
            except:
                pass
        else:
            print ("Closing frame")
            try:
                self.frame.Show(False)
                self.frame.Destroy()
            except:
                return False
        return True

    def change_pattern(self, index):
        try:
            self.frame.changeBackground(self.parent.pattern[index])
            #wx.CallAfter(self.useless2,index)
            #self.useless2(index)
        except:
            return False
        return True

    def set_parent(self, parent):
        self.parent = parent


class projector(wx.Frame):
    def __init__(self, xcord, img_file):
        """Constructor"""
        wx.Frame.__init__(self, None, xcord, img_file)
        self.bmp1 = None
        self.bitmap1 = None
        self.image_file = img_file
        try:
            # pick an image file you have in the working folder
            # you can load .jpg  .png  .bmp  or .gif files
            self.bmp1 = wx.Image(self.image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            # image's upper left corner anchors at panel coordinates (0, 0)
            self.bitmap1 = wx.StaticBitmap(self, -1, self.bmp1, (0, 0))
            # show some image details
            self.SetPosition((xcord, 0))
            self.Maximize(True)
            self.Show()
        except IOError:
            print "Image file %s not found" % self.imageFile
            raise SystemExit

    def changeBackground(self, image):

        self.image_file = image

        self.bmp1 = wx.Image(self.image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # image's upper left corner anchors at panel coordinates (0, 0)
        self.bitmap1 = wx.StaticBitmap(self, -1, self.bmp1, (0, 0))
        self.Layout()
        self.Refresh()
        print "changing background"
