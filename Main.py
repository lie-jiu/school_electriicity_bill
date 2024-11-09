import wx
import requests
from urllib.parse import quote
import threading
import sys
import os

class ShopInfoFrame(wx.Frame):
    def __init__(self, parent, title):
        super(ShopInfoFrame, self).__init__(parent, title=title, size=(250, 220))
        if getattr(sys, 'frozen', False):
            # 如果程序被打包，则从临时目录加载资源
            application_path = sys._MEIPASS
        else:
            # 如果程序没有被打包，则从当前工作目录加载资源
            application_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(application_path, 'icon.ico')
        # 设置窗口图标
        self.SetIcon(wx.Icon(icon_path, wx.BITMAP_TYPE_ICO))

        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 添加用户输入框和获取信息按钮
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.user_input = wx.TextCtrl(panel, size=(100, -1))
        self.fetch_button = wx.Button(panel, label="查询")
        hbox.Add(self.user_input, proportion=1, flag=wx.RIGHT | wx.EXPAND, border=5)
        hbox.Add(self.fetch_button, proportion=0, flag=wx.LEFT, border=5)
        vbox.Add(hbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        # 初始化标签属性
        self.label_shop_number = wx.StaticText(panel, label="寝室号: ")
        self.label_balance = wx.StaticText(panel, label="剩余电费: ")

        vbox.Add(self.label_shop_number, flag=wx.ALL, border=10)
        vbox.Add(self.label_balance, flag=wx.ALL, border=10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(vbox, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(sizer)
        self.Centre()
        self.Show(True)

        # 绑定按钮事件
        self.fetch_button.Bind(wx.EVT_BUTTON, self.OnFetchInfo)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnFetchInfo(self, event):
        user = self.user_input.GetValue()
        if user:  # 确保用户输入了用户名
            threading.Thread(target=self.fetch_info, args=(user,)).start()
        else:
            wx.MessageBox("请输入用户名", "提示", wx.ICON_INFORMATION)

    def OnClose(self, event):
        self.Destroy()

    def SetShopInfo(self, shop_number, balance):
        self.label_shop_number.SetLabel(f"寝室号:{shop_number}")
        self.label_balance.SetLabel(f"剩余电费:{balance}")

    def fetch_info(self, user):
        url = "http://jxgsxy.acrel-eem.com"
        password = "gs@1998_XY."  # 默认密码

        try:
            session = requests.Session()
            login_url = f"{url}/Ajax/UserLogin.ashx?username={quote(user)}&password={quote(password)}"
            response = session.get(login_url)

            if response.status_code == 200:
                id = session.cookies.get("ASP.NET_SessionId")
                if id:
                    response = session.get(f"{url}/Ajax/CheckUserLogin.ashx?Id=2")
                    if response.status_code == 200:
                        html_content = response.text
                        print(response.text)
                        # 使用字符串操作提取商铺号和剩余金额
                        # 我也不知道为什么html解析用不了
                        start_shop_number = html_content.find("商铺号") + len("商铺号")
                        end_shop_number = html_content.find("</p>", start_shop_number)
                        shop_number = html_content[start_shop_number:end_shop_number].strip()

                        start_balance = html_content.find("剩余金额：") + len("剩余金额：")
                        end_balance = html_content.find("</p>", start_balance)
                        balance = html_content[start_balance:end_balance].strip()

                        wx.CallAfter(self.SetShopInfo, shop_number, balance)
                    else:
                        wx.MessageBox("登录请求失败", "错误", wx.ICON_ERROR)
                else:
                    wx.MessageBox("无法获取信息\n正确寝室格式为：x#-xxx", "错误", wx.ICON_ERROR)
            else:
                wx.MessageBox("登录请求失败", "错误", wx.ICON_ERROR)
        except requests.exceptions.RequestException as e:
            wx.MessageBox(f"网络请求错误: {e}", "错误", wx.ICON_ERROR)

app = wx.App()
frame = ShopInfoFrame(None, title='电费查询')
app.MainLoop()